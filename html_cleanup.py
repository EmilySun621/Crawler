import re
from bs4 import BeautifulSoup, Comment

def clean_html_text(html_content: bytes) -> str:
    """
    Takes raw HTML (bytes) and returns a cleaned, space-delimited string
    for tokenization. Removes comments, scripts, styles, and excess whitespace.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove comments
    for tag in soup(text=lambda text: isinstance(text, Comment)):
        tag.extract()

    # Remove <script> and <style> content
    for element in soup.find_all(['script', 'style']):
        element.extract()

    # Get visible text and normalize spacing
    webtext = soup.get_text()
    space_delimited_text = re.sub(r'\s+', ' ', webtext).strip()

    return space_delimited_text


def filter_extreme_large_small_files(text,resp):
    if len(resp.raw_response.content) > 1_000_000 and len(text) < 500: