import sounddevice as sd
from scipy.io.wavfile import write
import uuid
import yaml

def load_config():
    with open("configs/config.yaml") as f:
        return yaml.safe_load(f)

def record_voice():

    config = load_config()

    duration = config["audio"]["duration"]
    fs = config["audio"]["sample_rate"]

    filename = f"{config['paths']['raw_audio']}/{uuid.uuid4()}.wav"

    print("Speak now...")

    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()

    write(filename, fs, recording)

    print("Saved:", filename)

    return filename