import datetime
import os
import sys
import json
import re
import logging
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from typing import List, Dict, Optional

load_dotenv()
LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
PROXY_URL = os.getenv('PROXY_URL')

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
   logging.warning("OPENROUTER_API_KEY environment variable not set. LLM parsing fallback will not be available.")

logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Stream API")

def load_config():
    try:
        with open('channels.json') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading config: {e}")
        return None

def build_url(config, channel_id):
    url_config = config['urls']
    return url_config['format'].format(
        base=url_config['base'],
        player=url_config['player'],
        channel_id=channel_id
    )

config = load_config()

if config is None or 'channels' not in config or 'urls' not in config:
    logger.error("CRITICAL: Failed to load configuration or 'channels'/'urls' key missing in channels.json.")
    sys.exit(1) # Exit if essential config is missing

possible_channel_names = list(config['channels'].keys())


def parse_stream_info_using_openrouter(api_key: Optional[str], html_content: str, model="google/gemini-2.5-flash-preview:thinking"):
    """Parses stream info from the HTML content using OpenRouter API.

    Args:
        api_key: The OpenRouter API key. If None, the function will return None.
        html_content: The HTML content to parse.
        model: The model to use for parsing.

    Returns:
        A dictionary with the parsed stream info, or None if the API key is not provided.
    """
    if not api_key:
        logger.warning("Cannot use OpenRouter API: No API key provided")
        return None

    url = "https://openrouter.ai/api/v1/chat/completions"

    system_prompt = """
    You are an expert web scraper specializing in extracting video stream details from complex HTML and JavaScript. Your task is to analyze the provided HTML content. Pay close attention to the JavaScript sections, especially those configuring a video player (e.g., Clappr) and potentially a P2P HLS engine (e.g., SwarmCloud/P2PEngineHls).

    Identify and extract the following specific values:
    1.  **`url`**: The *effective* M3U8 stream URL that the player is configured to load. This might be constructed dynamically or obfuscated (e.g., using `join()` on character arrays, concatenating variables, or returned by a function). Ensure you resolve these to get the final URL string.
    2.  **`token`**: The P2P token, typically found within a configuration object (often named `p2pConfig` or similar) used by the P2P engine. This is often a short alphanumeric string.
    3.  **`announce`**: The URL of the P2P announce server (tracker), also usually found in the P2P configuration object alongside the token.

    **Constraints:**
    *   Focus *only* on the values used for player/P2P initialization. Ignore unrelated URLs or strings.
    *   De-obfuscate simple JavaScript constructions (like array joins) to get the final values.
    *   The `token` and `announce` fields might not be present if P2P is not used or configured; handle this according to the required JSON schema (return null or omit if not found, based on schema strictness).
    *   Provide the output strictly following the specified JSON schema with keys 'url', 'token', and 'announce'.
    """

    query = f"""
    Analyze the following HTML content and extract the stream details as specified in the system prompt:

    ```html
    {html_content}
    ```
    """

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ],
        "temperature": 0,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "iptv_stream_details",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "The extracted m3u8 URL."},
                        "token": {"type": "string", "description": "The P2P token (optional)."},
                        "announce": {"type": "string", "description": "The P2P announce server URL (optional)."}
                    },
                    "required": ["url"],
                    "additionalProperties": False,
                },
            },
        },
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        content_str = data["choices"][0]["message"]["content"]
        return json.loads(content_str)
    except Exception as e:
        logger.error(f"Error using OpenRouter API: {str(e)}")
        return None

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
            logger.debug("Found the first relevant script tag.")
            relevant_script_text = script_text
            break # Stop searching once the first relevant script is found

    # 2. If no relevant script was found, exit
    if not relevant_script_text:
        logger.error("Could not find any script tag matching all relevant keywords.")
        return None

    # 3. Attempt extraction on the found script
    # Regex to find an array [...] followed immediately by .join("")
    array_pattern = re.compile(r'\[(.*?)\]\s*\.\s*join\s*\(\s*""\s*\)')
    match = array_pattern.search(relevant_script_text)

    if not match:
        # If the first attempt fails, maybe the array *does* span lines, try with DOTALL again
        # This adds a fallback, still minimal change overall
        logger.debug("Initial array.join pattern failed, trying with re.DOTALL...")
        array_pattern_dotall = re.compile(r'\[(.*?)\]\s*\.\s*join\s*\(\s*""\s*\)', re.DOTALL)
        match = array_pattern_dotall.search(relevant_script_text)
        if not match:
             logger.error("Relevant script found, but the array.join(\"\") pattern was not matched within it (tried with and without DOTALL).")
             return None

    logger.debug("Found array.join(\"\") pattern in the relevant script.")
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
            logger.warning("Parsed character array was empty.")
            # Log the problematic content for inspection
            logger.debug(f"Problematic raw array content: {array_content[:500]}...")
            return None

        stream_url = "".join(chars)

        # 5. Validate the result
        if stream_url.startswith("http") and ".m3u8" in stream_url:
             logger.info("Successfully constructed URL from array.")
             return stream_url
        else:
             # Log the invalid constructed URL and the raw content it came from
             logger.warning(f"Constructed string doesn't look like m3u8 URL: {stream_url[:100]}...")
             logger.debug(f"Failed validation. Raw array content: {array_content[:500]}...")
             return None

    except Exception as e:
        logger.error(f"Error processing extracted array content: {e}")
        logger.debug(f"Problematic raw array content: {array_content[:500]}...")
        return None



@app.get("/channels", response_model=List[str])
async def list_channels():
    """List all available channels"""
    logger.info("Returning list of available channels")
    return possible_channel_names


@app.get("/stream-info/{channel_id}", response_model=Dict[str, str])
async def get_stream_info(channel_id: str):
    """Get raw stream information for a specific channel (M3U8 URL)"""
    logger.info(f"Processing stream info request for channel: {channel_id}")

    if channel_id not in possible_channel_names:
        logger.warning(f"Invalid channel requested: {channel_id}")
        raise HTTPException(status_code=404, detail="Channel not found")

    url = build_url(config, channel_id)
    # Not necessary but still using the headers to emulate a browser request
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
        logger.info(f"Fetching stream data from: {url}")
        response = requests.get(url, headers=headers, timeout=15, proxies={"http": PROXY_URL, "https": PROXY_URL})
        response.raise_for_status()
        stream_url = parse_stream_info_no_llm(response.text)
        if not stream_url:
            # Save the HTML content for debugging
            with open(f"app/logs/failed_html_{channel_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.html", "w", encoding='utf-8') as f:
                f.write(response.text)

            if API_KEY:
                logger.debug("Failed to parse stream info. HTML content saved for debugging. Trying OpenRouter API...")
                stream_info_json = parse_stream_info_using_openrouter(API_KEY, response.text)
                if stream_info_json and (stream_url := stream_info_json.get("url")):
                    logger.info("Successfully extracted stream URL using OpenRouter API")
                else:
                    logger.error("Failed to extract stream URL using OpenRouter API")
                    raise HTTPException(status_code=500, detail="Failed to extract stream URL")
            else:
                logger.error("Failed to parse stream info and OpenRouter API key is not available")
                raise HTTPException(status_code=500, detail="Failed to extract stream URL and LLM fallback is not available")

        # Clean and normalize the URL
        cleaned_url = re.sub(r'(?<!:)//+', '/', stream_url)
        if not cleaned_url.startswith(('http://', 'https://')):
            cleaned_url = f"https://{cleaned_url}"
        logger.debug(f"Cleaned URL: {cleaned_url}")
        logger.info(f"Successfully processed stream info for channel: {channel_id}")
        return {
            "url": cleaned_url
        }

    except requests.Timeout:
        logger.error(f"Timeout while fetching stream for channel: {channel_id}")
        raise HTTPException(status_code=504, detail="Gateway timeout")
    except (requests.RequestException, ValueError, json.JSONDecodeError) as e:
        logger.error(f"Error processing stream for channel {channel_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/play/{channel_id}.m3u8")
async def get_m3u8_content(channel_id: str):
    """Get direct M3U8 content for a channel"""
    logger.info(f"Processing M3U8 request for channel: {channel_id}")

    if channel_id not in possible_channel_names:
        logger.warning(f"Invalid channel requested: {channel_id}")
        raise HTTPException(status_code=404, detail="Channel not found")
    try:
        # Get stream info first
        stream_info = await get_stream_info(channel_id)
        m3u8_url = stream_info["url"]
        logger.debug(f"Got M3U8 URL: {m3u8_url}")
        logger.info(f"Fetching M3U8 content from: {m3u8_url} using warp proxy")
        response = requests.get(m3u8_url, headers={}, proxies={"http": PROXY_URL, "https": PROXY_URL}, timeout=15)
        response.raise_for_status()

        return Response(
            content=response.content
        )

    except Exception as e:
        logger.error(f"Error fetching M3U8 content for channel {channel_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    logger.info(f"Starting Stream API")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)

if __name__ == "__main__":
    main()
