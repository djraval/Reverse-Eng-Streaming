#!/usr/bin/env python3

import requests, warnings, re, os, argparse, socket
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

warnings.filterwarnings("ignore")

# Configuration
def setup_cloudflare_dns():
    try:
        import dns.resolver
        resolver = dns.resolver.Resolver()
        resolver.nameservers = ['1.1.1.1', '1.0.0.1']
        original_getaddrinfo = socket.getaddrinfo
        def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
            try:
                return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (str(resolver.resolve(host, 'A')[0]), port))]
            except:
                return original_getaddrinfo(host, port, family, type, proto, flags)
        socket.getaddrinfo = custom_getaddrinfo
        return True
    except ImportError:
        return False

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

parser = argparse.ArgumentParser(description='Extract streaming links')
parser.add_argument('--proxy', type=str, help='Use proxy (e.g., 127.0.0.1:8080, socks5://127.0.0.1:1080). Defaults to http:// if no protocol specified.')
args = parser.parse_args()

proxies = None
public_ip = "unknown"

if not args.proxy:
    print("Using Cloudflare DNS (1.1.1.1)" if setup_cloudflare_dns() else "dnspython not available, using system DNS")
else:
    proxy_url = args.proxy if args.proxy.startswith(('http://', 'https://', 'socks5://', 'socks5h://')) else f'socks5h://{args.proxy}'
    proxies = {'http': proxy_url, 'https': proxy_url}

try:
    response = requests.get('https://www.cloudflare.com/cdn-cgi/trace', proxies=proxies, timeout=5)
    if response.status_code == 200:
        for line in response.text.strip().split('\n'):
            if line.startswith('ip='):
                public_ip = line.split('=')[1]
                break
    print(f"Using {'proxy (' + proxy_url + ')' if args.proxy else 'direct connection'} - IP: {public_ip}")
except Exception as e:
    print(f"Connection failed: {e}")

# Utility functions

def get_links(url):
    try:
        soup = BeautifulSoup(requests.get(url, timeout=10, proxies=proxies).text, 'html.parser')
        return [urljoin(url, a['href']) for a in soup.find_all('a', href=True)
                if any(pattern in a['href'] for pattern in ['crichdplayer', 'channel', 'live', 'stream'])]
    except:
        return []

def save_js_snippet(fid, script_text, page_url):
    try:
        os.makedirs('logs', exist_ok=True)
        with open(f"logs/js_snippet_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{fid}.js", 'w', encoding='utf-8') as f:
            f.write(f"// Source URL: {page_url}\n// Captured: {datetime.now().isoformat()}\n// {'=' * 50}\n\n{script_text}")
    except:
        pass

# Core functions

def get_channel_data(url):
    try:
        response = requests.get(url, timeout=10, proxies=proxies)
        soup = BeautifulSoup(response.text, 'html.parser')
        name = soup.find('h1').text.strip() if soup.find('h1') else "Unknown"
        php_match = re.search(r'embeds\[0\].*?src=[\'"]//([^\'\"]+\.php)[\'"]', response.text)
        if php_match:
            fid_response = requests.get(f"https://{php_match.group(1)}", timeout=10, proxies=proxies)
            fid_match = re.search(r'fid\s*=\s*[\'"]([^\'"]+)[\'"]', fid_response.text)
            if fid_match:
                return (fid_match.group(1), name)
    except:
        pass
    return None

def get_m3u8_url(fid):
    try:
        api_url = f"https://apex2nova.com/premium.php?player=desktop&live={fid}"
        response = requests.get(api_url, headers=headers, timeout=15, proxies=proxies)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        for script in soup.find_all('script'):
            script_content = script.text
            if not script_content:
                continue

            required_keywords = ["P2PEngineHls", "Clappr.Player", ".join(\"\")"]
            if not all(keyword in script_content for keyword in required_keywords):
                continue

            save_js_snippet(fid, script_content, api_url) # Original side-effect

            match = re.search(r'\[(.*?)\]\s*\.\s*join\s*\(\s*""\s*\)', script_content)
            if not match:
                continue

            raw_url_parts = match.group(1).split(',')
            processed_parts = [
                part.strip().strip('"\'').replace('\\/', '/')
                for part in raw_url_parts if part.strip()
            ]
            stream_url = "".join(processed_parts)

            cleaned_url = re.sub(r'(?<!:)//+', '/', stream_url)
            if not cleaned_url.startswith(('http://', 'https://')):
                cleaned_url = f"https://{cleaned_url}"

            if ".m3u8" not in cleaned_url:
                continue

            try:
                m3u8_response = requests.get(cleaned_url, timeout=10, proxies=proxies)
                if m3u8_response.status_code == 200 and m3u8_response.text.strip():
                    return cleaned_url
            except requests.RequestException:
                pass # Try next script if M3U8 fetch fails
        
        return None # No suitable M3U8 URL found in any script
        
    except requests.RequestException: # For initial API call error
        return None
    except Exception: # For other errors like BS4 parsing
        return None

def main():
    print("Discovering channels...")
    links = get_links("https://new.crichd.tv")
    channel_urls = links + [link for link in links[:10] for link in get_links(link)]
    channel_urls = list(set(channel_urls))

    with ThreadPoolExecutor(32) as executor:
        channels = [r for r in executor.map(get_channel_data, channel_urls) if r]

    print(f"Found {len(channels)} channels, testing streams...")

    working_streams = []
    with ThreadPoolExecutor(32) as executor:
        futures = [executor.submit(get_m3u8_url, fid) for fid, _ in channels]
        for i, future in enumerate(futures):
            fid, name = channels[i]
            m3u8_url = future.result()
            if m3u8_url:
                working_streams.append((fid, name, m3u8_url))

    all_hostnames = sorted(set(url.split('/')[2] for _, _, url in working_streams))

    unique_working_streams = {}
    for fid, name, url in working_streams:
        if fid not in unique_working_streams or len(name) < len(unique_working_streams[fid][1]):
            unique_working_streams[fid] = (fid, name, url)

    working_streams = sorted(unique_working_streams.values(), key=lambda x: x[0])

    with open('streams.txt', 'w', encoding='utf-8') as f:
        f.write(f'# Generated: {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}\n')
        f.write(f'# Public IP: {public_ip}\n')
        f.write(f'# Hostnames: {", ".join(all_hostnames)}\n')
        f.write('# Format: channel_id,name,m3u8_url\n')
        for fid, name, url in working_streams:
            f.write(f'{fid},{name},{url}\n')

    print(f"\nGenerated streams.txt with {len(working_streams)} working streams")

if __name__ == "__main__":
    main()
