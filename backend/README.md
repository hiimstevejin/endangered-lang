# Setup

To create virtual environment and download dependencies:

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

To run the application:

```
fastapi dev main.py
```

## Feature 1

Reference
https://www.youtube.com/watch?v=kDPzdyX76cg&t=1260s

Processing Audio Input / Output with voice agent
I chose Sandwich structure which works as follows

User Input -> Voice audio detection model -> Speech to Text model -> agent -> Text to Speech -> Output Audio

```
├── backend/
│   ├── app/
│   │   ├── services/
│   │   │   ├── stt.py     # Put Whisper logic here
│   │   │   ├── agent.py   # Put LangChain logichere
│   │   │   └── tts.py     # Put OpenAI TTS logic here
│   │   └── main.py        # WebSocket & API routes
│   └── .env               # API Keys
```

This is the structure of backend directory and _Voice audio detection model is often embedded in the stt model_ so I will skip it for now.
