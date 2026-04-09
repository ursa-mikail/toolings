#!/usr/bin/env python3
"""
repo_scanner.py
───────────────
Scans every public (or private) repository for a GitHub user / org,
or a GitLab / Gitea / Bitbucket group, looking for patterns defined in
a plain-text config file.

Works unauthenticated against public GitHub users (rate-limited to
60 req/hr). Pass --token to lift that limit or to access private repos.

Outputs a report folder:
  scan_report_<timestamp>/
  ├── summary.html          ← visual dashboard
  ├── summary.csv           ← one row per repo
  ├── matches.csv           ← every individual match (flat)
  ├── matches.json          ← full structured data
  └── per_repo/
      └── <repo_name>.txt   ← detailed match listing per repo

Usage examples:
    # Scan a public GitHub user for cryptography patterns
    python repo_scanner.py \\
        --user    ursa-mikail \\
        --config  crypto_patterns.txt

    # Scan a GitHub org with a token (more repos, no rate limits)
    python repo_scanner.py \\
        --host    https://github.com \\
        --token   ghp_xxxxxxxxxxxx \\
        --org     my-org \\
        --config  crypto_patterns.txt

    # GitLab self-hosted
    python repo_scanner.py \\
        --host    https://gitlab.mycompany.com \\
        --token   glpat-xxxxxxxxxxxx \\
        --org     my-group \\
        --provider gitlab \\
        --config  my_patterns.txt

    # Scan already-cloned repos (no network needed)
    python repo_scanner.py \\
        --no-clone \\
        --local-path /path/to/clones \\
        --config crypto_patterns.txt

Options:
    --config        Pattern config file          (default: patterns.txt)
    --user          Public GitHub username       (no token needed)
    --host          Git server base URL          (default: https://github.com)
    --token         Personal access token        (optional for public GitHub)
    --org           Organisation / group / owner (required unless --user is set)
    --provider      github | gitlab | gitea | bitbucket  (default: github)
    --report-dir    Output report folder         (default: scan_report_<timestamp>)
    --report-title  Title shown in HTML report   (default: auto)
    --workers       Parallel clone workers       (default: 4)
    --branch        Branch to scan               (default: default branch)
    --include-forks Include forked repos
    --max-repos     Limit number of repos scanned
    --verbose       Print every match as found
    --no-clone      Skip cloning; scan local repos via --local-path
    --local-path    Path to already-cloned repos
    --jar-scan      Also inspect .jar files
"""

import argparse
import csv
import fnmatch
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import requests

# ─── Logging ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s  %(levelname)-8s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)
log = logging.getLogger("repo_scanner")

# ─── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class Pattern:
    category: str
    regex: re.Pattern
    raw: str
    extensions: list


@dataclass
class Match:
    repo: str
    file: str
    line_number: int
    line: str
    category: str
    pattern: str


@dataclass
class RepoMeta:
    name: str
    full_name: str      = ""
    owner: str          = ""
    owner_type: str     = ""
    description: str    = ""
    default_branch: str = "main"
    language: str       = ""
    visibility: str     = ""
    topics: list        = field(default_factory=list)
    web_url: str        = ""
    clone_url: str      = ""
    is_fork: bool       = False
    namespace: str      = ""
    maintainers: list   = field(default_factory=list)


@dataclass
class RepoResult:
    meta: RepoMeta
    scanned: bool       = False
    error: Optional[str] = None
    matches: list       = field(default_factory=list)

    @property
    def repo(self):
        return self.meta.name


# ─── Pattern Loader ───────────────────────────────────────────────────────────

def load_patterns(path: str) -> list:
    patterns = []
    p = Path(path)
    if not p.exists():
        log.error("Patterns file not found: %s", path)
        sys.exit(1)
    for lineno, raw in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [x.strip() for x in line.split("|")]
        if len(parts) != 3:
            log.warning("Line %d: expected 3 pipe-separated fields – skipping", lineno)
            continue
        category, raw_pattern, ext_str = parts
        extensions = [] if ext_str == "*" else [
            e.strip().lstrip(".").lower() for e in ext_str.split(",") if e.strip()
        ]
        try:
            compiled = re.compile(raw_pattern, re.IGNORECASE)
        except re.error as exc:
            log.warning("Line %d: bad regex %r – %s – skipping", lineno, raw_pattern, exc)
            continue
        patterns.append(Pattern(
            category=category.strip(),
            regex=compiled,
            raw=raw_pattern,
            extensions=extensions,
        ))
    log.info("Loaded %d patterns from %s", len(patterns), path)
    return patterns


# ─── Extension Matching ───────────────────────────────────────────────────────

def extension_matches(filepath: str, extensions: list) -> bool:
    """Return True if extensions is empty (wildcard) or the file suffix matches."""
    if not extensions:
        return True
    name   = Path(filepath).name.lower()
    suffix = Path(filepath).suffix.lstrip(".").lower()
    return any(ext == suffix or fnmatch.fnmatch(name, ext) for ext in extensions)


# ─── File Scanner ─────────────────────────────────────────────────────────────

BINARY_EXT = {
    "png","jpg","jpeg","gif","ico","bmp","tiff","pdf","zip","tar","gz",
    "bz2","xz","7z","rar","mp3","mp4","avi","mov","mkv","wav","exe","dll","so",
    "dylib","class","pyc","pyo","pyd","woff","woff2","ttf","otf","eot","lock",
    "bin","dat","db","sqlite","sqlite3",
}
MAX_FILE_BYTES = 5 * 1024 * 1024   # 5 MB


def scan_file(filepath: Path, patterns: list, repo_name: str) -> list:
    if filepath.suffix.lstrip(".").lower() in BINARY_EXT:
        return []
    try:
        if filepath.stat().st_size > MAX_FILE_BYTES:
            return []
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    rel   = str(filepath)
    appls = [p for p in patterns if extension_matches(rel, p.extensions)]
    if not appls:
        return []

    matches = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for pat in appls:
            if pat.regex.search(line):
                matches.append(Match(
                    repo=repo_name,
                    file=rel,
                    line_number=lineno,
                    line=line.strip()[:300],
                    category=pat.category,
                    pattern=pat.raw,
                ))
    return matches


def scan_jars(repo_dir: Path, repo_name: str) -> list:
    matches = []
    tool = shutil.which("jar") or shutil.which("unzip")
    if not tool:
        return matches
    for jar in repo_dir.rglob("*.jar"):
        try:
            cmd    = ["jar", "tf", str(jar)] if shutil.which("jar") else ["unzip", "-l", str(jar)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            for n, line in enumerate(result.stdout.splitlines(), 1):
                matches.append(Match(
                    repo=repo_name,
                    file=str(jar.relative_to(repo_dir)),
                    line_number=n,
                    line=line.strip(),
                    category="jar_class",
                    pattern="(jar entry)",
                ))
        except Exception:
            pass
    return matches


# ─── Git Providers ────────────────────────────────────────────────────────────

class GitProvider:
    def __init__(self, host, token, org):
        self.host    = host.rstrip("/")
        self.token   = token
        self.org     = org
        self.session = requests.Session()
        hdrs = self._auth_headers()
        if hdrs:
            self.session.headers.update(hdrs)

    def _auth_headers(self): return {}
    def list_repos(self, include_forks=False): raise NotImplementedError

    def _paginate(self, url, params=None):
        results, params = [], dict(params or {})
        while url:
            r = self.session.get(url, params=params, timeout=30)
            r.raise_for_status()
            data  = r.json()

            # GitHub repos endpoints return a bare JSON array; others use objects.
            if isinstance(data, list):
                items = data
            else:
                items = data.get("items") or data.get("values") or []

            results.extend(items)
            params   = {}
            next_url = None
            for part in r.headers.get("Link", "").split(","):
                if 'rel="next"' in part:
                    next_url = part.split(";")[0].strip().strip("<>")
            url = next_url
        return results


class GitHubProvider(GitProvider):
    """Works against github.com or GitHub Enterprise."""

    def _auth_headers(self):
        hdrs = {"Accept": "application/vnd.github+json"}
        if self.token:
            hdrs["Authorization"] = f"token {self.token}"
        return hdrs

    def _api(self):
        if self.host in ("https://github.com", "http://github.com"):
            return "https://api.github.com"
        return f"{self.host}/api/v3"

    def list_repos(self, include_forks=False):
        # Try /users/{org}/repos first (works for individuals), fall back to /orgs/
        for endpoint in (
            f"{self._api()}/users/{self.org}/repos",
            f"{self._api()}/orgs/{self.org}/repos",
        ):
            try:
                raw = self._paginate(endpoint, {"per_page": 100, "type": "all"})
                break
            except requests.HTTPError as e:
                if e.response is not None and e.response.status_code == 404:
                    continue
                raise
        else:
            log.error("Could not find user or org %r on %s", self.org, self.host)
            sys.exit(1)

        out = []
        for r in raw:
            if not include_forks and r.get("fork"):
                continue
            owner = r.get("owner", {})
            out.append(RepoMeta(
                name           = r["name"],
                full_name      = r.get("full_name", ""),
                owner          = owner.get("login", self.org),
                owner_type     = owner.get("type", ""),
                description    = r.get("description") or "",
                default_branch = r.get("default_branch", "main"),
                language       = r.get("language") or "",
                visibility     = r.get("visibility", ""),
                topics         = r.get("topics", []),
                web_url        = r.get("html_url", ""),
                clone_url      = r.get("clone_url", ""),
                is_fork        = r.get("fork", False),
            ))
        return out


class GitLabProvider(GitProvider):
    def _auth_headers(self):
        return {"PRIVATE-TOKEN": self.token} if self.token else {}

    def list_repos(self, include_forks=False):
        enc = requests.utils.quote(self.org, safe="")
        raw = self._paginate(
            f"{self.host}/api/v4/groups/{enc}/projects",
            {"per_page": 100, "include_subgroups": "true", "with_shared": "false"},
        )
        out = []
        for r in raw:
            if not include_forks and r.get("forked_from_project"):
                continue
            ns = r.get("namespace", {})
            out.append(RepoMeta(
                name           = r["path"],
                full_name      = r.get("path_with_namespace", ""),
                owner          = ns.get("full_path", self.org),
                owner_type     = ns.get("kind", ""),
                description    = r.get("description") or "",
                default_branch = r.get("default_branch", "main"),
                visibility     = r.get("visibility", ""),
                topics         = r.get("topics", []),
                web_url        = r.get("web_url", ""),
                clone_url      = r.get("http_url_to_repo", ""),
                is_fork        = bool(r.get("forked_from_project")),
                namespace      = ns.get("full_path", ""),
            ))
        return out


class GiteaProvider(GitProvider):
    def _auth_headers(self):
        return {"Authorization": f"token {self.token}"} if self.token else {}

    def list_repos(self, include_forks=False):
        raw = self._paginate(f"{self.host}/api/v1/orgs/{self.org}/repos", {"limit": 50})
        out = []
        for r in raw:
            if not include_forks and r.get("fork"):
                continue
            owner = r.get("owner", {})
            out.append(RepoMeta(
                name        = r["name"],
                full_name   = r.get("full_name", ""),
                owner       = owner.get("login", self.org),
                owner_type  = owner.get("type", ""),
                description = r.get("description") or "",
                visibility  = "private" if r.get("private") else "public",
                web_url     = r.get("html_url", ""),
                clone_url   = r.get("clone_url", ""),
                is_fork     = r.get("fork", False),
            ))
        return out


class BitbucketProvider(GitProvider):
    def list_repos(self, include_forks=False):
        url    = f"{self.host}/rest/api/1.0/projects/{self.org}/repos"
        params = {"limit": 100, "start": 0}
        out    = []
        while True:
            resp = self.session.get(url, params=params,
                                    auth=(self.org, self.token), timeout=30)
            resp.raise_for_status()
            data = resp.json()
            for r in data.get("values", []):
                clone_url = next(
                    (l["href"] for l in r.get("links", {}).get("clone", [])
                     if l.get("name") == "http"), ""
                )
                web_url = next(
                    (l["href"] for l in r.get("links", {}).get("self", [])), ""
                )
                out.append(RepoMeta(
                    name      = r["slug"],
                    full_name = f"{self.org}/{r['slug']}",
                    owner     = self.org,
                    web_url   = web_url,
                    clone_url = clone_url,
                ))
            if data.get("isLastPage"):
                break
            params["start"] = data.get("nextPageStart", params["start"] + 100)
        return out


PROVIDERS = {
    "github":    GitHubProvider,
    "gitlab":    GitLabProvider,
    "gitea":     GiteaProvider,
    "bitbucket": BitbucketProvider,
}


# ─── Clone & Scan ─────────────────────────────────────────────────────────────

_print_lock = threading.Lock()


def clone_and_scan(meta, patterns, branch, jar_scan, verbose, token):
    result    = RepoResult(meta=meta)
    tmpdir    = tempfile.mkdtemp(prefix=f"scan_{meta.name}_")
    clone_url = meta.clone_url

    # Inject token into HTTPS clone URL
    if token and "://" in clone_url:
        scheme, rest = clone_url.split("://", 1)
        if "@" in rest:
            rest = rest.split("@", 1)[1]
        clone_url = f"{scheme}://oauth2:{token}@{rest}"

    try:
        cmd = ["git", "clone", "--depth", "1", "--quiet"]
        if branch:
            cmd += ["--branch", branch]
        cmd += [clone_url, tmpdir]
        subprocess.run(cmd, capture_output=True, timeout=300, check=True)

        repo_dir = Path(tmpdir)
        all_files = list(repo_dir.rglob("*"))
        for fp in all_files:
            if not fp.is_file():
                continue
            rel_path = fp.relative_to(repo_dir)
            rel_str  = str(rel_path)
            # Skip .git internals
            if rel_str.startswith(".git") or "/.git/" in rel_str:
                continue
            hits = scan_file(fp, patterns, meta.name)
            if hits:
                # Make the file path relative and clean
                for h in hits:
                    h.file = rel_str
                result.matches.extend(hits)
                if verbose:
                    with _print_lock:
                        for h in hits:
                            log.info("  MATCH  %s:%d  [%s]  %s",
                                     h.file, h.line_number, h.category, h.line[:120])

        if jar_scan:
            result.matches.extend(scan_jars(repo_dir, meta.name))

        result.scanned = True
    except subprocess.CalledProcessError as exc:
        result.error = f"git clone failed: {exc.stderr.decode(errors='replace').strip()}"
    except subprocess.TimeoutExpired:
        result.error = "git clone timed out"
    except Exception as exc:
        result.error = str(exc)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    with _print_lock:
        if result.error:
            log.warning("✗  %-50s  %s", meta.name, result.error)
        else:
            log.info("✓  %-50s  %4d match(es)", meta.name, len(result.matches))
    return result


def scan_local(local_path, patterns, jar_scan, verbose):
    base    = Path(local_path)
    results = []
    for repo_dir in sorted(base.iterdir()):
        if not repo_dir.is_dir():
            continue
        meta   = RepoMeta(name=repo_dir.name, full_name=str(repo_dir),
                          web_url=f"file://{repo_dir}")
        result = RepoResult(meta=meta, scanned=True)
        for fp in repo_dir.rglob("*"):
            if not fp.is_file():
                continue
            rel_str = str(fp.relative_to(repo_dir))
            if rel_str.startswith(".git") or "/.git/" in rel_str:
                continue
            hits = scan_file(fp, patterns, meta.name)
            if hits:
                for h in hits:
                    h.file = rel_str
                result.matches.extend(hits)
                if verbose:
                    with _print_lock:
                        for h in hits:
                            log.info("  MATCH  %s:%d  [%s]  %s",
                                     h.file, h.line_number, h.category, h.line[:120])
        if jar_scan:
            result.matches.extend(scan_jars(repo_dir, meta.name))
        with _print_lock:
            log.info("✓  %-50s  %4d match(es)", meta.name, len(result.matches))
        results.append(result)
    return results


# ─── HTML helpers ─────────────────────────────────────────────────────────────

def _esc(s):
    return (str(s)
            .replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# A palette of colours for dynamic category assignment
_PALETTE = [
    "#6366f1","#f59e0b","#ef4444","#10b981","#3b82f6",
    "#8b5cf6","#ec4899","#64748b","#14b8a6","#f97316",
    "#06b6d4","#84cc16","#a855f7","#e11d48","#0ea5e9",
]


def _col(cat, _cache={}):
    if cat not in _cache:
        _cache[cat] = _PALETTE[len(_cache) % len(_PALETTE)]
    return _cache[cat]


# ─── Report Writers ───────────────────────────────────────────────────────────

def write_report_folder(results, report_dir: Path, scan_meta: dict):
    report_dir.mkdir(parents=True, exist_ok=True)
    per_repo_dir = report_dir / "per_repo"
    per_repo_dir.mkdir(exist_ok=True)

    all_matches = [m for r in results for m in r.matches]
    hit_results = [r for r in results if r.matches]

    # ── matches.json ─────────────────────────────────────────────────────────
    (report_dir / "matches.json").write_text(
        json.dumps({
            **scan_meta,
            "total_repos":        len(results),
            "repos_with_matches": len(hit_results),
            "total_matches":      len(all_matches),
            "results": [{
                "repo":        r.meta.name,
                "full_name":   r.meta.full_name,
                "owner":       r.meta.owner,
                "owner_type":  r.meta.owner_type,
                "maintainers": r.meta.maintainers,
                "web_url":     r.meta.web_url,
                "language":    r.meta.language,
                "description": r.meta.description,
                "visibility":  r.meta.visibility,
                "is_fork":     r.meta.is_fork,
                "scanned":     r.scanned,
                "error":       r.error,
                "match_count": len(r.matches),
                "matches":     [asdict(m) for m in r.matches],
            } for r in results],
        }, indent=2),
        encoding="utf-8",
    )

    # ── matches.csv ──────────────────────────────────────────────────────────
    with open(report_dir / "matches.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["repo", "owner", "web_url", "file",
                    "line_number", "category", "pattern", "line"])
        for r in results:
            for m in r.matches:
                w.writerow([m.repo, r.meta.owner, r.meta.web_url,
                            m.file, m.line_number, m.category, m.pattern, m.line])

    # ── summary.csv ──────────────────────────────────────────────────────────
    with open(report_dir / "summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["repo", "owner", "language", "visibility",
                    "web_url", "match_count", "categories", "scanned", "error"])
        for r in results:
            cats = ", ".join(sorted({m.category for m in r.matches}))
            w.writerow([r.meta.name, r.meta.owner, r.meta.language,
                        r.meta.visibility, r.meta.web_url,
                        len(r.matches), cats, r.scanned, r.error or ""])

    # ── per_repo/<n>.txt ─────────────────────────────────────────────────────
    for r in hit_results:
        lines = [
            "=" * 80,
            f"  REPO       : {r.meta.name}",
            f"  FULL NAME  : {r.meta.full_name}",
            f"  OWNER      : {r.meta.owner}  ({r.meta.owner_type})",
            f"  LANGUAGE   : {r.meta.language or '—'}",
            f"  VISIBILITY : {r.meta.visibility}",
            f"  URL        : {r.meta.web_url}",
            f"  MATCHES    : {len(r.matches)}",
            "=" * 80, "",
        ]
        by_file = defaultdict(list)
        for m in r.matches:
            by_file[m.file].append(m)
        for fp, fm in sorted(by_file.items()):
            lines.append(f"  ▸ {fp}")
            for m in fm:
                lines.append(f"      line {m.line_number:>5}  [{m.category}]  {m.line}")
            lines.append("")
        safe = re.sub(r"[^\w\-.]", "_", r.meta.name)
        (per_repo_dir / f"{safe}.txt").write_text("\n".join(lines), encoding="utf-8")

    # ── summary.html ─────────────────────────────────────────────────────────
    _write_html(results, report_dir, scan_meta, all_matches, hit_results)

    log.info("")
    log.info("📂 Report written to: %s/", report_dir)
    log.info("   ├── summary.html   ← open this in a browser")
    log.info("   ├── summary.csv")
    log.info("   ├── matches.csv")
    log.info("   ├── matches.json")
    log.info("   └── per_repo/  (%d files)", len(hit_results))


def _write_html(results, report_dir, scan_meta, all_matches, hit_results):
    ts         = scan_meta.get("scan_timestamp", "")
    target     = scan_meta.get("target", "")
    title      = scan_meta.get("report_title", "Code Pattern Scan")
    cat_counts = Counter(m.category for m in all_matches)
    owner_hits = defaultdict(list)
    for r in hit_results:
        owner_hits[r.meta.owner].append(r.meta.name)

    sorted_hits = sorted(hit_results, key=lambda r: -len(r.matches))

    cat_rows = "".join(
        f'<div class="cat-badge" style="--c:{_esc(_col(cat))}">'
        f'<span class="cn">{_esc(cat)}</span>'
        f'<span class="cc">{count}</span></div>'
        for cat, count in cat_counts.most_common()
    )

    owner_rows = "".join(
        f"<tr><td class='ow'>{_esc(o)}</td><td>{len(rs)}</td>"
        f"<td class='rl'>{_esc(', '.join(rs))}</td></tr>"
        for o, rs in sorted(owner_hits.items(), key=lambda x: -len(x[1]))
    )

    cards = ""
    for r in sorted_hits:
        by_cat = Counter(m.category for m in r.matches)
        pills  = "".join(
            f'<span class="pill" style="background:{_esc(_col(c))}">{_esc(c)} {n}</span>'
            for c, n in by_cat.most_common()
        )
        url  = _esc(r.meta.web_url)
        safe = re.sub(r"[^\w\-.]", "_", r.meta.name)
        det  = f"per_repo/{_esc(safe)}.txt"
        lang = f"<span class='lang'>{_esc(r.meta.language)}</span>" if r.meta.language else ""
        vis  = f"<span class='vis'>{_esc(r.meta.visibility)}</span>" if r.meta.visibility else ""
        desc = f'<div class="desc">{_esc(r.meta.description)}</div>' if r.meta.description else ""
        cards += f"""
        <div class="card">
          <div class="card-top">
            <div><a class="rname" href="{url}" target="_blank">{_esc(r.meta.name)}</a>
              <span class="rmeta">{lang}{vis}</span></div>
            <span class="mbadge">{len(r.matches)}</span>
          </div>
          <div class="owner-line">👤 <strong>{_esc(r.meta.owner)}</strong></div>
          {desc}
          <div class="pills">{pills}</div>
          <a class="dlink" href="{det}">View full match listing →</a>
        </div>"""

    errored    = [r for r in results if r.error]
    err_rows   = "".join(
        f"<tr><td>{_esc(r.meta.name)}</td><td>{_esc(r.error or '')}</td></tr>"
        for r in errored
    )
    err_section = (
        f'<section><h2>⚠️ Scan Errors ({len(errored)})</h2>'
        f'<table><thead><tr><th>Repo</th><th>Error</th></tr></thead>'
        f'<tbody>{err_rows}</tbody></table></section>'
    ) if errored else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{_esc(title)} — {_esc(target)}</title>
<style>
:root{{
  --bg:#0d1117;--surf:#161b22;--surf2:#21262d;--bdr:#30363d;
  --tx:#e6edf3;--mu:#8b949e;--acc:#58a6ff;--grn:#3fb950;--red:#f85149;
  --rad:8px;--font:'Segoe UI',system-ui,sans-serif;
}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--tx);font-family:var(--font);font-size:14px;
      line-height:1.6;padding:2.5rem 3rem}}
h1{{font-size:1.7rem;font-weight:800;color:var(--acc);margin-bottom:.2rem}}
h2{{font-size:1rem;font-weight:700;color:var(--tx);margin:2.5rem 0 1rem;
    border-left:3px solid var(--acc);padding-left:.75rem;letter-spacing:.02em}}
.sub{{color:var(--mu);font-size:.82rem;margin-bottom:2rem}}
.stats{{display:flex;gap:.85rem;flex-wrap:wrap;margin-bottom:2.5rem}}
.stat{{background:var(--surf);border:1px solid var(--bdr);border-radius:var(--rad);
       padding:.9rem 1.4rem;flex:1;min-width:130px}}
.sv{{font-size:2rem;font-weight:900;color:var(--acc)}}
.sl{{color:var(--mu);font-size:.75rem;margin-top:.1rem;text-transform:uppercase;letter-spacing:.07em}}
.cats{{display:flex;flex-wrap:wrap;gap:.5rem;margin-bottom:2.5rem}}
.cat-badge{{background:color-mix(in srgb,var(--c) 12%,var(--surf));
            border:1px solid color-mix(in srgb,var(--c) 50%,transparent);
            border-radius:20px;padding:.28rem .85rem;display:flex;align-items:center;gap:.45rem}}
.cn{{font-weight:600;color:var(--c);font-size:.8rem}}
.cc{{background:var(--c);color:#000;border-radius:20px;padding:0 .45rem;
     font-weight:800;font-size:.75rem}}
table{{width:100%;border-collapse:collapse;background:var(--surf);
       border-radius:var(--rad);overflow:hidden;border:1px solid var(--bdr);margin-bottom:2rem}}
thead{{background:var(--surf2)}}
th{{text-align:left;padding:.65rem 1rem;color:var(--mu);font-size:.75rem;
    text-transform:uppercase;letter-spacing:.06em}}
td{{padding:.6rem 1rem;border-top:1px solid var(--bdr);vertical-align:top}}
.ow{{font-weight:700;color:var(--acc)}}
.rl{{color:var(--mu);font-size:.8rem}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:.85rem}}
.card{{background:var(--surf);border:1px solid var(--bdr);border-radius:var(--rad);
       padding:1.1rem;transition:border-color .15s}}
.card:hover{{border-color:var(--acc)}}
.card-top{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.4rem}}
.rname{{font-size:.95rem;font-weight:700;color:var(--acc);text-decoration:none}}
.rname:hover{{text-decoration:underline}}
.rmeta{{margin-left:.4rem}}
.lang,.vis{{font-size:.7rem;color:var(--mu);background:var(--surf2);
            border:1px solid var(--bdr);border-radius:4px;padding:.1rem .4rem;margin-left:.25rem}}
.mbadge{{background:var(--acc);color:#000;font-weight:900;border-radius:20px;
         padding:.1rem .7rem;font-size:.82rem;white-space:nowrap}}
.owner-line{{font-size:.8rem;color:var(--mu);margin-bottom:.35rem}}
.desc{{font-size:.8rem;color:var(--mu);font-style:italic;margin-bottom:.4rem}}
.pills{{display:flex;flex-wrap:wrap;gap:.3rem;margin-top:.45rem}}
.pill{{font-size:.7rem;font-weight:700;color:#fff;border-radius:20px;padding:.12rem .55rem}}
.dlink{{display:inline-block;margin-top:.7rem;font-size:.78rem;color:var(--acc);text-decoration:none}}
.dlink:hover{{text-decoration:underline}}
section{{margin-bottom:2rem}}
footer{{color:var(--mu);font-size:.75rem;margin-top:3rem;padding-top:1rem;
        border-top:1px solid var(--bdr)}}
</style>
</head>
<body>
<h1>🔍 {_esc(title)}</h1>
<p class="sub">Target: <strong>{_esc(target)}</strong>&nbsp;·&nbsp;Scanned: {_esc(ts)}</p>

<div class="stats">
  <div class="stat"><div class="sv">{len(results)}</div><div class="sl">Repos Scanned</div></div>
  <div class="stat"><div class="sv" style="color:var(--{'grn' if hit_results else 'mu'})">{len(hit_results)}</div><div class="sl">With Matches</div></div>
  <div class="stat"><div class="sv">{len(all_matches)}</div><div class="sl">Total Matches</div></div>
  <div class="stat"><div class="sv">{len(cat_counts)}</div><div class="sl">Categories Hit</div></div>
</div>

<section>
  <h2>📊 Matches by Category</h2>
  <div class="cats">{cat_rows}</div>
</section>

<section>
  <h2>👥 Owners with Matching Repos</h2>
  <table>
    <thead><tr><th>Owner</th><th>Repos</th><th>Repository Names</th></tr></thead>
    <tbody>{owner_rows}</tbody>
  </table>
</section>

<section>
  <h2>📁 Matching Repositories ({len(hit_results)})</h2>
  <div class="cards">{cards}</div>
</section>

{err_section}

<footer>Generated by repo_scanner.py · {_esc(ts)}</footer>
</body>
</html>"""
    (report_dir / "summary.html").write_text(html, encoding="utf-8")


# ─── Terminal Summary ─────────────────────────────────────────────────────────

def print_summary(results, report_dir):
    hit   = [r for r in results if r.matches]
    all_m = [m for r in results for m in r.matches]

    print("\n" + "═" * 65)
    print("  SCAN SUMMARY")
    print("═" * 65)
    print(f"  Repos scanned        : {len(results)}")
    print(f"  Repos with matches   : {len(hit)}")
    print(f"  Total matches        : {len(all_m)}")
    print(f"  Errors               : {sum(1 for r in results if r.error)}")

    if all_m:
        print("\n  Matches by category:")
        for cat, n in Counter(m.category for m in all_m).most_common():
            print(f"    {cat:<30s}  {n}")

    if hit:
        print("\n  Repos by match count:")
        for r in sorted(hit, key=lambda r: -len(r.matches)):
            print(f"    {r.meta.name:<45s} {len(r.matches):>4} hits")

    print("═" * 65)
    print(f"\n  📂 Full report → {report_dir}/summary.html\n")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(
        description="Generic code pattern scanner for GitHub / GitLab / Gitea / Bitbucket.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--config",        default="patterns.txt",
                   help="Pattern config file (default: patterns.txt)")
    p.add_argument("--user",          default=None,
                   help="GitHub username to scan (public repos, no token needed)")
    p.add_argument("--host",          default=os.getenv("GIT_HOST", "https://github.com"),
                   help="Git server base URL (default: https://github.com)")
    p.add_argument("--token",         default=os.getenv("GIT_TOKEN"),
                   help="Personal access token (optional for public GitHub)")
    p.add_argument("--org",           default=os.getenv("GIT_ORG"),
                   help="Organisation / group / project key")
    p.add_argument("--provider",      default="github", choices=list(PROVIDERS),
                   help="Git provider (default: github)")
    p.add_argument("--report-dir",    default=None,
                   help="Output directory for report (default: scan_report_<timestamp>)")
    p.add_argument("--report-title",  default=None,
                   help="Title shown in the HTML report")
    p.add_argument("--workers",       type=int, default=4,
                   help="Parallel clone workers (default: 4)")
    p.add_argument("--branch",        default=None,
                   help="Branch to scan (default: repo default)")
    p.add_argument("--include-forks", action="store_true",
                   help="Include forked repos")
    p.add_argument("--max-repos",     type=int, default=None,
                   help="Cap number of repos scanned")
    p.add_argument("--verbose",       action="store_true",
                   help="Print every match line as found")
    p.add_argument("--no-clone",      action="store_true",
                   help="Skip cloning; use --local-path instead")
    p.add_argument("--local-path",    default=None,
                   help="Directory of pre-cloned repos (used with --no-clone)")
    p.add_argument("--jar-scan",      action="store_true",
                   help="Inspect .jar files for matching class entries")
    return p.parse_args()


def main():
    args = parse_args()

    # --user is shorthand for --org on github.com
    if args.user:
        args.org      = args.user
        args.host     = "https://github.com"
        args.provider = "github"

    patterns = load_patterns(args.config)
    if not patterns:
        log.error("No valid patterns loaded. Aborting.")
        sys.exit(1)

    ts          = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_dir  = Path(args.report_dir) if args.report_dir else Path(f"scan_report_{ts}")
    report_title = args.report_title or f"Code Pattern Scan — {args.org or args.local_path}"
    results     = []

    if args.no_clone:
        if not args.local_path:
            log.error("--no-clone requires --local-path")
            sys.exit(1)
        log.info("Scanning local path: %s", args.local_path)
        results = scan_local(args.local_path, patterns, args.jar_scan, args.verbose)
        target  = args.local_path
    else:
        org = args.org
        if not org:
            log.error("--org (or --user) is required unless --no-clone is set")
            sys.exit(1)
        provider = PROVIDERS[args.provider](args.host, args.token, org)
        target   = f"{args.host} / {org}"
        log.info("Fetching repository list from %s …", target)
        try:
            repos = provider.list_repos(include_forks=args.include_forks)
        except Exception as exc:
            log.error("Failed to list repos: %s", exc)
            sys.exit(1)
        if args.max_repos:
            repos = repos[:args.max_repos]
        log.info("Found %d repos — scanning with %d workers …", len(repos), args.workers)
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {
                pool.submit(
                    clone_and_scan, meta, patterns,
                    args.branch, args.jar_scan, args.verbose, args.token
                ): meta
                for meta in repos
            }
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as exc:
                    meta = futures[future]
                    log.error("Unhandled error for %s: %s", meta.name, exc)

    scan_meta = {
        "scan_timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "target":         target,
        "report_title":   report_title,
        "config":         args.config,
    }
    write_report_folder(results, report_dir, scan_meta)
    print_summary(results, report_dir)


if __name__ == "__main__":
    main()
