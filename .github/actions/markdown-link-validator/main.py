"""
This script checks all markdown files in the repository,
it exits with a non-zero status code if it's unable to parse the markdown files
or if it finds any broken links.
"""
import os
from urllib.parse import urlparse

import markdown
import requests
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


def validate_link(url: str) -> bool:
    """
    Validate if the given URL is reachable. Skip URLs with non-HTTP schemes.
    """
    parsed_url = urlparse(url)
    if parsed_url.scheme not in ('http', 'https'):
        return True
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code == 200
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
        exit(1)
    else:
        print("No broken links found!")

        write_to_step_summary("## Broken Links Report\nNo broken links found!")


if __name__ == "__main__":
    main()
