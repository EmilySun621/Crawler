import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

from scraper import is_valid      

# -------------------------------------------------------------------------
LOG_FILE        = Path("run1_Worker.log")      
ALLOWED_FILE    = Path("calendar_allowed_urls.txt")
BLOCKED_FILE    = Path("calendar_blocked_urls.txt")
# -------------------------------------------------------------------------

URL_RE   = re.compile(r"https?://[^\s,>]+")

# path contains one of these words
KEYWORD_RE = re.compile(r"/(?:event|events|calendar|day)(?:/|$)", re.I)

# path contains an explicit date slug (YYYY/MM(/DD) or YYYY-MM(-DD))
DATE_RE = re.compile(
    r"/(?:19|20)\d{2}(?:[-/](?:0[1-9]|1[0-2]))(?:[-/](?:0[1-9]|[12]\d|3[01]))?(/|$)",
    re.I,
)

def _calendar_candidates():
    """Yield all calendar‑related URLs found in the log file."""
    if not LOG_FILE.exists():
        raise FileNotFoundError(f"Cannot find log file {LOG_FILE}")

    seen = set()
    with LOG_FILE.open(encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            for url in URL_RE.findall(line):
                if url in seen:
                    continue
                seen.add(url)

                p = urlparse(url)
                q = p.query.lower()

                if KEYWORD_RE.search(p.path) or DATE_RE.search(p.path):
                    yield url
                    continue

                # calendar plug‑in query params
                if any(x in q for x in ("tribe_event_display", "ical_export", "feed=tribe")):
                    yield url

class CalendarURLDump(unittest.TestCase):
    """Generate the allowed / blocked lists for manual inspection."""

    @classmethod
    def setUpClass(cls):
        cls.allowed, cls.blocked = [], []

        for url in _calendar_candidates():
            (cls.allowed if is_valid(url) else cls.blocked).append(url)

        # write files
        ALLOWED_FILE.write_text("\n".join(cls.allowed), encoding="utf-8")
        BLOCKED_FILE.write_text("\n".join(cls.blocked), encoding="utf-8")

    def test_summary(self):
        print(f"{len(self.allowed):>5} allowed URLs  → {ALLOWED_FILE}")
        print(f"{len(self.blocked):>5} blocked URLs  → {BLOCKED_FILE}")
        # Always pass – this suite is for data extraction, not assertions.
        self.assertTrue(True)

if __name__ == "__main__":
    unittest.main()