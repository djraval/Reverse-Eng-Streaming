#!/usr/bin/env python3

import requests, warnings, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

warnings.filterwarnings("ignore")
proxies = {'http': 'socks5h://127.0.0.1:1080', 'https': 'socks5h://127.0.0.1:1080'}

def get_links(url):
    try:
        response = requests.get(url, timeout=10, proxies=proxies)
        soup = BeautifulSoup(response.text, 'html.parser')
        return [urljoin(url, a['href']) for a in soup.find_all('a', href=True)
                if any(pattern in a['href'] for pattern in ['crichdplayer', 'channel', 'live', 'stream'])]
    except:
        return []

def get_channel_data(url):
    try:
        response = requests.get(url, timeout=10, proxies=proxies)
        soup = BeautifulSoup(response.text, 'html.parser')
        name = soup.find('h1').text.strip() if soup.find('h1') else "Unknown"
        php_match = re.search(r'embeds\[0\].*?src=[\'"]//([^\'\"]+\.php)[\'"]', response.text)
        if php_match:
            php_url = f"https://{php_match.group(1)}"
            fid_response = requests.get(php_url, timeout=10, proxies=proxies)
            fid_match = re.search(r'fid\s*=\s*[\'"]([^\'"]+)[\'"]', fid_response.text)
            if fid_match:
                return (fid_match.group(1), name)
    except:
        pass
    return None

def test_stream(fid):
    try:
        url = f"https://apex2nova.com/premium.php?player=desktop&live={fid}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.6',
            'Referer': "https://stream.crichd.sc/",
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Sec-Fetch-Dest': 'iframe',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Storage-Access': 'none',
            'Priority': 'u=0, i',
            'Sec-Ch-Ua': '"Brave";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-GPC': '1',
            'Upgrade-Insecure-Requests': '1'
        }
        response = requests.get(url, headers=headers, timeout=15, proxies=proxies)

        if response.status_code != 200:
            return None  # No M3U8 URL found

        # Extract stream URL using the JavaScript pattern (same as main.py)
        scripts = BeautifulSoup(response.text, 'html.parser').find_all('script')
        for script in scripts:
            if script.text and all(k in script.text for k in ["P2PEngineHls", "Clappr.Player", ".join(\"\")"]):
                match = re.search(r'\[(.*?)\]\s*\.\s*join\s*\(\s*""\s*\)', script.text)
                if match:
                    chars = [c.strip().strip('"\'').replace('\\/', '/') for c in match.group(1).split(',') if c.strip()]
                    stream_url = "".join(chars)

                    # Clean and normalize the URL (same as main.py)
                    cleaned_url = re.sub(r'(?<!:)//+', '/', stream_url)
                    if not cleaned_url.startswith(('http://', 'https://')):
                        cleaned_url = f"https://{cleaned_url}"

                    if cleaned_url.startswith("http") and ".m3u8" in cleaned_url:
                        # Test M3U8 content
                        try:
                            m3u8_response = requests.get(cleaned_url, timeout=10, proxies=proxies)
                            if m3u8_response.status_code == 200 and len(m3u8_response.text.strip()) > 0:
                                return "WORKING"
                            else:
                                return "NOT WORKING"
                        except:
                            return "NOT WORKING"

        return None  # No M3U8 URL found
    except Exception:
        return None  # No M3U8 URL found

def discover_channels():
    channel_urls = []
    links = get_links("https://new.crichd.tv")
    channel_urls.extend(links)

    for link in links[:10]:
        channel_urls.extend(get_links(link))

    channel_urls = list(set(channel_urls))

    with ThreadPoolExecutor(5) as executor:
        results = list(executor.map(get_channel_data, channel_urls))

    return [r for r in results if r]

def main():
    channels = discover_channels()
    working_channels = []

    print(f"Testing {len(channels)} discovered channels for M3U8 generation...")

    for i, (fid, name) in enumerate(channels):
        status = test_stream(fid)
        if status == "WORKING":  # Only include working channels
            working_channels.append((fid, name))
            print(f"[{i+1}/{len(channels)}] {fid}: WORKING")
        elif status == "NOT WORKING":
            print(f"[{i+1}/{len(channels)}] {fid}: NOT WORKING")
        else:
            print(f"[{i+1}/{len(channels)}] {fid}: NO M3U8 (skipped)")

    # Sort channels by channel_id
    working_channels.sort(key=lambda x: x[0])

    with open('channels.txt', 'w', encoding='utf-8') as f:
        for fid, name in working_channels:
            f.write(f'{fid},"{name}"\n')

    print(f"Generated channels.txt with {len(working_channels)} working channels")

if __name__ == "__main__":
    main()
