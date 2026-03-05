import numpy as np
import uuid
import yaml
from model.profile_manager import update_profile


def load_config():
    with open("configs/config.yaml") as f:
        return yaml.safe_load(f)


def save_embedding(embedding):

    config = load_config()

    filename = f"{config['paths']['embeddings']}/{uuid.uuid4()}.npy"

    np.save(filename, embedding)

    print("Embedding stored:", filename)

    update_profile()