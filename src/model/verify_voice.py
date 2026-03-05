import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import yaml
from model.profile_manager import load_profile


def load_config():
    with open("configs/config.yaml") as f:
        return yaml.safe_load(f)


def verify_voice(new_embedding):

    config = load_config()

    profile = load_profile()

    if profile is None:
        return False, 0

    score = cosine_similarity(
        [profile],
        [new_embedding]
    )[0][0]

    if score > config["model"]["threshold"]:
        return True, score

    return False, score