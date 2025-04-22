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

## API Documentation
The included API provides endpoints for technical analysis:

- `/channels` - Lists available channel identifiers
- `/stream-info/{channel_id}` - Fetches and returns raw stream information (M3U8 URL, token, announce)

## Research Notes
See [Research.md](Research.md) for detailed technical analysis of:
- URL construction patterns
- JavaScript deobfuscation examples
- P2P configuration parameters
- P2P network architecture

## Academic Purpose
This project documents streaming architecture patterns for research and educational purposes.

## Docker Setup

### Prerequisites
- Docker
- Docker Compose
- OPENROUTER_API_KEY (optional, set in .env file for LLM fallback parsing)

### Running with Docker
1. Create a `.env` file (optional):
   ```
   # Optional: For LLM fallback parsing when regular parsing fails
   OPENROUTER_API_KEY=your_api_key_here
   ```

2. Build and start the containers:
   ```bash
   docker compose up --build
   ```

3. Access the API:
   - API Documentation: http://localhost:9000/docs
   - Channels List: http://localhost:9000/channels
   - Stream Info: http://localhost:9000/stream-info/{channel_id}

4. View logs:
   - Real-time logs: `docker compose logs -f stream-api`
   - Log files are stored in the `./logs` directory

### Development
To run in development mode with live reload:
```bash
docker compose up --build stream-api
```
