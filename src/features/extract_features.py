import librosa
import numpy as np
import torch
from speechbrain.inference.speaker import SpeakerRecognition

# load pretrained model
verification = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="models/speaker_model"
)

def extract_features(file_path):

    # load audio and resample to 16 kHz to match the model
    audio, _ = librosa.load(file_path, sr=16000, mono=True)
    if audio.size == 0:
        raise ValueError("Empty audio signal")
    signal = torch.from_numpy(np.asarray(audio, dtype=np.float32)).unsqueeze(0)

    # extract embedding
    embedding = verification.encode_batch(signal)

    return embedding.numpy()