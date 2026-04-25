
import numpy as np
import uuid
import yaml
import os
from model.profile_manager import update_profile


# ---------------- CONFIG ----------------

def load_config():
    with open("configs/config.yaml") as f:
        return yaml.safe_load(f)


# ---------------- SAVE EMBEDDING ----------------

def save_embedding(embedding, update=True):
    """
    Save embedding and optionally update profile

    Args:
        embedding: numpy array (voice embedding)
        update: whether to recompute profile immediately
    """

    config = load_config()
    path = config["paths"]["embeddings"]

    os.makedirs(path, exist_ok=True)

    filename = os.path.join(path, f"{uuid.uuid4()}.npy")

    np.save(filename, embedding)

    print("Embedding stored:", filename)

    # Update profile only if required
    if update:
        update_profile()


# ---------------- BULK SAVE (REGISTRATION) ----------------

def save_multiple_embeddings(embeddings):
    """
    Save multiple embeddings (used in registration)
    and update profile only once
    """

    config = load_config()
    path = config["paths"]["embeddings"]

    os.makedirs(path, exist_ok=True)

    for emb in embeddings:
        filename = os.path.join(path, f"{uuid.uuid4()}.npy")
        np.save(filename, emb)

    print(f"{len(embeddings)} embeddings stored")

    # Update profile once
    update_profile()

