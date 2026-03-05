import librosa
import noisereduce as nr
import soundfile as sf
import yaml
import uuid

def load_config():
    with open("configs/config.yaml") as f:
        return yaml.safe_load(f)

def preprocess_audio(file_path):

    config = load_config()

    audio, sr = librosa.load(file_path, sr=16000)

    reduced_noise = nr.reduce_noise(y=audio, sr=sr)

    output_file = f"{config['paths']['processed_audio']}/{uuid.uuid4()}.wav"

    sf.write(output_file, reduced_noise, sr)

    return output_file