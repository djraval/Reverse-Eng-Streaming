# Stream Architecture Analysis
A research project analyzing the technical architecture of CrichD's streaming infrastructure.

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
- `/stream/{channel}` - Analyzes stream construction for specified channel

## Research Notes
See [Research.md](Research.md) for detailed technical analysis of:
- URL construction patterns
- JavaScript deobfuscation examples
- P2P configuration parameters

## Academic Purpose
This project documents streaming architecture patterns for research and educational purposes.

## Docker Setup

### Prerequisites
- Docker
- Docker Compose
- OPENROUTER_API_KEY (set in .env file)

### Running with Docker
1. Create a `.env` file with your OPENROUTER_API_KEY:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```

2. Build and start the containers:
   ```bash
   docker compose up --build
   ```

3. Access the API:
   - API Documentation: http://localhost:9000/docs
   - Channels List: http://localhost:9000/channels
   - Stream Info: http://localhost:9000/stream/{channel}

4. View logs:
   - Real-time logs: `docker compose logs -f stream-analysis`
   - Log files are stored in the `./logs` directory

### Development
To run in development mode with live reload:
```bash
docker compose up --build stream-analysis
```
