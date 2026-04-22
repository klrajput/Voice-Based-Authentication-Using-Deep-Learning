import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import yaml
import json
from model.profile_manager import load_profile
from model.ecapa_classifier import ECAPAClassifier

classifier = ECAPAClassifier(num_speakers=51)


def load_speaker_map():
    try:
        with open("data/profile/speaker_map.json") as f:
            return json.load(f)
    except:
        return {}


def load_config():
    with open("configs/config.yaml") as f:
        return yaml.safe_load(f)


def verify_voice(emb, user_id):
    profile = load_profile()

    if profile is None:
        return False, 0.0

    # 🔥 FIX SHAPE
    emb = np.array(emb).squeeze()
    profile = np.array(profile).squeeze()

    emb_2d = emb.reshape(1, -1)
    profile_2d = profile.reshape(1, -1)

    speaker_map = load_speaker_map()
    expected_speaker = speaker_map.get(str(user_id))
    predicted_speaker = classifier.predict(emb)

    # cosine similarity
    score = cosine_similarity(emb_2d, profile_2d)[0][0]

    # 🔥 classifier prediction
    predicted_speaker = classifier.predict(emb)

    if score > 0.75 and predicted_speaker == expected_speaker:
        return True, score
    else:
        return False, score