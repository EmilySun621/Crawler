from collections import defaultdict, Counter
from urllib.parse import urlparse

class DataBase:
    lowerbound = 2000
    upperBound = 100000
    scraped = set()
    unique_urls = set()
    blacklistURL = set()
    maxWords = ["", 0]
    subdomain_count = defaultdict(int)
    word_counter = Counter()


    stop_words = set([
        "the", "is", "and", "in", "to", "of", "for", "a", "an", "on", "this", "that", "at",
        "by", "with", "as", "from", "it", "are", "was", "were", "be", "or", "which", "we",
        "can", "if", "but", "not", "has", "have", "had", "will", "would", "should", "do",
        "does", "did", "you", "your", "they", "their", "our", "its", "i"
    ])

    @staticmethod
    def update_max_words(url, word_count):
        if word_count > DataBase.maxWords[1]:
            DataBase.maxWords = [url, word_count]

    @staticmethod
    def add_subdomain(url):
        parsed = urlparse(url)
        subdomain = parsed.netloc.lower()
        DataBase.subdomain_count[subdomain] += 1

    @staticmethod
    def count_words(text):
        for word in text.lower().split():
            clean_word = ''.join(c for c in word if c.isalnum())
            if clean_word:
                DataBase.word_counter[clean_word] += 1

    #Save the blacklist locally 
    @staticmethod
    def save_blacklist(filepath="blacklist.txt"):
        with open(filepath, "w") as f:
            for url in DataBase.blacklistURL:
                f.write(url + "\n")
    
    #Load the blacklist to variable when restarting the project
    @staticmethod
    def load_blacklist(filepath="blacklist.txt"):
        try:
            with open(filepath, "r") as f:
                for line in f:
                    DataBase.blacklistURL.add(line.strip())
        except FileNotFoundError:
            pass

    @staticmethod
    def print_summary():
        with open("crawl_stats.txt", "w") as f:
            f.write(f"🔹 TOTAL UNIQUE PAGES FOUND: {len(DataBase.unique_urls)}\n\n")

            f.write("🔹 SUBDOMAIN COUNTS:\n")
            for subdomain, count in sorted(DataBase.subdomain_count.items()):
                f.write(f"{subdomain}: {count}\n")

            f.write("\n🔹 TOP 50 WORDS (excluding stop words):\n")
            filtered = [(word, freq) for word, freq in DataBase.word_counter.items()
            if word not in DataBase.stop_words]:
                top50 = sorted(filtered, key=lambda x: x[1], reverse=True)[:50]
                for word, freq in top50:
                    f.write(f"{word}: {freq}\n")

            f.write("\n🔹 LONGEST PAGE:\n")
            f.write(f"URL: {DataBase.maxWords[0]}\n")
            f.write(f"Word Count: {DataBase.maxWords[1]}\n")

            f.write("\n🔹 BLACKLISTED / TRAP URLS:\n")
            for url in DataBase.blacklistURL:
                f.write(url + "\n")

            f.write("🔁 EXACT DUPLICATES:\n")
            for checksum, urls in seen_checksums.items():
                if len(urls) > 1:
                    f.write(", ".join(urls) + "\n")

            f.write("\n🔄 NEAR DUPLICATES:\n")
            for url, dupes in near_duplicates.items():
                f.write(f"{url} ≈ {', '.join(dupes)}\n")

    @staticmethod
    def reset():
        DataBase.scraped.clear()
        DataBase.unique_urls.clear()
        DataBase.blacklistURL.clear()
        DataBase.maxWords = ["", 0]
        DataBase.subdomain_count = defaultdict(int)
        DataBase.word_counter = Counter()
