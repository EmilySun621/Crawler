import csv
from urllib.parse import urlparse, parse_qs
from collections import Counter
import os


def flush_to_csv(feature_buffer, file_path="machine_learning.csv"):
    if not feature_buffer:
        return 

    fieldnames = list(feature_buffer[0].keys())
    

    write_header = not os.path.exists(file_path)

    with open(file_path, mode="a", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerows(feature_buffer)


    feature_buffer.clear()
    print(f"Flushed {len(fieldnames)} columns × {len(feature_buffer)} rows to {file_path}")



def extract_url_features(url, input_label):
    parsed = urlparse(url)
    path = parsed.path
    query = parsed.query

    query_params = parse_qs(query)
    query_keys = query_params.keys()
    paths_split = [segment for segment in path.split("/") if segment]

    trap_keywords = [
        "calendar", "date", "year", "month", "day",
        "sort=", "ref=", "replytocom", "trackback", "event"
    ]

    session_keywords = ["sessionid", "token", "auth", "jsessionid", "sid"]
    format_keys = {"lang", "language", "locale", "format", "output", "view", "display", "print", "pdf"}
    social_fragment_keywords = ["?share=", "redirect", "#comment", "#respond", "#comments"]

    features = {
        "url": url,
        "url_length": len(url),
        "path_depth": path.count('/'),
        "query_length": len(query),
        "query_param_count": len(query_params),
        "has_fragment": int("#" in url),
        "has_share_or_redirect": int(any(k in url for k in social_fragment_keywords)),
        "has_trap_keyword": int(any(k in url.lower() for k in trap_keywords)),
        "has_session_id": int(any(k.lower() in session_keywords for k in query_keys)),
        "has_format_param": int(any(k.lower() in format_keys for k in query_keys)),
        "has_repeated_path_segments": int(len(paths_split) != len(set(paths_split))),
        "max_segment_repeat_count": max((count for _, count in Counter(paths_split).items()), default=0),
        "is_path_too_long": int(path.count('/') > 10),
        "is_query_too_long": int(len(query) > 100),
        "is_url_too_long": int(len(url) > 2000),
        "is_query_param_count_too_high": int(len(query_params) > 10),
        "has_path_repetition_trap": int(
            Counter(paths_split).most_common(1)[0][1] > 5 if paths_split else 0
        ),
        "label": input_label
    }

    with open("machine_learning.csv", mode="a", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(features.keys()))
        writer.writerow(features)

    return features
