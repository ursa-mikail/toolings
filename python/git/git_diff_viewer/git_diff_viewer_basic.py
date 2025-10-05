import requests
import difflib

def download_file(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def diff_files(content1, content2):
    diff = difflib.unified_diff(
        content1.splitlines(), content2.splitlines(),
        fromfile='file1', tofile='file2', lineterm=''
    )
    return '\n'.join(diff)

def main():
    url1 = "https://raw.githubusercontent.com/ursa-mikail/toolings/main/python/git/git_diff_viewer/files/product_old.py"
    url2 = "https://raw.githubusercontent.com/ursa-mikail/toolings/main/python/git/git_diff_viewer/files/product_new.py"

    content1 = download_file(url1)
    content2 = download_file(url2)

    diff_result = diff_files(content1, content2)
    print(diff_result)

if __name__ == "__main__":
    main()

"""
import requests
import difflib

def download_file(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def diff_files(content1, content2):
    diff = difflib.unified_diff(
        content1.splitlines(), content2.splitlines(),
        fromfile='file1', tofile='file2', lineterm=''
    )
    return '\n'.join(diff)

def main():
    url1 = "https://raw.githubusercontent.com/ursa-mikail/toolings/main/python/git/git_diff_viewer/files/product_old.py"
    url2 = "https://raw.githubusercontent.com/ursa-mikail/toolings/main/python/git/git_diff_viewer/files/product_new.py"

    content1 = download_file(url1)
    content2 = download_file(url2)

    diff_result = diff_files(content1, content2)
    print(diff_result)

if __name__ == "__main__":
    main()

"""