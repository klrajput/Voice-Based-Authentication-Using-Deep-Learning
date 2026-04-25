
import numpy as np
import os

PROFILE_PATH = "data/profile/user_profile.npy"
EMBEDDINGS_PATH = "data/embeddings"


# ---------------- UPDATE PROFILE ----------------

def update_profile():
    """
    Build user profile by averaging all stored embeddings
    """

    if not os.path.exists(EMBEDDINGS_PATH):
        print("No embeddings folder found")
        return None

    embeddings = []

    for file in os.listdir(EMBEDDINGS_PATH):
        if file.endswith(".npy"):
            try:
                emb = np.load(os.path.join(EMBEDDINGS_PATH, file))
                embeddings.append(emb)
            except:
                print(f"Skipping corrupted file: {file}")

    if len(embeddings) == 0:
        print("No valid embeddings found")
        return None

    profile = np.mean(embeddings, axis=0)

    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
    np.save(PROFILE_PATH, profile)

    print("Profile updated successfully")

    return profile


# ---------------- LOAD PROFILE ----------------

def load_profile():
    """
    Load stored voice profile
    """

    if not os.path.exists(PROFILE_PATH):
        return None

    try:
        return np.load(PROFILE_PATH)
    except:
        print("Profile corrupted")
        return None


# ---------------- RESET PROFILE ----------------

def reset_profile():
    """
    Delete all embeddings and profile (used for re-registration)
    """

    if os.path.exists(PROFILE_PATH):
        os.remove(PROFILE_PATH)

    if os.path.exists(EMBEDDINGS_PATH):
        for file in os.listdir(EMBEDDINGS_PATH):
            if file.endswith(".npy"):
                os.remove(os.path.join(EMBEDDINGS_PATH, file))

    print("Profile reset successfully")

