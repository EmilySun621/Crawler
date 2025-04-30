import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from detect_duplication import DuplicateDetector
from html_cleaner import clean_html_text
from crawler.database import DataBase as db


detector = DuplicateDetector()

def scraper(url, resp):
    print(f"[SCRAPER] Crawling: {url} - Status: {resp.status}")
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    if resp.status != 200 or resp.raw_response is None:
        d.blacklistURL.add(url)
        print(f"[BlackListing]: Falling to find new link in {url}.")
        return []

    text = clean_html_text(resp.raw_response.content) 

    if detector.is_duplicate(text, url):
        return []
    
    #Skip large file with tiny text 
    if len(resp.raw_response.content) > 1_000_000 and len(text) < 500:
        print(f"[SKIP] Large file with low content: {url}")
        return []
    links = []
    for link_tag in soup.find_all('a'):
        href = link_tag.get('href')
        #Don't select anchor, email link, and javascript behavior 
        if href and not herf.startswith('#') and not href.startswith("mailto") and not href.startswith("javascript"):
            full_url = urljoin(url, href)
            links.append(full_url)
    # only maintain the unique links
    return list(set(links))

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        netloc = parsed.netloc.lower()
        path = parsed.path.lower()

        if (
            netloc.endswith(".ics.uci.edu")
            or netloc.endswith(".cs.uci.edu")
            or netloc.endswith(".informatics.uci.edu")
            or netloc.endswith(".stat.uci.edu")
            or (netloc == "today.uci.edu" and path.startswith("/department/information_computer_sciences"))
        ):
            pass
        else:
            return False
        if re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            r"|png|tiff?|mid|mp2|mp3|mp4"
            r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            r"|epub|dll|cnf|tgz|sha1"
            r"|thmx|mso|arff|rtf|jar|csv"
            r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False
        return True
    except TypeError:
        print ("TypeError for ", parsed)
        raise
