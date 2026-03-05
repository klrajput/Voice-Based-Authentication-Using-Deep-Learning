import librosa
import numpy as np

def detect_spoof(audio_file):

    y, sr = librosa.load(audio_file, sr=16000)

    # compute spectral flatness
    flatness = np.mean(librosa.feature.spectral_flatness(y=y))

    # compute zero crossing rate
    zcr = np.mean(librosa.feature.zero_crossing_rate(y))

    # simple heuristic rules
    if flatness > 0.5 or zcr < 0.01:
        return True   # spoof detected

    return False