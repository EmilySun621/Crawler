import hashlib
import zlib

class DuplicateDetector:
    ngram_size = 3
    threshold = 0.7
    seen_checksums = dict()
    seen_fingerprints = dict()
    near_duplicates = dict()

    @classmethod
    def get_fingerprints(cls, text):
        """
        Parameters:
            text (str): The input text to be fingerprinted.
    
        Returns:
            fps: A set of string fingerprints representing hashed n-grams.
    
        Generate a set of hashed n-gram fingerprints from the input text.
    
        This method converts the input text to lowercase, splits it into words, 
        and then forms overlapping n-grams of the specified size (`ngram_size`). 
        These fingerprints are used to efficiently compare text documents for 
        near-duplicate detection.
        # this is the method discussed in the lecture
        """
        words = text.lower().split()
        if len(words) < cls.ngram_size:
            return set()
        fps = set()
        for i in range(len(words) - cls.ngram_size + 1):
            ngram = " ".join(words[i:i + cls.ngram_size])
            h = hashlib.sha256(ngram.encode("utf-8")).hexdigest()
            fps.add(h[:16])
        return fps

    @classmethod
    def is_exact_duplicate(cls, text, url):
        """
        is_exact_duplicate() checks if the text is an exact duplicate by comparing it with previously seen texts.
        zlib.adler32 returns a deterministic 32-bit integer, if two strings have the same content, their Adler-32 checksums will match.
        we append the URL to self.seen_checksums[checksum] when a duplicate is detected is so we can track all the different URLs that point to the same exact content.
        If you see many URLs with the same content, it might indicate a crawler trap (e.g., session IDs, calendars).
        """
        checksum = zlib.adler32(text.lower().strip().encode("utf-8"))
        if checksum in cls.seen_checksums:
            cls.seen_checksums[checksum].append(url)
            return True
        cls.seen_checksums[checksum] = [url]
        return False

    @classmethod
    def is_near_duplicate(cls, text, url):
        """
        Determines whether the given text is a near-duplicate of previously seen texts.

        This method computes hashed n-gram fingerprints for the input text and compares
        them with fingerprints from previously seen URLs.
        If the similarity is above the configured threshold
        or if the fingerprints are identical, the URL is recorded as a near duplicate.

        Parameters:
        text (str): The text content to check for duplication.
        url (str): The URL associated with the content, used as a key for storage.

        Returns:
        bool: True if the text is a near duplicate; False otherwise.
        """
        fp = cls.get_fingerprints(text)
        for prev_url, prev_fp in cls.seen_fingerprints.items():
            if fp == prev_fp:
                cls.near_duplicates.setdefault(url, []).append(prev_url)
                return True
            inter = fp & prev_fp
            union = fp | prev_fp
            if len(union) == 0:
                continue
            similarity = len(inter) / len(union)
            if similarity > cls.threshold:
                cls.near_duplicates.setdefault(url, []).append(prev_url)
                return True
        cls.seen_fingerprints[url] = fp
        return False

    @classmethod
    def is_duplicate(cls, text, url):
        if cls.is_exact_duplicate(text, url):
            print(f"[EXACT DUPLICATE] {url}")
            return True
        if cls.is_near_duplicate(text, url):
            print(f"[NEAR DUPLICATE] {url}")
            return True
        return False
