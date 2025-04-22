import os
from dotenv import load_dotenv
from kokoro import KPipeline
import sounddevice as sd
from openai import OpenAI
import audioRecorder

# ===== Configuration =====
load_dotenv()  # Load API keys from .env

# Initialize clients ONCE (avoid reinitializing in loops)
tts_pipeline = KPipeline(lang_code='a')  # American English
deepseek_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

SYSTEM_PROMPT = """
You are an interviewer for a FAANG company (Amazon).

You are giving me an interview question and I am tasked to solve to this question.
You are helpful but not easily into giving away answers directly.
Speak like you are in a conversation.
Keep your responses short 1-2 sentences. 
Be Enthusiastic and helpful 
Also its good to start off and introduce yourself 
"""

# ===== Core Functions =====
def get_llm_response(user_input: str) -> str:
    """Send user input to DeepSeek and return AI response."""
    response = deepseek_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT },
            {"role": "user", "content": user_input },
        ],
        stream=False
    )
    return response.choices[0].message.content





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
    with open("interview_log.txt", "a") as f:  # Appends to file
        while True:
            user_input = audioRecorder.record()
            f.write(f"You: {user_input}\n")
            
            ai_response = get_llm_response(user_input)
            clean_text = ai_response.encode("ascii", "ignore").decode() 
            f.write(f"AI: {clean_text}\n")
            
            print(f"AI: {ai_response}")
            speak(ai_response)
        


if __name__ == "__main__":
    interview()