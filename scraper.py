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

#A
def scraper(url, resp):
    """
    Arguments:
        url (str): The URL from the server.
        resp (object): The page on that url from the server.
    Returns:
        list: A list of valid URLs.
    Description:
        Extract links from the given URL using the response object.
        Check each extracted link:
            - If the link is valid, append it to the valid_links list.
            - If the link is invalid, add it to the blacklistURL dictionary in the DataBase.
        Finally, return the list of valid links.
    """
    print(f"[SCRAPER] Crawling: {url} - Status: {resp.status}")
    links = extract_next_links(url, resp)
    valid_links = []
    for link in links:
        if is_valid(link):
            valid_links.append(link)
        else:
            DataBase.blacklistURL[link] = "invalid link"
    return valid_links

#E 
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
        link, _ = urldefrag(url)
        DataBase.unique_urls.add(link)
        return []


    # extract text the html 
    text = clean_html_text(resp.raw_response.content)

     # detect if samples are too large or too small, 
    if not filter_extreme_large_small_files(url,DataBase, text, resp, DataBase.lowerBound, DataBase.upperBound):
        link, _ = urldefrag(url)
        DataBase.unique_urls.add(link)
        return []
    
    #detect if text is duplicate 
    if DuplicateDetector.is_duplicate(text, url):
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
    DataBase.print_summary(DuplicateDetector.seen_checksums,DuplicateDetector.near_duplicates) 
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


#C
def is_valid(url):
   """
    1. Only allows pages on UCI’s School of Information & Computer Sciences subdomains or the ICS section of today.uci.edu. Every other host is immediately dropped.
    2. Uses a giant regex to block URLs ending in “static” or binary file types (images, videos, archives, docs, code files, datasets, fonts, etc.). 
    You skip anything that looks like a download rather than an HTML page.
    3. Blocks DokuWiki action URLs like ?do=edit or ?do=show, which would just let you bounce around the same content in different modes.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        netloc = parsed.netloc.lower()
        path = parsed.path.lower()

        if (
            netloc.endswith("ics.uci.edu")
            or netloc.endswith("cs.uci.edu")
            or netloc.endswith("informatics.uci.edu")
            or netloc.endswith("stat.uci.edu")
            or (netloc == "today.uci.edu" and path.startswith("/department/information_computer_sciences"))
        ):
            pass
        else:
            return False
        if "cs122b" in path:
            DataBase.blacklistURL[url] = "Filtered: contains cs122b"
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
    ):
            return False

        if "do=" in parsed.path.lower():
            DataBase.blacklistURL[url] = "DokuWiki do= parameter trap"
            # DataBase.feature_buffer.append(extract_url_features(url,0))
            return False
        return True

    except TypeError:
        print ("TypeError for ", parsed)
        raise
