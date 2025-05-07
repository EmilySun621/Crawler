from collections import defaultdict, Counter
from urllib.parse import urlparse
from collections import defaultdict
import time

class DataBase:
    lowerBound = 200
    upperBound = 1000000
    scraped = set()
    unique_urls = set()
    blacklistURL = dict()
    maxWords = ["", 0]
    subdomain_count = defaultdict(int)
    word_counter = Counter()
    visited_path = set()
    stop_words = set()
    start_time = 0
    # Load stop words once at startup
    feature_buffer = []

    # @staticmethod
    # def start_timer():
    #     DataBase.start_time = time.time()

    # @staticmethod
    # def get_current_elapsed():
    #     return time.time() - DataBase.start_time if DataBase.start_time else 0

    #C 
    @staticmethod
    def load_stop_words(filepath="/home/qirans3/121/a2/spacetime-crawler4py/stop_words.txt"):
        try:
            with open(filepath, "r") as f:
                DataBase.stop_words = set([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            print("[WARNING] stop_words.txt not found. Stop word filtering disabled.")

    @staticmethod
    def update_max_words(url, word_count):
        if word_count > DataBase.maxWords[1]:
            DataBase.maxWords = [url, word_count]

    @staticmethod
    def add_subdomain(url):
        parsed = urlparse(url)
        subdomain = parsed.netloc.lower()
        DataBase.subdomain_count[subdomain] += 1

    #A
    @staticmethod
    def count_words(text):
        for word in text.lower().split():
            clean_word = ''.join(c for c in word if c.isalnum())
            # Skip if:
            # - It's empty after cleaning
            # - It's a number (only digits)
            # - It's a single letter
            if not clean_word or clean_word.isdigit() or len(clean_word) == 1:
                continue

            DataBase.word_counter[clean_word] += 1

    @staticmethod
    def save_blacklist(filepath="/home/qirans3/121/a2/spacetime-crawler4py/blacklist.txt"):
        with open(filepath, "w") as f:
            for url, reason in DataBase.blacklistURL.items():
                f.write(f"{reason}: {url}\n")
                f.flush()

    @staticmethod
    def load_blacklist(filepath="/home/qirans3/121/a2/spacetime-crawler4py/blacklist.txt"):
        try:
            with open(filepath, "r") as f:
                for line in f:
                    line = line.strip()
                    if "http" in line:
                        reason_part, url_part = line.split("http", 1)
                        reason = reason_part.strip(" :")
                        url = "http" + url_part.strip()
                        DataBase.blacklistURL[url] = reason
        except FileNotFoundError:
            pass

    # @staticmethod
    # def log_live_progress(filepath="live_stats.txt"):
    #     elapsed = DataBase.get_current_elapsed()
    #     pages = len(DataBase.scraped)
    #     speed = pages / elapsed if elapsed > 0 else 0

    #     with open(filepath, "a") as f:
    #         f.write(f"[{time.strftime('%H:%M:%S')}] Pages: {pages}, Time: {elapsed:.2f}s, Speed: {speed:.2f} pages/sec\n")


    #E 到时候加到parameter系数就好了
    @staticmethod
    def print_summary(seen_checksums,near_duplicates):
        with open("/home/qirans3/121/a2/spacetime-crawler4py/crawl_stats.txt", "w") as f:
            f.write(f"🔹 TOTAL UNIQUE PAGES FOUND: {len(DataBase.unique_urls)}\n\n")

            f.write("🔹 SUBDOMAIN COUNTS:\n")
            for subdomain, count in sorted(DataBase.subdomain_count.items()):
                f.write(f"{subdomain}: {count}\n")

            f.write("\n🔹 TOP 50 WORDS (excluding stop words):\n")
            filtered = [
                (word, freq) for word, freq in DataBase.word_counter.items()
                if word not in DataBase.stop_words
            ]
            top50 = sorted(filtered, key=lambda x: x[1], reverse=True)[:50]
            for word, freq in top50:
                f.write(f"{word}: {freq}\n")

            f.write("\n🔹 LONGEST PAGE:\n")
            f.write(f"URL: {DataBase.maxWords[0]}\n")
            f.write(f"Word Count: {DataBase.maxWords[1]}\n")


            f.write("\n🔁 EXACT DUPLICATES:\n")
            if seen_checksums:
                for checksum, urls in seen_checksums.items():
                    if len(urls) > 1:
                        f.write(", ".join(urls) + "\n")

            f.write("\n🔄 NEAR DUPLICATES:\n")
            for fingerprint, urls in near_duplicates.items():
                if len(urls) > 1:
                    f.write(f"{fingerprint} ≈ {', '.join(urls)}\n")

            reason_counter = defaultdict(int)
            for url, reason in DataBase.blacklistURL.items():
                reason_counter[reason] += 1

            f.write("\n🔹 BLACKLIST REASONS (counts):\n")
            for reason, count in sorted(reason_counter.items(), key=lambda x: x[1], reverse=True):
                f.write(f"{reason}: {count}\n")
            f.flush()


    # @staticmethod
    # def reset():
    #     DataBase.scraped.clear()
    #     DataBase.unique_urls.clear()
    #     DataBase.blacklistURL.clear()
    #     DataBase.maxWords = ["", 0]
    #     DataBase.subdomain_count = defaultdict(int)
    #     DataBase.word_counter = Counter()
    #     DataBase.visited_path = set()
