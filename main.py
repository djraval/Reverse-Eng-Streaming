import json
import re
import sys
from bs4 import BeautifulSoup
import requests
from typing import Optional

def load_config():
    try:
        with open('channels.json') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config: {e}")
        return None

def build_url(config, channel_id):
    url_config = config['urls']
    return url_config['format'].format(
        base=url_config['base'],
        player=url_config['player'],
        channel_id=channel_id
    )

def parse_stream_info_no_llm(html_content: str) -> Optional[str]:
    soup = BeautifulSoup(html_content, 'html.parser')
    scripts = soup.find_all('script')
    relevant_script_text = None
    # Keywords to find the script block
    relevant_keywords = ["P2PEngineHls", "p2pConfig", "Clappr.Player", ".join(\"\")"]

    # 1. Find the first relevant script block
    for script in scripts:
        script_text = script.text
        if script_text and all(keyword in script_text for keyword in relevant_keywords):
            relevant_script_text = script_text
            break # Stop searching once the first relevant script is found

    # 2. If no relevant script was found, exit
    if not relevant_script_text:
        return None

    # 3. Attempt extraction on the found script
    # Regex to find an array [...] followed immediately by .join("")
    array_pattern = re.compile(r'\[(.*?)\]\s*\.\s*join\s*\(\s*""\s*\)')
    match = array_pattern.search(relevant_script_text)

    if not match:
        # If the first attempt fails, maybe the array *does* span lines, try with DOTALL again
        array_pattern_dotall = re.compile(r'\[(.*?)\]\s*\.\s*join\s*\(\s*""\s*\)', re.DOTALL)
        match = array_pattern_dotall.search(relevant_script_text)
        if not match:
             return None

    array_content = match.group(1) # Get the content inside [...]

    # 4. Process the extracted array content
    try:
        # Split by comma, strip quotes/whitespace, handle escaped slashes
        chars = [
            c.strip().strip('"\'').replace('\\/', '/')
            for c in array_content.split(',')
            if c.strip() # Ensure not empty after stripping
        ]

        if not chars:
            return None

        stream_url = "".join(chars)

        # 5. Validate the result
        if stream_url.startswith("http") and ".m3u8" in stream_url:
             return stream_url
        else:
             return None

    except Exception as e:
        return None

def get_stream_url(channel_id):
    """Get stream URL for a specific channel"""
    config = load_config()
    
    if config is None or 'channels' not in config or 'urls' not in config:
        print("CRITICAL: Failed to load configuration or 'channels'/'urls' key missing in channels.json.")
        return None
    
    possible_channel_names = list(config['channels'].keys())
    
    if channel_id not in possible_channel_names:
        print(f"Invalid channel: {channel_id}. Available channels: {', '.join(possible_channel_names)}")
        return None

    url = build_url(config, channel_id)
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

    try:
        print(f"Fetching stream data for {channel_id}...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        stream_url = parse_stream_info_no_llm(response.text)
        if not stream_url:
            print("Failed to parse stream info using basic method")
            return None

        # Clean and normalize the URL
        cleaned_url = re.sub(r'(?<!:)//+', '/', stream_url)
        if not cleaned_url.startswith(('http://', 'https://')):
            cleaned_url = f"https://{cleaned_url}"

        return cleaned_url

    except Exception as e:
        print(f"Error getting stream for {channel_id}: {e}")
        return None

def list_channels():
    """List all available channels"""
    config = load_config()
    if config and 'channels' in config:
        return list(config['channels'].keys())
    return []

def main():
    """Main function to handle command line arguments"""
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [channel_id]")
        print("Commands:")
        print("  list                    - List all available channels")
        print("  get <channel_id>        - Get stream URL for a specific channel")
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        channels = list_channels()
        if channels:
            print("Available channels:")
            for channel in channels:
                print(f"  - {channel}")
        else:
            print("No channels available or config file not found")
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("Error: Please specify a channel ID")
            print("Usage: python main.py get <channel_id>")
            return
        
        channel_id = sys.argv[2]
        stream_url = get_stream_url(channel_id)
        
        if stream_url:
            print(f"Stream URL for {channel_id}:")
            print(stream_url)
        else:
            print(f"Failed to get stream URL for {channel_id}")
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: list, get")

if __name__ == "__main__":
    main()
