import re
from bs4 import BeautifulSoup, Comment
from urllib.parse import urlparse
import re
from collections import Counter
from url_info import *
from database import DataBase


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


def filter_extreme_large_small_files(url, DataBase, text, resp, lowerbound, upperbound):
    """
    Filters out:
    1. Extremely large files with very little text content
    2. Text content smaller than lowerbound
    3. Text content larger than upperbound

    Returns False if the file should be skipped.
    """
    content_size = len(resp.raw_response.content)
    text_length = len(text)

    # Very large file but low content → suspicious
    if content_size > 1_000_000 and text_length < 500:
        DataBase.blacklistURL[url] = "Large File With Low Content"
        # DataBase.feature_buffer.append(extract_url_features(url,0))
        return False

    # Content too small
    if text_length < lowerbound:
        print(f"[SKIP] Content too long: {text_length} chars (max: {lowerbound})")
        DataBase.blacklistURL[url] = f"Content Too Short"
        # DataBase.feature_buffer.append(extract_url_features(url,0))
        return False

    # Content too large
    if text_length > upperbound:
        print(f"[SKIP] Content too long: {text_length} chars (max: {upperbound})")
        DataBase.blacklistURL[url] = f"Content Too Long"
        # DataBase.feature_buffer.append(extract_url_features(url,0))
        return False

    # If page is more than 20
    path = urlparse(url).path
    pagination_match = re.search(r'/page/(\d+)/', path)
    if pagination_match:
        page_num = int(pagination_match.group(1))
        if page_num > 20:
            DataBase.blacklistURL[url] = f"Page More Than 20"
            # DataBase.feature_buffer.append(extract_url_features(url,0))
            return False
    return True



def is_low_information_path(url, db, depth=3):
    """
    Heuristic to detect template-based or low-information pages
    by repeated shallow URL paths (e.g., /news/article/123, /news/article/124...)
    
    Returns True if the path structure is already visited.
    """
    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").split("/")

    if len(path_parts) < depth:
        path_key = "/".join(path_parts)
    else:
        path_key = "/".join(path_parts[:depth])

    if path_key in db.visited_path:
        print(f"[SKIP] Repeated low-info path structure: {path_key}")
        db.blacklistURL[url] = "Low Information Path"
        # DataBase.feature_buffer.append(extract_url_features(url,0))
        return True

    db.visited_path.add(path_key)
    return False