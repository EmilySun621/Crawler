from urllib.parse import urlparse


def trap_identify(url,DataBase):
    parsed = urlparse(url)
    path = parsed.path
    query = parsed.query

    if len(query) > 100:
        DataBase.blacklistURL[url] = "100+ Queries"
        return True

    if path.count('/') > 10:
        DataBase.blacklistURL[url] = "Path Too Long"
        return True
    
    segments = path.split('/')
    if len(segments) != len(set(segments)):
        DataBase.blacklistURL[url] = "Repeated Segments"
        return True
    
    trap_keywords = [
    "calendar", "date", "year", "month", "day", "sessionid",
    "sort=", "ref=", "replytocom", "trackback", "event"
    ]

    if any(keyword in url.lower() for keyword in trap_keywords):
        DataBase.blacklistURL[url] = "Calendar Trap"
        return True

    if "?share=" in url:
        DataBase.blacklistURL[url] = "Social Share URL"
        return True
    if "redirect" in url:
        DataBase.blacklistURL[url] = "Redirect Trap"
        return True
    if "#comment" in url:
        DataBase.blacklistURL[url] = "Fragment Comment Anchor"
        return True
    if "#respond" in url:
        DataBase.blacklistURL[url] = "Fragment Respond Anchor"
        return True
    if "#comments" in url:
        DataBase.blacklistURL[url] = "Fragment Comments Anchor"
        return True
    
    return False
