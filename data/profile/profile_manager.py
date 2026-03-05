import numpy as np
import os

PROFILE_PATH = "data/profile/user_profile.npy"
EMBEDDINGS_PATH = "data/embeddings"


def update_profile():

    embeddings = []

    for file in os.listdir(EMBEDDINGS_PATH):

        if file.endswith(".npy"):
            emb = np.load(f"{EMBEDDINGS_PATH}/{file}")
            embeddings.append(emb)

    if len(embeddings) == 0:
        return None

    profile = np.mean(embeddings, axis=0)

    np.save(PROFILE_PATH, profile)

    return profile


def load_profile():

    if not os.path.exists(PROFILE_PATH):
        return None

    return np.load(PROFILE_PATH)