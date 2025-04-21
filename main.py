import os
import sys
import json
import re
import logging
from dotenv import load_dotenv
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict

load_dotenv()
PORT = int(os.getenv('PORT', 9000))

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
   logging.error("CRITICAL: OPENROUTER_API_KEY environment variable not set.")
   sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Stream Architecture Analysis API")

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


def fetch_stream_info(api_key: str, html_content: str, model="google/gemini-2.5-flash-preview"):
    """Fetches stream info from OpenRouter API."""
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
    response = requests.post(url, headers=headers, json=payload, timeout=20)
    response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
    data = response.json()
    content_str = data["choices"][0]["message"]["content"]
    return json.loads(content_str)


@app.get("/channels", response_model=List[str])
async def list_channels():
    """List all available channels"""
    logger.info("Returning list of available channels")
    return possible_channel_names

@app.get("/stream/{channel}", response_model=Dict)
async def get_stream(channel: str):
    """Get stream information for a specific channel"""
    logger.info(f"Processing request for channel: {channel}")
    
    if channel not in possible_channel_names:
        logger.warning(f"Invalid channel requested: {channel}")
        raise HTTPException(status_code=404, detail="Channel not found")
    
    url = build_url(config, channel)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': "https://stream.crichd.sc/"
    }

    try:
        logger.info(f"Fetching stream data from: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        html_content = response.text
        
        logger.info("Processing stream information")
        stream_info_json = fetch_stream_info(API_KEY, html_content)
        extracted_url = stream_info_json.get("url")
        if extracted_url: # Ensure URL exists before processing
             extracted_url = re.sub(r'(https?://)/+', r'\1', extracted_url)
             stream_info_json["url"] = extracted_url
        else:
            logger.warning(f"No 'url' found in stream info for channel: {channel}")
            raise HTTPException(status_code=500, detail="Analysis service failed to return a stream URL")
        
        logger.info(f"Successfully processed stream for channel: {channel}")
        return stream_info_json
        
    except requests.Timeout as e:
        # Specific handling for timeouts (could be initial fetch or OpenRouter)
        logger.error(f"Timeout during request for {channel}: {str(e)}")
        raise HTTPException(status_code=504, detail="Gateway timeout") # 504 might be suitable for timeout
    except requests.RequestException as e:
        # Handles connection errors, HTTP errors, etc. from both requests.get and fetch_stream_info
        logger.error(f"Request error processing {channel}: {str(e)}")
        # Check if it's an HTTP error from OpenRouter to return 502, otherwise maybe 500 or 502
        status_code = 502 if isinstance(e, requests.HTTPError) else 500
        detail = f"Error communicating with upstream service: {str(e)}" if status_code == 502 else f"Request failed: {str(e)}"
        raise HTTPException(status_code=status_code, detail=detail)
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        # Errors during JSON parsing or accessing expected keys/indices in OpenRouter response
        logger.error(f"Error parsing stream info for {channel}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to parse stream information")
    except Exception as e: # Catch-all
        logger.exception(f"Unexpected error processing {channel}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def main():
    logger.info(f"Starting Stream Architecture Analysis API on port {PORT}")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()
