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

```bash
python main.py list                    # List available channels
python main.py get <channel_id>        # Extract stream URL
python main.py                         # Show help
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
```

## Setup

```bash
pip install -r requirements.txt
python main.py list
```

Channel configuration in `channels.json`.

## Research Notes
See [Research.md](Research.md) for technical analysis of URL construction patterns, JavaScript deobfuscation, and P2P network architecture.

## Project Structure

```
├── main.py              # Main application
├── channels.json        # Channel configuration
├── requirements.txt     # Dependencies
├── Research.md         # Technical analysis
└── README.md           # Documentation
```
