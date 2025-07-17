# Interview Mocker

A combined application that integrates a Python backend with an Electron frontend to create an AI-powered technical interview practice tool.

## Features

- Submit LeetCode problem URLs to set up interview context
- Record audio responses to interview questions
- Get AI-powered feedback from a simulated interviewer
- Add code from clipboard to the interview context
- Replay previous AI responses

## Setup

### Prerequisites

- Python 3.8+ with pip
- Node.js and npm
- Git (optional)

### Backend Dependencies

```bash
pip install flask flask-cors openai pyperclip sounddevice whisper kokoro
```

### Frontend Dependencies

```bash
cd electron-app
npm install
```

## Running the Application

You can run both the backend and frontend together using the start script:

```bash
python start_app.py
```

Or run them separately:

### Backend

```bash
python api.py
```

### Frontend

```bash
cd electron-app
npm run dev
```

## How to Use

1. Start the application using `python start_app.py`
2. Enter a LeetCode problem URL in the input field and click "Submit"
3. The AI interviewer will introduce the problem
4. Use the "Record Response" button to answer interview questions
5. Use "Replay Last" to hear the last AI response again
6. Use "Add Clipboard" to add code from your clipboard to the interview context
7. Use "New Problem" to start with a different LeetCode problem

## Architecture

- **Backend**: Flask API that handles audio recording, transcription, and AI responses
- **Frontend**: Electron app with React that provides a user interface for the interview experience
- **Communication**: The frontend communicates with the backend via HTTP requests

## Files

- `api.py`: Flask API for the backend
- `app.py`: Original Python backend logic
- `audioRecorder.py`: Audio recording and transcription functionality
- `scrape.py`: LeetCode problem scraping functionality
- `start_app.py`: Script to run both backend and frontend together
