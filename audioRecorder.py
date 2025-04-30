import pyaudio
import wave
import keyboard
import time
import whisper


model = whisper.load_model("small.en")  

def record():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100  
    CHUNK = 1024
    OUTPUT_FILENAME = "userAudio.wav"
    TARGET_MIC_INDEX = 1  

    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK,
        input_device_index=TARGET_MIC_INDEX
    )

    frames = []
    print("Press SPACE to start recording...")
    keyboard.wait('space')
    print("Recording... (Press SPACE to stop)")
    time.sleep(0.2)

    while True:
        try:
            data = stream.read(CHUNK)
            frames.append(data)
            if keyboard.is_pressed('space'):
                print("Stopping...")
                time.sleep(0.2)
                break
        except KeyboardInterrupt:
            break

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    result = model.transcribe(OUTPUT_FILENAME)
    return result["text"]