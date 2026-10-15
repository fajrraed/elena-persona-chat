# Elena AI Chatbot

A Python chatbot utilizing the Groq Cloud API. It features a persistent local memory architecture that tracks user context, nicknames, and choices via a JSON file. The system optimizes API response speeds by managing history length and includes automatic model fallback logic.

## Features
- Immersive custom AI persona configuration.
- Local memory tracking saved in mommy_memory.json.
- Automatic context limits for optimal API speeds.
- Fallback logic handling transitions between model endpoints.

## Requirements
Install the official Groq client library:
```bash
pip install groq
```

## Setup Instructions
1. Download the repository source files.
2. Open main.py and input your API key from the Groq Cloud Console:
   ```python
   GROQ_API_KEY = "your_actual_api_key_here"
   ```
3. Run the script:
   ```bash
   python main.py
   ```

## License
This project is open for educational and personal modification purposes.
