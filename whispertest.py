import whisper

model = whisper.load_model("small.en")
result = model.transcribe("userAudio.wav")
print(result["text"])