from collections import defaultdict, Counter
from urllib.parse import urlparse
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
    feature_buffer = []

    #C 
    @staticmethod
    def load_stop_words(filepath="stop_words.txt"):
        """
    Copied all stop words from the link the instructor provided to stop_words.txt. 
    load_stop_words() reads the stop words from the file and stores them in a set for quick lookup."""
        try:
            with open(filepath, "r") as f:
                DataBase.stop_words = set([line.strip() for line in f if line.strip()])
        except FileNotFoundError:
            print("[WARNING] stop_words.txt not found. Stop word filtering disabled.")

    @staticmethod
    def update_max_words(url, word_count):
        """
        update_max_words() checks if the current word count is greater than the maximum word count recorded.
        If it is, it updates the maximum word count and the corresponding URL.
        """
        if word_count > DataBase.maxWords[1]:
            DataBase.maxWords = [url, word_count]

    @staticmethod
    def add_subdomain(url):
        """
        Add_subdomain() extracts the subdomain from the URL and updates the subdomain count in the database.
        It uses urlparse to parse the URL and lower() to ensure the subdomain is in lowercase as the URL is case-insensitive.
        """
        parsed = urlparse(url)
        subdomain = parsed.netloc.lower()
        DataBase.subdomain_count[subdomain] += 1

    #A
    @staticmethod
    def count_words(text):
        """
            Counts the frequency of valid words in the url text 
            add the word count in `DataBase.word_counter`.
            Skip if:
            - It's empty after cleaning
            - It's a number (only digits)
            - It's a single letter
            A valid word should be alphanumeric
    
            This method is useful in other method count the
            most frequent words.
        """
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
    def save_blacklist(filepath="blacklist.txt"):
        """
            Saves all blacklisted URLs and their reasons to a specified file.
        
            Args:
                filepath (str): Path to the file where blacklist entries will be written.
                                Each line contains a reason and the corresponding URL.
        
        """
        with open(filepath, "w") as f:
            for url, reason in DataBase.blacklistURL.items():
                f.write(f"{reason}: {url}\n")
            f.flush()

    @staticmethod
    def load_blacklist(filepath="blacklist.txt"):
         """Copied all stop words from the link the instructor provided to stop_words.txt. 
    load_stop_words() reads the stop words from the file and stores them in a set for quick lookup."""
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

    @staticmethod
    def print_summary(seen_checksums,near_duplicates):
         """
        Writes crawl statistics to a summary file.
    
        Includes unique URL count, subdomain counts, top 50 words, longest page,
        exact and near duplicates, and blacklist reason counts.
    
        Args:
            seen_checksums (dict): Mapping of exact duplicate checksums to URL lists.
            near_duplicates (dict): Mapping of near-duplicate fingerprints to URL lists.
        """
        with open("crawl_stats.txt", "w") as f:
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
