import os
import librosa
import noisereduce as nr
import soundfile as sf
import yaml
import uuid
import numpy as np


def load_config():
    with open("configs/config.yaml") as f:
        return yaml.safe_load(f)


def preprocess_audio(file_path):

    config = load_config()

    # Load audio
    audio, sr = librosa.load(file_path, sr=16000)

    # Noise reduction
    reduced_noise = nr.reduce_noise(y=audio, sr=sr)

    # ✅ FIX 1: ensure correct dtype
    reduced_noise = np.asarray(reduced_noise, dtype=np.float32)

    # ✅ FIX 2: ensure directory exists
    output_dir = config["paths"]["processed_audio"]
    os.makedirs(output_dir, exist_ok=True)

    # ✅ FIX 3: proper filename
    output_file = os.path.join(output_dir, f"{uuid.uuid4()}.wav")

    # ✅ FIX 4: explicitly set format
    sf.write(output_file, reduced_noise, sr, format='WAV')

    return output_file