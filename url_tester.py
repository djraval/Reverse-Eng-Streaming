import requests
from urllib.parse import urlparse, urlunparse

STREAMS_FILE = "streams.txt"
ALTERNATIVE_NETLOCS = [
    "pol5.dunyapurkaraja.com:999",
    "pol6.dunyapurkaraja.com:999",
    "pol7.dunyapurkaraja.com:999",
    "m1.merichunidya.com:999",
    "m2.merichunidya.com:999",
    "m3.merichunidya.com:999",
    "m4.merichunidya.com:999",
    "m7.merichunidya.com:999"
]

# Suppress InsecureRequestWarning for verify=False in requests.head
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

print(f"Reading M3U8 URLs from {STREAMS_FILE}...")
urls_from_file = []
try:
    with open(STREAMS_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(',')
            if len(parts) >= 3:
                urls_from_file.append(parts[2].strip())
except FileNotFoundError:
    print(f"Error: File '{STREAMS_FILE}' not found.")
    exit()
except Exception as e:
    print(f"Error reading file '{STREAMS_FILE}': {e}")
    exit()

if not urls_from_file:
    print(f"No M3U8 URLs found in {STREAMS_FILE} to test.")
    exit()

print(f"Found {len(urls_from_file)} URLs to process.")

for i, current_url in enumerate(urls_from_file):
    print(f"\n\n--- Processing URL {i + 1}/{len(urls_from_file)}: {current_url} ---")

    # 1. Test the original URL from the file
    print(f"\nTesting original: {current_url}")
    try:
        response = requests.head(current_url, timeout=5, verify=False)
        print(f"SUCCESS: {current_url} - Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"FAILED: {current_url} - Error: {e}")

    # 2. Test variations with alternative hostnames
    try:
        parsed_original = urlparse(current_url)
        original_scheme = parsed_original.scheme
        original_path = parsed_original.path
        original_query = parsed_original.query

        if not original_scheme or not original_path:
            print(f"Warning: Could not properly parse components from: {current_url}. Skipping alternatives.")
            continue
    except Exception as parse_error:
        print(f"Warning: Error parsing URL {current_url}: {parse_error}. Skipping alternatives.")
        continue
        
    print(f"\nAttempting alternative hostnames for path '{original_path}' (scheme: {original_scheme})...")
    for alt_netloc in ALTERNATIVE_NETLOCS:
        new_url_parts = (original_scheme, alt_netloc, original_path, '', original_query, '')
        alternative_url = urlunparse(new_url_parts)

        if alternative_url == current_url:
            # print(f"Skipping re-test of identical URL: {alternative_url}") # Optional: uncomment for verbosity
            continue

        print(f"\nTesting alternative: {alternative_url}")
        try:
            response = requests.head(alternative_url, timeout=5, verify=False)
            print(f"SUCCESS: {alternative_url} - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"FAILED: {alternative_url} - Error: {e}")

print("\n\n--- Script finished ---")
