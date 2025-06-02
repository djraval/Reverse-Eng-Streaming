#!/usr/bin/env python3
"""
Test suite for streaming URL extraction.
"""

import time
import requests

from main import get_stream_url, list_channels, parse_stream_info_no_llm


def test_javascript_parsing():
    """Test core JavaScript parsing"""
    html = '''<script>
    var p2pConfig = { live: true };
    var player = new Clappr.Player({ autoPlay: true });
    P2PEngineHls.tryRegisterServiceWorker(p2pConfig).then(() => {
        player.load({
            source: ["h","t","t","p","s",":","\\/","\\/","t","e","s","t",".","c","o","m","\\/","s","t","r","e","a","m",".","m","3","u","8"].join("")
        });
    });
    </script>'''
    result = parse_stream_info_no_llm(html)
    expected = "https://test.com/stream.m3u8"

    if result == expected:
        print("✓ JavaScript parsing test passed")
        return True
    else:
        print(f"✗ JavaScript parsing test failed: expected '{expected}', got '{result}'")
        return False


def test_all_channels():
    """Test all channels and validate M3U8 content"""
    print(f"[{time.strftime('%H:%M:%S')}] Testing channels...")

    channels = list_channels()
    if not channels:
        print("ERROR: No channels configured")
        return False

    success_count = 0
    for channel in channels:
        try:
            url = get_stream_url(channel)
            if not url or not url.startswith('http') or '.m3u8' not in url:
                print(f"FAIL {channel}: Invalid URL")
                continue

            # Validate M3U8 content
            response = requests.get(url, timeout=10)
            content = response.text.strip()

            if content.startswith('#EXTM3U') and '#EXT-X-TARGETDURATION' in content:
                segments = sum(1 for line in content.split('\n') if line.strip() and not line.startswith('#'))
                print(f"PASS {channel}: {segments} segments")
                success_count += 1
            else:
                print(f"FAIL {channel}: Invalid M3U8")

        except Exception as e:
            print(f"FAIL {channel}: {e}")

    success_rate = (success_count / len(channels)) * 100
    print(f"\nResult: {success_count}/{len(channels)} channels working ({success_rate:.0f}%)")
    return success_rate >= 50  # 50% threshold


if __name__ == "__main__":
    print("Stream URL Extraction Tests")
    print("="*30)

    # Run JavaScript parsing test
    parsing_success = test_javascript_parsing()

    if parsing_success:
        print()
        test_all_channels()
    else:
        print("Skipping channel tests due to parsing test failure")
