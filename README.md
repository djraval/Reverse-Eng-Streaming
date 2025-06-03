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

## Implementation

The stream extractor (`stream_extractor.py`) implements the findings documented in [Research.md](Research.md). It automatically discovers channels, extracts working M3U8 URLs, and outputs results to text files.

### Output Files

- **streams.txt** - Contains channel IDs, names, and working M3U8 URLs with signatures
- **logs/*.js** - JavaScript snippets saved for debugging obfuscation patterns


## Research Notes
See [Research.md](Research.md) for technical analysis of URL construction patterns, JavaScript deobfuscation, and P2P network architecture.

## Project Structure

```
├── stream_extractor.py    # Single script implementing research findings
├── streams.txt           # Generated output with working M3U8 URLs
├── logs/                 # JavaScript snippets for debugging
├── requirements.txt      # Dependencies
├── Research.md          # Technical analysis and methodology
└── README.md            # Documentation
```
