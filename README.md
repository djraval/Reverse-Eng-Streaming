# Stream Architecture Analysis
A research project analyzing the technical architecture of CrichD's streaming infrastructure.

## Disclaimer
This project is purely for academic research and educational purposes. As a software engineer passionate about reverse engineering web applications, I created this project to study and document interesting streaming architecture patterns from a technical perspective. The analysis explores how modern web streaming platforms implement features like dynamic content delivery, P2P networking, and token-based authentication.

The code and documentation provided here are meant for learning about:
- Video streaming technologies
- Network protocols
- Web architecture patterns
- JavaScript deobfuscation techniques
- Modern player implementations

**Important Notes:**
- This is an experimental project intended for academic study only
- The authors do not condone or encourage any unauthorized access or copyright infringement
- This research should only be used to understand streaming technologies in legal and authorized contexts
- No actual stream content is hosted or distributed by this project
- The focus is purely on understanding the technical implementation details of web streaming architectures

## Technical Components Analyzed
1. Stream Source Discovery
   - Initial channel page (crichdplayer.com)
   - Embedded iframe chain
   - PHP endpoint resolution

2. Player Architecture
   - Clappr player implementation
   - P2P integration (SwarmCloud/P2PEngineHls)
   - Stream URL construction

3. Security Mechanisms
   - JavaScript obfuscation patterns
   - Token generation
   - URL expiration implementation

## Usage

### Stream URL Extraction
```bash
python main.py list                    # List available channels
python main.py get <channel_id>        # Extract stream URL
python main.py                         # Show help
```

### Channel Discovery & Updates
```bash
python discover.py                    # Discover channels, test them, and update channels.txt
```

### Sample Output
```bash
$ python main.py list
Available channels:
  - starhindi
  - skyscric
  - willowusa
  - star1in

$ python main.py get starhindi
Fetching stream data for starhindi...
Stream URL for starhindi:
https://off1.gogohaalmal.com:1686/hls/starhindi.m3u8?md5=hLeV65QPS37_MYtux7X1Ug&expires=1748824542

$ python discover.py
Testing 45 discovered channels for M3U8 generation...
[1/45] asportshd: WORKING
[2/45] bbtsp2: WORKING
[3/45] hdchnl8: NOT WORKING
[4/45] skysact: NO M3U8 (skipped)
...
Generated channels.txt with 25 working channels
```

## Setup

```bash
pip install -r requirements.txt
python main.py list
```

Channel configuration in `channels.txt` (simple CSV format):
```csv
starhindi,"Star Sports 1 Hindi"
willowusa,"Willow Cricket HD"
asportshd,"A Sports HD"
bbtsp2,"TNT Sports 2"
```

Use `python discover.py` to automatically discover and update all available channels. Only working channels are included in the output.

## Research Notes
See [Research.md](Research.md) for technical analysis of URL construction patterns, JavaScript deobfuscation, and P2P network architecture.

## Testing

The discovery script includes live stream validation:

- **Channel discovery** - Crawls website for channel links
- **Stream URL extraction** - Parses JavaScript to find M3U8 URLs
- **Live stream validation** - Fetches actual M3U8 content to verify working streams
- **Automatic filtering** - Only includes channels that generate valid M3U8 content

## Project Structure

```
├── main.py                 # Main application - stream URL extraction
├── discover.py            # Channel discovery with live testing
├── channels.txt           # Channel list (working channels only)
├── requirements.txt       # Dependencies
├── Research.md           # Technical analysis
└── README.md             # Documentation
```
