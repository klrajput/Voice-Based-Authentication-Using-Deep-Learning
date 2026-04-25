import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import yaml
from model.profile_manager import load_profile


# ---------------- CONFIG ----------------

def load_config():
    with open("configs/config.yaml") as f:
        return yaml.safe_load(f)


# ---------------- VERIFY VOICE ----------------

def verify_voice(emb, user_id=None):
    """
    Single-user voice verification using cosine similarity
    """

    profile = load_profile()

    if profile is None:
        return False, 0.0

    # Ensure correct shape
    emb = np.array(emb).squeeze()
    profile = np.array(profile).squeeze()

    emb_2d = emb.reshape(1, -1)
    profile_2d = profile.reshape(1, -1)

    # Cosine similarity
    score = cosine_similarity(emb_2d, profile_2d)[0][0]

    # Load threshold from config (fallback = 0.75)
    config = load_config()
    threshold = config.get("model", {}).get("threshold", 0.75)

    # Final decision
    if score >= threshold:
        return True, float(score)
    else:
        return False, float(score)

