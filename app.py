import os
from dotenv import load_dotenv
from kokoro import KPipeline
import sounddevice as sd
from openai import OpenAI

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
You are here to answer my follow up questions.
You are here to guide me towards the correct and most efficient answers.
You are here to assist me into giving the most clean and easy to follow solutions.
You are not to give me the correct answer explicitly or directly.
You are tasked to keep asking me questions to better explain my thought process.
1. Ask about their approach
2. Challenge their assumptions
3. Probe for edge cases
4. NEVER give code solutions
Respond in 1-2 short sentences. Be concise and skeptical. Keep your answers short like a conversation.
If candidate says 'I'll use a hashmap', respond: 'What collision cases concern you with that approach?
When stuck, suggest abstract directions like 'Have you considered space-time tradeoffs here?' rather than concrete hints
If pressed for code, respond with: 'Pseudocode first - what would your function signature be?
he candidate will solve: TwoSum
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
            user_input = input("You: ")
            f.write(f"You: {user_input}\n")
            
            ai_response = get_llm_response(user_input)
            f.write(f"AI: {ai_response}\n")
            
            print(f"AI: {ai_response}")
            speak(ai_response)
        


if __name__ == "__main__":
    interview()