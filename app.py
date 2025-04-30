import os
import pyperclip 
from dotenv import load_dotenv
from kokoro import KPipeline
import sounddevice as sd
from openai import OpenAI
import audioRecorder
import scrape

# ===== Configuration =====
load_dotenv()  # Load API keys from .env

# Initialize clients
tts_pipeline = KPipeline(lang_code='a')  # American English
deepseek_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

SYSTEM_PROMPT = """
Consider yourself as a hiring manager, Shoot me potential questions asked during a technical coding interview.
Start off by explaining the question you are giving me.
You are an interviewer for a FAANG company (Amazon).
You are giving me an interview question and I am tasked to solve to this question.
You are helpful but not easily into giving away answers directly.
Speak like you are in a conversation.
This is a conversation and you are speaking.
Keep your responses short 1-2 sentences. 
Be Enthusiastic and helpful 
"""

# ===== State Management =====
conversation_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]
cached_responses = []  # Stores recent AI responses
current_user_input = ""  # Stores the current user input for possible re-recording

# ===== Context Management =====
def load_context_from_file(file_path: str) -> str:
    """Load additional context from a text file"""
    with open(file_path, 'r') as file:
        return file.read()
    
def add_clipboard_to_context():
    """Add clipboard contents to the conversation context"""
    try:
        clipboard_content = pyperclip.paste()
        if clipboard_content.strip():
            add_context_to_history(f"User added from clipboard:\n{clipboard_content}")
            print("\n✓ Clipboard content added to context!")
        else:
            print("\nClipboard is empty!")
    except Exception as e:
        print(f"\nFailed to access clipboard: {e}")

def add_context_to_history(context: str):
    """Add additional context to the conversation history"""
    global conversation_history
    context_message = {
        "role": "system", 
        "content": f"Additional context:\n{context}"
    }
    conversation_history.insert(1, context_message)

# ===== Response Handling =====
def cache_response(response: str):
    """Cache the latest AI response"""
    global cached_responses
    cached_responses.append(response)
    if len(cached_responses) > 5:  # Keep last 5 responses
        cached_responses = cached_responses[-5:]

def get_last_response() -> str:
    """Get the most recent cached response"""
    return cached_responses[-1] if cached_responses else "No cached responses available."

# ===== Recording Functions =====
def record_user_input() -> str:
    """Record user input with option to re-record"""
    global current_user_input
    
    while True:
        print("\nRecording... (Press Ctrl+C to stop)")
        try:
            current_user_input = audioRecorder.record()
            print(f"\nYou recorded: {current_user_input}")
            
            # Ask user if they want to keep or re-record
            while True:  # Inner loop for re-recording decisions
                choice = input("Keep this recording? (y/n/r to replay/listen): ").lower()
                
                if choice == 'y':
                    return current_user_input
                elif choice == 'r':
                    # Play back the recording using TTS
                    print("Playing back your recording...")
                    speak(current_user_input)
                    continue  # Goes back to choice prompt
                elif choice == 'n':
                    print("Re-recording...")
                    break  # Breaks inner loop to start new recording
                else:
                    print("Invalid input. Please enter y/n/r.")
                    continue
                    
        except KeyboardInterrupt:
            print("\nRecording stopped")
            return None  # Or handle this case as you prefer

# ===== Core Functions =====
def get_llm_response(user_input: str) -> str:
    """Send user input to DeepSeek with full history and return AI response."""
    global conversation_history
    
    conversation_history.append({"role": "user", "content": user_input})
    
    response = deepseek_client.chat.completions.create(
        model="deepseek-chat",
        messages=conversation_history,
        stream=False
    )
    
    ai_response = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": ai_response})
    cache_response(ai_response)  # Cache the response
    
    # Limit history length
    if len(conversation_history) > 20:
        conversation_history = [conversation_history[0]] + conversation_history[-19:]
    
    return ai_response

def speak(text: str):
    """Convert text to speech using Kokoro and play it."""
    generator = tts_pipeline(
        text,
        voice='af_heart',
        speed=1.0,
        split_pattern=r'\n+'
    )
    for i, (_, _, audio) in enumerate(generator):
        sd.play(audio, samplerate=24000)
        sd.wait()

# ===== Main Loop =====
def interview():
    # Load additional context from file
    scrape.get_url()
    
    try:
        scraped_problems = load_context_from_file("scraped_problems.txt")
        add_context_to_history(scraped_problems)
        print("Loaded additional context from scraped_problems.txt")
        ai_response = get_llm_response("Introduce yourself and what problem you want me to solve today")
        speak(ai_response)
    except FileNotFoundError:
        print("No scraped_problems.txt found - running without additional context")
    
    with open("interview_log.txt", "a") as f:
        while True:
            print("\nOptions:")
            print("[1] New Response  [2] Replay Last AI")
            print("[3] Show Cache    [4] Add Clipboard to Context")
            print("[5] Exit")
            
            choice = input("Choose an option (1-5): ").strip()
            
            if choice == '1':
                user_input = record_user_input()
                f.write(f"You: {user_input}\n")
                
                ai_response = get_llm_response(user_input)
                clean_text = ai_response.encode("ascii", "ignore").decode()
                f.write(f"AI: {clean_text}\n")
                
                print(f"\nAI: {ai_response}")
                speak(ai_response)
                
            elif choice == '2':
                if cached_responses:
                    last_response = get_last_response()
                    print(f"\nReplaying last AI response: {last_response}")
                    speak(last_response)
                else:
                    print("No cached responses available.")
                    
            elif choice == '3':
                print("\nCached Responses:")
                for i, resp in enumerate(cached_responses, 1):
                    print(f"{i}. {resp[:100]}...")  # Show first 100 chars
                    
            elif choice == '4':
                add_clipboard_to_context()
            elif choice == '5':
                print("Ending interview session.")
                break
                
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    interview()