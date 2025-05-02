from urllib.parse import urlparse, parse_qs
from collections import Counter
from url_info import *

# E
def is_query_too_long(query, url, DataBase):
    if len(query) > 100:
        DataBase.blacklistURL[url] = "Queries Longer Than 100"
        return True
    return False

def is_path_too_long(path, url, DataBase):
    if path.count('/') > 10:
        DataBase.blacklistURL[url] = "Path Too Long"
        return True
    return False

def has_repeated_path_segments(path, url, DataBase):
    segments = path.split('/')
    if len(segments) != len(set(segments)):
        DataBase.blacklistURL[url] = "Repeated Segments"
        return True
    return False

# C
def contains_trap_keywords(url, DataBase):
    trap_keywords = [
        "calendar", "date", "year", "month", "day",
        "sort=", "ref=", "replytocom", "trackback", "event"
    ]
    if any(keyword in url.lower() for keyword in trap_keywords):
        DataBase.blacklistURL[url] = "Calendar Trap"
        return True
    return False

def is_url_too_long(url, DataBase, max_len=2000):
    if len(url) > max_len:
        DataBase.blacklistURL[url] = f"URL Too Long ({len(url)} chars)"
        return True
    return False

def has_format_or_lang_trap(query, url, DataBase):
    trap_keys = {"lang", "language", "locale", "format", "output", "view", "display", "print", "pdf"}
    query_params = parse_qs(query)
    for key in query_params:
        if key.lower() in trap_keys:
            DataBase.blacklistURL[url] = "Language/Format/View Trap"
            return True
    return False

# A
def has_session_id(query, url, DataBase):
    session_keywords = ["sessionid", "token", "auth", "jsessionid", "sid"]
    query_keys = parse_qs(query).keys()
    if any(key.lower() in session_keywords for key in query_keys):
        DataBase.blacklistURL[url] = "Session/Token Trap"
        return True
    return False


def has_social_or_fragment_traps(url, DataBase):
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

def is_query_param_count_too_high(query, url, DataBase):
    query_params = parse_qs(query)
    if len(query_params) > 10:
        DataBase.blacklistURL[url] = "Query's Params Greater Than 10"
        return True
    return False

def has_path_repetition_trap(path, url, DataBase, repeat_threshold=5):
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
    parsed = urlparse(url)
    path = parsed.path
    query = parsed.query

    # Modularized trap checks
    if (
        is_query_too_long(query, url, DataBase) or
        is_path_too_long(path, url, DataBase) or
        has_repeated_path_segments(path, url, DataBase) or
        contains_trap_keywords(url, DataBase) or
        has_social_or_fragment_traps(url, DataBase) or
        is_query_param_count_too_high(query, url, DataBase) or
        has_path_repetition_trap(path, url, DataBase) or
        is_url_too_long(url, DataBase) or
        has_format_or_lang_trap(query, url, DataBase) or
        has_session_id(query, url, DataBase)
    ):
        # DataBase.feature_buffer.append(extract_url_features(url,0))
        return True
    return False
