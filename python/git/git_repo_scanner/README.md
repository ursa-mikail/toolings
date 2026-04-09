# repo_scanner

A generic, pattern-driven code scanner that clones every repository for a
GitHub user, GitHub/GitLab/Gitea/Bitbucket organisation, or a local directory
and reports every line that matches a configurable set of regex patterns.

Comes with `crypto_patterns.txt` — ready-made patterns for cryptography,
security primitives, post-quantum algorithms, ZKP/MPC, and related libraries.

---

## Quick Start

```bash
pip install requests
```

`git` must be on your `PATH`.

```bash
# Scan a public GitHub user for cryptography usage (no token needed)
python repo_scanner.py \
  --user    ursa-mikail \
  --config  crypto_patterns.txt

# Scan a GitHub org with a token (removes rate limits, includes private repos)
python repo_scanner.py \
  --host    https://github.com \
  --token   ghp_xxxxxxxxxxxx \
  --org     my-org \
  --config  crypto_patterns.txt

# Scan already-cloned repos — no network required
python repo_scanner.py \
  --no-clone \
  --local-path /path/to/clones \
  --config  crypto_patterns.txt
```

The scanner writes a self-contained report folder:

```
scan_report_<timestamp>/
├── summary.html       ← visual dashboard — open in a browser
├── summary.csv        ← one row per repo
├── matches.csv        ← every individual match (flat)
├── matches.json       ← full structured data
└── per_repo/
    └── <repo>.txt     ← detailed match listing per repo
```

---

## All Options

| Flag | Default | Description |
|---|---|---|
| `--config` | `patterns.txt` | Pattern config file |
| `--user` | — | GitHub username (public repos, no token required) |
| `--host` | `https://github.com` | Git server base URL |
| `--token` | — | Personal access token (optional for public GitHub) |
| `--org` | — | Organisation / group / project key |
| `--provider` | `github` | `github` \| `gitlab` \| `gitea` \| `bitbucket` |
| `--report-dir` | auto | Output folder name |
| `--report-title` | auto | Title shown in the HTML dashboard |
| `--workers` | `4` | Parallel clone workers |
| `--branch` | default branch | Branch to check out and scan |
| `--include-forks` | false | Include forked repos |
| `--max-repos` | unlimited | Cap number of repos scanned |
| `--verbose` | false | Print every match line as found |
| `--no-clone` | false | Skip cloning; use `--local-path` |
| `--local-path` | — | Pre-cloned repos directory (use with `--no-clone`) |
| `--jar-scan` | false | Inspect `.jar` files for matching class entries |

Environment variables can substitute CLI flags:

| Variable | Equivalent flag |
|---|---|
| `GIT_HOST` | `--host` |
| `GIT_TOKEN` | `--token` |
| `GIT_ORG` | `--org` |

---

## Pattern File Format

Each active line has three pipe-separated fields:

```
CATEGORY | REGEX | EXTENSIONS
```

| Field | Description |
|---|---|
| `CATEGORY` | Label shown in results (e.g. `symmetric`, `hash_func`) |
| `REGEX` | Python regex, compiled with `re.IGNORECASE` |
| `EXTENSIONS` | Comma-separated `.ext` or exact filenames, or `*` for all |

Lines starting with `#` and blank lines are ignored.

### Examples

```
# Match AES in any file
symmetric    | AES\b                           | *

# Match SHA-256 variants in source files only
hash_func    | SHA-?256\b                      | .py,.js,.ts,.java,.kt,.go

# Match PBKDF2 in any file
kdf          | PBKDF2\b                        | *

# Match Python import of the cryptography library
py_import    | ^\s*from\s+cryptography\b       | .py

# Match cryptography in dependency manifests
dependency   | cryptography\b                  | requirements.txt,Pipfile,pyproject.toml
```

---

## crypto_patterns.txt

The included pattern file covers:

| Category | Examples |
|---|---|
| `py_import` | `cryptography`, `hashlib`, `hmac`, `nacl`, `jose`, `jwt`, `gnupg` |
| `symmetric` | AES, ChaCha20, Salsa20, DES/3DES, Blowfish, Twofish, RC4 |
| `cipher_mode` | GCM, CBC, CCM, CTR, OFB, ECB, SIV, XTS, OCB |
| `asymmetric` | RSA, ECC, ECDH, ECDSA, DH, ElGamal, DSA, X25519, Ed25519 |
| `hash_func` | SHA-256/512/3, MD5, BLAKE2/3, Whirlpool, RIPEMD |
| `kdf` | PBKDF2, scrypt, Argon2, bcrypt, HKDF, HMAC, CMAC |
| `signature` | `.sign()`, `.verify()`, digital signature patterns |
| `key_mgmt` | PEM headers, `generate_key`, `load_pem_*`, `private_bytes` |
| `tls` | SSL/TLS/mTLS, `ssl.create_default_context`, `ssl_context` |
| `fpe_token` | FPE, format-preserving, tokenization, FF1/FF3 |
| `post_quantum` | Kyber, Dilithium, FALCON, SPHINCS+, NTRU, McEliece |
| `zkp` | ZKP, SNARK, STARK, Bulletproofs, MPC, Shamir secret sharing |
| `random` | `os.urandom`, `secrets.*`, `/dev/urandom`, CSPRNG/DRBG |
| `encoding` | base64, hexlify, DER/PEM/PKCS/ASN.1 |
| `openssl` | `openssl enc/dgst/genrsa`, `libssl`, `libcrypto` |
| `secrets_leak` | Hardcoded passwords/keys in config files |
| `dependency` | `cryptography`, `pycryptodome`, `pynacl`, `PyJWT`, `bcrypt` in manifests |

---

## Output Formats

### summary.html
Visual dashboard with stat cards, category badges, per-owner tables, and repo
cards showing match counts broken down by category. Open directly in a browser
— no server needed.

### matches.csv
Flat spreadsheet with one row per match:
`repo, owner, web_url, file, line_number, category, pattern, line`

### summary.csv
One row per repo:
`repo, owner, language, visibility, web_url, match_count, categories, scanned, error`

### matches.json
Full structured output including all repo metadata and every match, suitable
for piping into reporting tools or CI pipelines.

### per_repo/<name>.txt
Human-readable listing for each repo that had at least one match, grouped by
file with line numbers and category labels.

---

## Extending the Patterns

The pattern file is yours to edit — no code changes needed.

```
# Add a custom internal library
custom       | MyInternalCryptoWrapper\b       | *

# Narrow a pattern to a specific file type
hash_func    | sha3_256\b                      | .py

# Comment out noisy patterns that produce false positives
# broad      | key\b                           | *
```

Add as many categories as you like. New category names are automatically
assigned a colour in the HTML dashboard.

---

## Tips

- **Speed** — increase `--workers` for large orgs (8–16 is good on fast networks).
- **Rate limits** — unauthenticated GitHub allows 60 API requests/hour. Pass `--token` for 5,000/hour.
- **Large repos** — files over 5 MB and binary files (images, archives, compiled objects) are skipped automatically.
- **False positives** — comment out or tighten broad patterns; use extension filters to restrict matches to relevant file types.
- **CI integration** — exit code is always `0`; pipe `matches.json` into your own reporting or alerting tool.
- **Private repos** — pass `--token` with appropriate scopes (`repo` for GitHub).
- **JAR inspection** — add `--jar-scan` to list class entries inside `.jar` files; requires `jar` (JDK) or `unzip` on `PATH`.

---

## Provider Examples

```bash
# GitHub Enterprise
python repo_scanner.py \
  --host     https://github.mycompany.com \
  --token    ghp_xxxxxxxxxxxx \
  --org      my-org \
  --provider github \
  --config   crypto_patterns.txt

# GitLab (self-hosted)
python repo_scanner.py \
  --host     https://gitlab.mycompany.com \
  --token    glpat-xxxxxxxxxxxx \
  --org      my-group \
  --provider gitlab \
  --config   crypto_patterns.txt

# Gitea
python repo_scanner.py \
  --host     https://gitea.mycompany.com \
  --token    xxxxxxxxxxxxxxxxxxxxxxxx \
  --org      my-org \
  --provider gitea \
  --config   crypto_patterns.txt

# Bitbucket Data Center / Server
python repo_scanner.py \
  --host     https://bitbucket.mycompany.com \
  --token    <personal-access-token> \
  --org      MY_PROJECT_KEY \
  --provider bitbucket \
  --config   crypto_patterns.txt
```

---

## Differences from voltage_scanner

`repo_scanner.py` is a generalised fork of `voltage_scanner.py` with these changes:

- **`--user` flag** — scan any public GitHub user without a token.
- **Topic-agnostic** — no hardcoded references to Voltage or OpenText; the report title and labels adapt to whatever patterns file is supplied.
- **Dynamic category colours** — colour palette is assigned automatically; adding new categories to the pattern file requires no code changes.
- **GitHub user/org auto-detection** — tries `/users/{name}/repos` first, then `/orgs/{name}/repos`, so individuals and organisations both work without changing flags.
- **Token optional** — public GitHub repos scan without authentication.
