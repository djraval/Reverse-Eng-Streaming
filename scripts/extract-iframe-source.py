import json
import requests
import re
from bs4 import BeautifulSoup

with open('channels.json') as f:
    data = json.load(f)

channels = data["channels"]

def extract_iframe_src(page_url):
    resp = requests.get(page_url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    scripts = soup.find_all('script')

    for script in scripts:
        if script.string and 'embeds[0]' in script.string:
            m = re.search(r"embeds\[0\]\s*=\s*'(<iframe[^']+)';", script.string)
            if m:
                iframe_html = m.group(1)
                iframe_src = re.search(r'src="([^"]+)"', iframe_html)
                if iframe_src:
                    src = iframe_src.group(1)
                    return 'https:' + src if src.startswith('//') else src
    return None

for key, channel in channels.items():
    if "source" not in channel and "webpage" in channel:
        src = extract_iframe_src(channel["webpage"])
        if src:
            channel["source"] = src
            print(f"Filled source for {channel['name']}: {src}")

with open('channels.json', 'w') as f:
    json.dump(data, f, indent=4)