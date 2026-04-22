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


def register_voice():
    raw = record_voice()
    proc = preprocess_audio(raw)
    emb = extract_features(proc)
    save_embedding(emb)


def get_user_folder(user_id):
    base = os.path.join(BASE_PROFILE_PATH, user_id)
    emb = os.path.join(base, "embeddings")
    os.makedirs(emb, exist_ok=True)
    return base


def save_user_identity(name, user_id):
    os.makedirs(os.path.dirname(USER_INFO_PATH), exist_ok=True)
    data = {}

    if os.path.exists(USER_INFO_PATH):
        with open(USER_INFO_PATH, "r") as f:
            try:
                data = json.load(f)
            except:
                data = {}

    data[user_id] = {"name": name.strip()}

    with open(USER_INFO_PATH, "w") as f:
        json.dump(data, f, indent=4)


def load_user_identity(user_id):
    if not os.path.exists(USER_INFO_PATH):
        return {"name": "", "user_id": ""}

    with open(USER_INFO_PATH, "r") as f:
        data = json.load(f)

    user = data.get(user_id, {})
    return {"name": user.get("name", ""), "user_id": user_id}


def save_lock_metadata(file_name, user_id):
    os.makedirs(os.path.dirname(LOCK_META_PATH), exist_ok=True)
    data = {}

    if os.path.exists(LOCK_META_PATH):
        with open(LOCK_META_PATH, "r") as f:
            try:
                data = json.load(f)
            except:
                data = {}

    data[user_id] = {"locked_file": file_name}

    with open(LOCK_META_PATH, "w") as f:
        json.dump(data, f, indent=4)


def load_lock_metadata(user_id):
    if not os.path.exists(LOCK_META_PATH):
        return None

    with open(LOCK_META_PATH, "r") as f:
        data = json.load(f)

    return data.get(user_id)


def login_via_voice(user_id):
    user_folder = get_user_folder(user_id)

    from model import profile_manager
    original = EMBEDDINGS_PATH
    profile_manager.EMBEDDINGS_PATH = os.path.join(user_folder, "embeddings")

    if load_profile() is None:
        profile_manager.EMBEDDINGS_PATH = original
        return False, None, "No registered voice profile found"

    raw = record_voice()
    proc = preprocess_audio(raw)

    if detect_spoof(proc):
        profile_manager.EMBEDDINGS_PATH = original
        return False, None, "Spoof detected"

    emb = extract_features(proc)
    result, score = verify_voice(emb, user_id)

    if result:
        save_embedding(emb)
        log_auth(score, "accept")
    else:
        log_auth(score, "reject")

    profile_manager.EMBEDDINGS_PATH = original
    return result, float(score), ""


def read_auth_logs():
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r") as f:
        rows = list(csv.DictReader(f))

    rows.reverse()
    return rows[:10]


def apply_custom_styles():
    st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a, #1e293b);
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="Voice-Based File Locker", layout="wide")
    apply_custom_styles()

    st.title("🔐 Voice-Based Secure File Locker")

    col1, col2 = st.columns([2, 1])

    with col1:
        name_col, id_col = st.columns(2)

        with id_col:
            user_id = st.text_input("User ID")

        with name_col:
            identity = load_user_identity(user_id) if user_id else {"name": ""}
            user_name = st.text_input("User Name", value=identity["name"])

        st.subheader("📁 File Locker")

        uploaded_file = st.file_uploader("Upload a file")

        file_name = None

        if uploaded_file:
            path = "data/locked_file"
            os.makedirs(path, exist_ok=True)

            save_path = os.path.join(path, uploaded_file.name)
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            file_name = uploaded_file.name
            st.success(f"File '{file_name}' uploaded")

        if st.button("🔐 Lock File"):
            if not user_name.strip() or not user_id.strip():
                st.error("Enter user details first")
            elif not uploaded_file:
                st.error("Upload a file first")
            else:
                folder = get_user_folder(user_id)

                from model import profile_manager
                original = EMBEDDINGS_PATH
                profile_manager.EMBEDDINGS_PATH = os.path.join(folder, "embeddings")

                register_voice()
                save_user_identity(user_name, user_id)
                save_lock_metadata(file_name, user_id)

                profile_manager.EMBEDDINGS_PATH = original
                st.success(f"File '{file_name}' locked")

        if st.button("🔓 Unlock File"):
            metadata = load_lock_metadata(user_id)

            if not metadata:
                st.error("No locked file found")
            elif not uploaded_file:
                st.error("Please upload the file you want to unlock")
            elif uploaded_file.name != metadata["locked_file"]:
                st.error("❌ This file is not the locked file")
            else:
                challenge = random.randint(10, 99)
                st.warning(f"🎤 Please say this number clearly: {challenge}")

                result, score, message = login_via_voice(user_id)

                if message:
                    st.error(message)
                else:
                    if score is not None:
                        st.subheader("🎯 Authentication Score")
                        st.progress(min(max(score, 0.0), 1.0))
                        st.write(f"Similarity Score: {score:.4f}")

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

    with col2:
        st.subheader("🔒 Locked File Status")

        metadata = load_lock_metadata(user_id) if user_id else None

        if metadata:
            st.success(f"Locked File: {metadata['locked_file']}")
        else:
            st.info("No file is currently locked")

        st.subheader("🛡️ System Security Status")

        if metadata:
            st.success("🔒 System Status: ACTIVE")
            st.write(f"Protected File: {metadata['locked_file']}")
            st.write(f"Authorized User: {user_id}")
        else:
            st.warning("⚠️ System Status: NO FILE LOCKED")

        st.divider()

        st.subheader("📊 Logs")

        logs = read_auth_logs()

        if logs:
            st.dataframe(logs)
        else:
            st.write("No logs yet")


if __name__ == "__main__":
    main()
