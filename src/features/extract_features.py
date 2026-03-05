import torchaudio
import torch
from speechbrain.inference.speaker import SpeakerRecognition

# load pretrained model
verification = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="models/speaker_model"
)

def extract_features(file_path):

    # load audio
    signal, fs = torchaudio.load(file_path)

    # convert to mono if needed
    if signal.shape[0] > 1:
        signal = torch.mean(signal, dim=0, keepdim=True)

    # extract embedding
    embedding = verification.encode_batch(signal)

    return embedding.squeeze().detach().numpy()