from gtts import gTTS

def generate_voiceover(text: str, filename="report.mp3"):
    tts = gTTS(text)
    tts.save(filename)
    return filename