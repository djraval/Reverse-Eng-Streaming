#!/usr/bin/env python3

# Channel Discovery Workflow:
# 1. Crawl crichd.tv to find all channel pages (crichdplayer.com links)
# 2. Extract channel names from H1 tags and PHP URLs from JavaScript embeds
# 3. Fetch PHP pages and extract FIDs using regex pattern fid="..."
# 4. Output: FID, channel name, webpage URL, and source PHP link

import requests, warnings, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

warnings.filterwarnings("ignore")
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})
proxies = {'http': 'socks5h://127.0.0.1:1080', 'https': 'socks5h://127.0.0.1:1080'}
visited, all_links = set(), set()



def get_links(url):
    for _ in range(2):
        try:
            soup = BeautifulSoup(session.get(url, timeout=10, proxies=proxies).text, 'html.parser')
            return [urljoin(url, a['href']) for a in soup.find_all('a', href=True)
                    if not any(x in a['href'] for x in ['.css', '.js', '.png', 'mailto:'])]
        except: pass
    return []

def get_channel_data(url):
    for _ in range(2):
        try:
            response = session.get(url, timeout=10, proxies=proxies)
            soup = BeautifulSoup(response.text, 'html.parser')

            name = soup.find('h1').text.strip() if soup.find('h1') else "Unknown"
            php_match = re.search(r'embeds\[0\].*?src=[\'"]//([^\'\"]+\.php)[\'"]', response.text)
            php_url = f"https://{php_match.group(1)}" if php_match else None

            return {"name": name, "php_url": php_url, "webpage": url}
        except: pass
    return None

def get_fid(php_url):
    for _ in range(2):
        try:
            response = session.get(php_url, timeout=10, proxies=proxies)
            fid_match = re.search(r'fid\s*=\s*[\'"]([^\'"]+)[\'"]', response.text)
            return fid_match.group(1) if fid_match else None
        except: pass
    return None

def crawl(urls, level=1):
    if level > 3 or not urls: return
    visited.update(urls)
    with ThreadPoolExecutor(10) as e:
        new_links = [l for links in e.map(get_links, urls) for l in links]
    unique = [l for l in set(new_links) if l not in visited]
    all_links.update(unique)
    crawl(unique, level + 1)

crawl(["https://new.crichd.tv"])
channel_urls = [link for link in all_links if 'crichdplayer.com' in link]

with ThreadPoolExecutor(10) as executor:
    channel_data = list(executor.map(get_channel_data, channel_urls))

valid_channels = [c for c in channel_data if c and c['php_url']]

php_urls = [c['php_url'] for c in valid_channels]
with ThreadPoolExecutor(10) as executor:
    fids = list(executor.map(get_fid, php_urls))



successful_channels = [(channel, fid) for channel, fid in zip(valid_channels, fids) if fid]

print(f"Successfully discovered {len(successful_channels)} FIDs")

for channel, fid in successful_channels:
    print(f"{fid}: {channel['name']}")
    print(f"  webpage: {channel.get('webpage', 'N/A')}")
    print(f"  source: {channel['php_url']}")
    print()
