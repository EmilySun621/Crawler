from urllib.parse import urlparse, parse_qs
from collections import Counter
from url_info import *


def is_query_too_long(query, url, DataBase):
    """
    Check if the query string is longer than 100 characters.

    Args:
        query (str): Query part of the URL.
        url (str): Full URL (used for blacklist entry).
        DataBase: Stores blacklist info.

    Returns:
        bool: True if query is too long; otherwise False.
    """
    if len(query) > 100:
        DataBase.blacklistURL[url] = "Queries Longer Than 100"
        return True
    return False

def is_path_too_long(path, url, DataBase):
    """
    Returns True if the path has more than 10 slashes.

    Args:
        path (str): Path part of the URL.
        url (str): Full URL (used for blacklist entry).
        DataBase: Stores blacklist info.

    Returns:
        bool: True if path is too long; otherwise False.
    """
    if path.count('/') > 10:
        DataBase.blacklistURL[url] = "Path Too Long"
        return True
    return False


def contains_trap_keywords(url, DataBase):
    """
    contains_trap_keywords() checks if the URL contains any trap keywords that indicate it might be a crawler      trap."""
    trap_keywords = [

            "sort=", "ref=", "replytocom", "trackback", "events/category"
    ]
    if any(keyword in url.lower() for keyword in trap_keywords):
        DataBase.blacklistURL[url] = "Calendar Trap"
        return True
    return False

def is_url_too_long(url, DataBase, max_len=2000):
    """Attackers or misconfigured sites may generate URLs with endless parameters (e.g. pagination loops), so a length cutoff helps you bail out early."""
    if len(url) > max_len:
        DataBase.blacklistURL[url] = f"URL Too Long ({len(url)} chars)"
        return True
    return False

def has_format_or_lang_trap(query, url, DataBase):
    """By blacklisting any URL with these keys, you avoid crawling duplicate content that only differs by presentation 
    (language, downloadable PDF, print layout, etc.)."""
    trap_keys = {"lang", "language", "locale", "format", "output", "view", "display", "print", "pdf"}
    query_params = parse_qs(query)
    for key in query_params:
        if key.lower() in trap_keys:
            DataBase.blacklistURL[url] = "Language/Format/View Trap"
            return True
    return False

# A
def has_session_id(query, url, DataBase):
    """
        Description:
        Detects if the URL's query string contains any session-related keywords. 
        These keywords typically represent temporary identifiers 
        that change on each visit. Including them in URLs can lead to:
            - Infinite crawling loops (as new sessions create new URLs),
            - Many duplication of pages with identical content,
            - Poor performance.

        If any such keywords are found, 
        the URL is added to the blacklist, "Session/Token Trap"
        and the function returns True.

        Conclusion:
        These types of URLs are relatively common during web crawling.
    """
    session_keywords = ["sessionid", "token", "auth", "jsessionid", "sid"]
    query_keys = parse_qs(query).keys()
    if any(key.lower() in session_keywords for key in query_keys):
        DataBase.blacklistURL[url] = "Session/Token Trap"
        return True
    return False


def has_social_or_fragment_traps(url, DataBase):
    """
        - "?share": related to social sharing features with low value or duplicate content.
        - "redirect": Typically found in URLs that may cause infinite redirection loops (while login).
        - Fragment identifiers: used for navigation anchors,
              but may generate multiple URLs that point to the same content.
        If any such keywords are found, 
        the URL is added to the blacklist with corresponding message
        and the function returns True.

        Conclusion:
        These types of URLs are relatively common during web crawling
    """
    traps = {
        "?share=": "Social Share URL",
        "redirect": "Redirect Trap",
        "#comment": "Fragment Comment Anchor",
        "#respond": "Fragment Respond Anchor",
        "#comments": "Fragment Comments Anchor"
    }
    for pattern, reason in traps.items():
        if pattern in url:
            DataBase.blacklistURL[url] = reason
            return True
    return False

def has_path_repetition_trap(path, url, DataBase, repeat_threshold=5):
    """
        Similar to has_repeated_path_segments.
        The function checks if a URL path has too many repeated path segments.
        Example: "https://example.com/repeat/repeat/repeat/repeat/repeat/item"
        The segment "repeat" appears multiple times, which might indicate a trap.

        These types of URLs are very rare to encounter during crawling,
        but they are problematic because they could be part of an infinite loop 
        or poorly structured URLs that generate unnecessary duplication.
    """
    paths_split = [segment for segment in path.split("/") if segment]
    if paths_split:
        most_common = Counter(paths_split).most_common(1)
        if most_common:
            _, times = most_common[0]
            if times > repeat_threshold:
                DataBase.blacklistURL[url] = "Repetitive Path Segments"
                return True
    return False

#E
def trap_identify(url, DataBase):
     """
    Determines whether a given URL is likely to be a crawler trap.

    A crawler trap is a URL pattern or behavior that can cause the crawler to enter
    infinite loops, excessive crawling depth, or waste resources. This function
    delegates to a set of modular trap detectors, including checks for:
      - excessively long query strings or paths
      - repeated path segments
      - session identifiers
      - social media share links and fragments
      - format/language-related traps
      - trap-like keywords (e.g., "calendar", "print", "sort")

    Args:
        url (str): The full URL to be checked for trap patterns.
        DataBase (object): The global state object used for recording filtered traps
                           and blacklist annotations.

    Returns:
        bool: True if the URL is identified as a trap and should be avoided;
              False if the URL is considered safe for crawling.
    """
    parsed = urlparse(url)
    path = parsed.path
    query = parsed.query

    # Modularized trap checks
    if (
        is_query_too_long(query, url, DataBase) or
        is_path_too_long(path, url, DataBase) or
        contains_trap_keywords(url, DataBase) or
        has_social_or_fragment_traps(url, DataBase) or
        has_path_repetition_trap(path, url, DataBase) or
        is_url_too_long(url, DataBase) or
        has_format_or_lang_trap(query, url, DataBase) or
        has_session_id(query, url, DataBase)
    ):
        return True
    return False
