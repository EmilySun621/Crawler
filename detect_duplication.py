import hashlib
import zlib

class DuplicateDetector:
    def __init__(self, ngram_size=3, threshold=0.9):
        self.ngram_size = ngram_size
        self.threshold = threshold
        self.seen_checksums = dict()
        self.seen_fingerprints = dict()
        self.near_duplicates = dict()

    def get_fingerprints(self, text):
        words = text.lower().split()
        if len(words) < self.ngram_size:
            return set()
        fps = set()
        for i in range(len(words) - self.ngram_size + 1):
            ngram = " ".join(words[i:i+self.ngram_size])
            h = hashlib.sha256(ngram.encode("utf-8")).hexdigest()
            fps.add(h[:16])
        return fps

    def is_exact_duplicate(self, text, url):
        checksum = zlib.adler32(text.lower().strip().encode("utf-8"))
        if checksum in self.seen_checksums:
            self.seen_checksums[checksum].append(url)
            return True
        self.seen_checksums[checksum] = [url]
        return False

    def is_near_duplicate(self, text, url):
        fp = self.get_fingerprints(text)
        for prev_url, prev_fp in self.seen_fingerprints.items():
            if fp == prev_fp:
                self.near_duplicates.setdefault(url, []).append(prev_url)
                return True
            inter = fp & prev_fp
            union = fp | prev_fp
            if len(union) == 0:
                continue
            similarity = len(inter) / len(union)
            if similarity > self.threshold:
                self.near_duplicates.setdefault(url, []).append(prev_url)
                return True
        self.seen_fingerprints[url] = fp
        return False

    def is_duplicate(self, text, url):
        if self.is_exact_duplicate(text, url):
            print(f"[EXACT DUPLICATE] {url}")
            return True
        if self.is_near_duplicate(text, url):
            print(f"[NEAR DUPLICATE] {url}")
            return True
        return False