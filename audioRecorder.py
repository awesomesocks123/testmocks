import pyaudio
import wave
import keyboard
import time
import whisper 

def record(): 
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    OUTPUT_FILENAME = "userAudio.wav"
    TARGET_MIC_INDEX = 1

    audio = pyaudio.PyAudio()
    # for i in range(audio.get_device_count()):
    #     device_info = audio.get_device_info_by_index(i)
    #     if device_info["maxInputChannels"] > 0:  # Only show input devices (microphones)
    #         print(f"ID: {i}, Name: {device_info['name']}, Sample Rate: {device_info['defaultSampleRate']} Hz")


    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True,frames_per_buffer=CHUNK,input_device_index=TARGET_MIC_INDEX)

    frames = []
    print("press space to start recording.")
    keyboard.wait('space')
    print('recording space to stop')
    time.sleep(0.2) 

    while True:
        try:
            data = stream.read(CHUNK)
            frames.append(data)
        except KeyboardInterrupt:
            break
        if keyboard.is_pressed('space'):
            print("stopping recording after a brief delay")
            time.sleep(0.2)
            break
        
    stream.stop_stream()
    stream.close()
    audio.terminate()  

    wf = wave.open(OUTPUT_FILENAME, 'wb')  
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


    model = whisper.load_model("small.en")
    result = model.transcribe("userAudio.wav")
    response = result["text"]
    print(response)
    return response
    
