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
        checksum = zlib.adler32(text.lower().strip().encode("utf-8"))
        if checksum in cls.seen_checksums:
            cls.seen_checksums[checksum].append(url)
            return True
        cls.seen_checksums[checksum] = [url]
        return False

    @classmethod
    def is_near_duplicate(cls, text, url):
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
