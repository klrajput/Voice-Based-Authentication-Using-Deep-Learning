import csv
import json
import os
import random

import streamlit as st

from audio.preprocess import preprocess_audio
from audio.recorder import record_voice
from evaluation.logger import LOG_FILE, log_auth
from features.extract_features import extract_features
from learning.continual_learning import save_embedding
from model.profile_manager import EMBEDDINGS_PATH, PROFILE_PATH, load_profile
from model.verify_voice import load_config, verify_voice
from security.antispoof import detect_spoof

LOCK_META_PATH = "data/locked_file/lock_meta.json"
USER_INFO_PATH = "data/profile/user_info.json"
BASE_PROFILE_PATH = "data/profile/users"


def register_voice() -> None:
    raw_file = record_voice()
    processed_file = preprocess_audio(raw_file)
    embedding = extract_features(processed_file)
    save_embedding(embedding)

def get_user_folder(user_id: str):
    base_path = os.path.join(BASE_PROFILE_PATH, user_id)
    embeddings_path = os.path.join(base_path, "embeddings")
    os.makedirs(embeddings_path, exist_ok=True)
    return base_path

def save_user_identity(name: str, user_id: str) -> None:
    os.makedirs(os.path.dirname(USER_INFO_PATH), exist_ok=True)
    data = {}
    # Load existing users
    if os.path.exists(USER_INFO_PATH):
        with open(USER_INFO_PATH, "r") as f:
            try:
                data = json.load(f)
            except:
                data = {}
    # Add/update current user
    data[user_id] = {"name": name.strip()}
    # Save back
    with open(USER_INFO_PATH, "w") as f:
        json.dump(data, f, indent=4)


def load_user_identity(user_id: str) -> dict[str, str]:
    if not os.path.exists(USER_INFO_PATH):
        return {"name": "", "user_id": ""}
    with open(USER_INFO_PATH, "r") as file:
        data = json.load(file)
    user = data.get(user_id, {})
    return {
        "name": user.get("name", ""),
        "user_id": user_id
    }


def save_lock_metadata(file_name: str, user_id: str) -> None:
    os.makedirs(os.path.dirname(LOCK_META_PATH), exist_ok=True)
    data = {}
    # Load existing data
    if os.path.exists(LOCK_META_PATH):
        with open(LOCK_META_PATH, "r") as f:
            try:
                data = json.load(f)
            except:
                data = {}
    # Save per-user file
    data[user_id] = {
        "locked_file": file_name
    }
    with open(LOCK_META_PATH, "w") as f:
        json.dump(data, f, indent=4)


def load_lock_metadata(user_id: str):
    if not os.path.exists(LOCK_META_PATH):
        return None
    with open(LOCK_META_PATH, "r") as f:
        data = json.load(f)
    return data.get(user_id)


def reset_profile_data() -> None:
    if os.path.exists(EMBEDDINGS_PATH):
        for file_name in os.listdir(EMBEDDINGS_PATH):
            if file_name.endswith(".npy"):
                os.remove(os.path.join(EMBEDDINGS_PATH, file_name))

    if os.path.exists(PROFILE_PATH):
        os.remove(PROFILE_PATH)

    if os.path.exists(USER_INFO_PATH):
        os.remove(USER_INFO_PATH)


def login_via_voice() -> tuple[bool, float | None, str]:
    if load_profile() is None:
        return False, None, "No registered voice profile found. Please register first."

    raw_file = record_voice()
    processed_file = preprocess_audio(raw_file)

    if detect_spoof(processed_file):
        return False, None, "Spoof attempt detected. Authentication blocked."

    embedding = extract_features(processed_file)
    result, score = verify_voice(embedding)

    if result:
        save_embedding(embedding)
        log_auth(score, "accept")
    else:
        log_auth(score, "reject")

    return result, float(score), ""


def read_auth_logs(limit: int = 10) -> list[dict[str, str]]:
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r", newline="") as file:
        rows = list(csv.DictReader(file))

    rows.reverse()
    return rows[:limit]


def apply_custom_styles():
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a, #1e293b);
            color: white;
        }

        h1, h2, h3 {
            color: #facc15;
        }

        .stButton>button {
            background: linear-gradient(90deg, #22c55e, #16a34a);
            color: white;
            border-radius: 10px;
            height: 3em;
            font-weight: bold;
        }

        .stDownloadButton>button {
            background: linear-gradient(90deg, #3b82f6, #2563eb);
            color: white;
            border-radius: 10px;
            height: 3em;
            font-weight: bold;
        }

        .stTextInput>div>div>input {
            background-color: #1e293b;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title="Voice-Based File Locker", layout="wide")
    apply_custom_styles()
    config = load_config()
    threshold = float(config["model"]["threshold"])
    identity = load_user_identity(user_id) if 'user_id' in locals() else {"name": "", "user_id": ""}

    st.title("🔐 Voice-Based Secure File Locker")

    col1, col2 = st.columns([2, 1])

    # ================= LEFT SIDE =================
    with col1:

        # USER INPUTS (FIXED POSITION)
        name_col, id_col = st.columns(2)
        with name_col:
            user_name = st.text_input("User Name", value=identity["name"])
        with id_col:
            user_id = st.text_input("User ID", value=identity["user_id"])

        st.subheader("📁 File Locker")

        uploaded_file = st.file_uploader("Upload a file")

        file_name = None

        if uploaded_file:
            file_path = "data/locked_file"
            os.makedirs(file_path, exist_ok=True)

            save_path = os.path.join(file_path, uploaded_file.name)

            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            file_name = uploaded_file.name
            st.success(f"File '{file_name}' uploaded")

        # LOCK FILE
        if st.button("🔐 Lock File"):
            if not user_name.strip() or not user_id.strip():
                st.error("Enter user details first")
            elif not uploaded_file:
                st.error("Upload a file first")
            else:
                user_folder = get_user_folder(user_id)

                # temporarily change global path
                original_path = EMBEDDINGS_PATH

                # redirect embeddings to user-specific folder
                from model import profile_manager
                profile_manager.EMBEDDINGS_PATH = os.path.join(user_folder, "embeddings")

                register_voice()
                save_user_identity(user_name, user_id)
                save_lock_metadata(file_name, user_id)

                # restore original path
                profile_manager.EMBEDDINGS_PATH = original_path
                st.success(f"File '{file_name}' locked")

        # UNLOCK FILE
        if st.button("🔓 Unlock File"):
            metadata = load_lock_metadata(user_id)

            if not metadata:
                st.error("No locked file found")
            elif not uploaded_file:
                st.error("Please upload the file you want to unlock")
            elif uploaded_file.name != metadata["locked_file"]:
                st.error("❌ This file is not the locked file")

            elif user_id != metadata["user_id"]:
                st.error("❌ This file belongs to another user")

            else:
                challenge = random.randint(10, 99)
                st.warning(f"🎤 Please say this number clearly: {challenge}")
                result, score, message = login_via_voice()

                if message:
                    st.error(message)
                else:
                    if score is not None:
                        st.subheader("🎯 Authentication Score")

                        st.progress(min(max(score, 0.0), 1.0))

                        st.write(f"Similarity Score: {score:.4f}")

                        threshold = float(load_config()["model"]["threshold"])

                        if score >= threshold:
                            st.success("Voice Match Level: HIGH ✅")
                        else:
                            st.warning("Voice Match Level: LOW ⚠️")

                    if result:
                        file_path = os.path.join("data", "locked_file", metadata["locked_file"])

                        st.success(f"✅ File '{metadata['locked_file']}' unlocked successfully")

                        if os.path.exists(file_path):
                            with open(file_path, "rb") as f:
                                st.download_button(
                                    label="⬇️ Download File",
                                    data=f,
                                    file_name=metadata["locked_file"],
                                    use_container_width=True
                                )
                        else:
                            st.error("File not found on system")
                    else:
                        st.error("❌ Access Denied (voice mismatch)")

    # ================= RIGHT SIDE =================

    st.subheader("🔒 Locked File Status")

    metadata = load_lock_metadata(user_id)

    if metadata:
        st.success(f"Locked File: {metadata['locked_file']}")
    else:
        st.info("No file is currently locked")



    st.subheader("🛡️ System Security Status")
    metadata = load_lock_metadata(user_id)
    if metadata:
        st.success("🔒 System Status: ACTIVE")
        st.write(f"Protected File: {metadata['locked_file']}")
        st.write(f"Authorized User: {user_id}")
    else:
        st.warning("⚠️ System Status: NO FILE LOCKED")
    st.divider()

    with col2:
        st.subheader("📊 Logs")

        logs = read_auth_logs()

        if logs:
            st.dataframe(logs)
        else:
            st.write("No logs yet")


if __name__ == "__main__":
    main()
