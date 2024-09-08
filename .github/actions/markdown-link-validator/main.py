"""
This script checks all markdown files in the repository,
it exits with a non-zero status code if it's unable to parse the markdown files
or if it finds any broken links.
"""
import json
import os
from urllib.parse import urlparse

import markdown
import requests
import http
from bs4 import BeautifulSoup


def list_markdown_files(root_directory: str = '.') -> list:
    """
    List all markdown files in the given directory and its subdirectories.
    """
    markdown_files = []
    for root, _, files in os.walk(root_directory):
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(root, file))
    return markdown_files


def generate_markdown_table(broken_links_report: list) -> str:
    """
    Generate a markdown table of broken links.
    """
    if not broken_links_report:
        return ""

    table = "| File | Broken URL |\n"
    table += "|------|------------|\n"
    for file_path, url in broken_links_report:
        table += f"| {file_path} | {url} |\n"
    return table


def write_to_step_summary(content: str):
    """
    Write content to the GitHub Actions step summary.
    """
    summary_file = os.getenv('GITHUB_STEP_SUMMARY')
    if summary_file:
        with open(summary_file, 'a') as f:
            f.write(content)


def post_comment_to_pr(token: str, repo: str, pr_number: int, content: str):
    """
    Post a comment on a pull request.
    documentation reference:
    - https://docs.github.com/en/rest/issues/comments?apiVersion=2022-11-28
    """
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'Accept: application/vnd.github+json'
    }
    data = {
        'body': content
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == http.HTTPStatus.CREATED:
        print("Comment posted successfully.")
    else:
        print(
            f"Failed to post comment: {response.status_code} - {response.text}")


def validate_link(url: str) -> bool:
    """
    Validate if the given URL is reachable. Skip URLs with non-HTTP schemes.
    """
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ('http', 'https'):
        return True
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == http.HTTPStatus.OK
    except requests.RequestException:
        return False


def check_links_in_html(html_content: str, file_path: str) -> list:
    """
    Parse the HTML content, find all links, and check if they are valid.
    Returns a list of broken links with the corresponding file path.
    """
    broken_links = []
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', href=True)

    for link in links:
        url = link['href']
        if not validate_link(url):
            broken_links.append((file_path, url))

    return broken_links


def main():
    broken_links_report = []
    markdown_files = list_markdown_files()

    for file in markdown_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
                # https://python-markdown.github.io/reference/#the-basics
                html_content = markdown.markdown(markdown_content)

            broken_links = check_links_in_html(html_content, file)
            broken_links_report.extend(broken_links)

        except Exception as e:
            print(f"Error processing file {file}: {e}")
            exit(1)

    if broken_links_report:
        print("Broken links found:")
        for file_path, url in broken_links_report:
            print(f"File: {file_path} | Broken URL: {url}")

        markdown_table = generate_markdown_table(broken_links_report)
        write_to_step_summary(f"## Broken Links Report\n{markdown_table}")

        # fully-formed ref of the branch or tag
        github_ref = os.getenv('GITHUB_REF')
        print(f"DEBUG: GITHUB_REF is {github_ref}")
        gh_ref_slc = github_ref.split('/')

        # if the ref is a pull request, the last element is the PR number
        pr_number = gh_ref_slc[-2] if gh_ref_slc[1] == 'pull' else None
        print(f"DEBUG: PR number is {pr_number}")
        if pr_number and pr_number.isdigit():
            repo = os.getenv('GITHUB_REPOSITORY')
            print(f"DEBUG: Repo is {repo}")
            token = os.getenv('PAT_TOKEN')
            if not token:
                token = os.getenv('GITHUB_TOKEN')
            comment_content = "## Markdown link validator action\n" \
                f"### Broken Links Found\n{markdown_table}"
            post_comment_to_pr(token, repo, int(pr_number), comment_content)

        exit(1)
    else:
        print("No broken links found!")

        write_to_step_summary("## Broken Links Report\nNo broken links found!")


if __name__ == "__main__":
    main()
