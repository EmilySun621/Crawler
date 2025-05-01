import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from detect_duplication import DuplicateDetector
from html_cleanup import *
from database import DataBase
from avoid_trap import *
from url_info import *
from url_info import flush_to_csv
from urllib.parse import urldefrag

detector = DuplicateDetector()

def scraper(url, resp):
    print(f"[SCRAPER] Crawling: {url} - Status: {resp.status}")
    links = extract_next_links(url, resp)
    valid_links = []
    for link in links:
        if is_valid(link):
            valid_links.append(link)
        else:
            blacklistURL.add(link) = ["Invalid Link"]
    return valid_links

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

    # Already in the blacklist
    if url in DataBase.blacklistURL:
        return []

    if resp.status != 200:
        DataBase.blacklistURL[url] = f"Status = {resp.status}" 
        # DataBase.feature_buffer.append(extract_url_features(url,0))
        return []

    if resp.raw_response is None:
        DataBase.blacklistURL[url] = f"Actual Page Not Found" 
        # DataBase.feature_buffer.append(extract_url_features(url,0))
        return []

    if "do=" in url:
        DataBase.blacklistURL[url] = "DokuWiki do= parameter trap"
        # DataBase.feature_buffer.append(extract_url_features(url,0))
        return []

    # extract text the html 
    text = clean_html_text(resp.raw_response.content) 
    
    #detect if text is duplicate 
    if detector.is_duplicate(text, url):
        return []
    
    # detect if samples are too large or too small, 
    if not filter_extreme_large_small_files(url,DataBase, text, resp, DataBase.lowerBound, DataBase.upperBound):
        link, _ = urldefrag(url)
        DataBase.unique_urls.add(link)
        return []

    # detet if url contain traps
    if trap_identify(url,DataBase):
        link, _ = urldefrag(url)
        DataBase.unique_urls.add(link)
        return []

    #detect if url contain low information
    # if is_low_information_path(url,DataBase):
    #     link, _ = urldefrag(url)
    #     DataBase.unique_urls.add(link)
    #     return []

    #After passed all filters, save data to database
    DataBase.count_words(text)
    DataBase.add_subdomain(url)
    DataBase.scraped.add(url)
    link, _ = urldefrag(url)
    DataBase.unique_urls.add(link)
    DataBase.update_max_words(url, len(text))
    # DataBase.feature_buffer.append(extract_url_features(url,1))
    # if len(DataBase.feature_buffer) >= 20:
    #     flush_to_csv(DataBase.feature_buffer)
    DataBase.print_summary() 
    DataBase.save_blacklist()

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")
    links = []

    for link_tag in soup.find_all('a'):
        href = link_tag.get('href')
        #Don't select anchor, email link, and javascript behavior 
        if href and not href.startswith(("#", "mailto:", "javascript:")):
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
        r".*\.(ppsx|mpg|css|js|bmp|gif|jpe?g|ico"
        r"|png|tiff?|mid|mp2|mp3|mp4"
        r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
        r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
        r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
        r"|epub|dll|cnf|tgz|sha1"
        r"|thmx|mso|arff|rtf|jar|csv"
        r"|rm|smil|wmv|swf|wma|zip|rar|gz"
        r"|pptm|docm|xlsm|odt|ods|odp|rtfd"
        r"|xz|lz|lzma|zst|zstd|img"
        r"|c|cpp|h|java|py|go|ts|rs|sh|bat"
        r"|mat|hdf5?|np[yz]|sav|dta|por|rdata|rds"
        r"|pak2?|blend"
        r"|ttf|otf|woff2?"
        r"|log|bak|tmp|swp"
        r"|sig|asc|gpg|key"
        r"|php|html|m|txt)$",
        parsed.path.lower()
    )
            return False
        return True
    except TypeError:
        print ("TypeError for ", parsed)
        raise
