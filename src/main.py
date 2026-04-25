import os
import json
import datetime

from audio.recorder import record_voice
from audio.preprocess import preprocess_audio
from features.extract_features import extract_features
from model.verify_voice import verify_voice
from learning.continual_learning import save_multiple_embeddings
from model.profile_manager import reset_profile
from security.antispoof import detect_spoof
from security.encryption import encrypt_file, decrypt_file


LOCK_FOLDER = "data/locked_file"
USER_DB = "data/profile/users.json"


# ---------------- USER DB ----------------

def load_users():
    if not os.path.exists(USER_DB):
        return {"users": {}}
    with open(USER_DB) as f:
        return json.load(f)


def save_users(data):
    os.makedirs("data/profile", exist_ok=True)
    with open(USER_DB, "w") as f:
        json.dump(data, f, indent=4)


# ---------------- REGISTRATION ----------------

def register():
    db = load_users()

    username = input("Enter username: ").strip().lower()
    phrase = input("Set unlock phrase: ").strip()

    if username in db["users"]:
        print("⚠️ User already exists")
        return

    embeddings = []

    print("\n🎤 Recording 5 voice samples...")
    for i in range(5):
        print(f"Sample {i+1}/5")
        raw = record_voice()
        proc = preprocess_audio(raw)
        emb = extract_features(proc)
        embeddings.append(emb)

    save_multiple_embeddings(embeddings)

    db["users"][username] = {
        "name": username,
        "phrase": phrase,
        "registered": str(datetime.date.today())
    }

    save_users(db)

    print("✅ User registered!")


# ---------------- AUTH ----------------

def authenticate():
    db = load_users()

    username = input("Enter username: ").strip().lower()

    if username not in db["users"]:
        print("❌ User not found")
        return False, None

    user = db["users"][username]

    raw = record_voice()
    proc = preprocess_audio(raw)

    if detect_spoof(proc):
        print("⚠️ Spoof detected")
        return False, None

    emb = extract_features(proc)
    result, score = verify_voice(emb)

    print(f"Score: {score:.4f}")

    phrase = input("Enter phrase: ").strip()

    if result and phrase.lower() == user["phrase"].lower():
        print("✅ Access Granted")
        return True, username

    print("❌ Access Denied")
    return False, None


# ---------------- LOCK ----------------

def lock_file():
    ok, user = authenticate()
    if not ok:
        return

    path = input("Enter file path: ").strip()

    if not os.path.exists(path):
        print("❌ File not found")
        return

    os.makedirs(LOCK_FOLDER, exist_ok=True)

    filename = os.path.basename(path)
    enc = os.path.join(LOCK_FOLDER, f"{user}_{filename}.enc")

    encrypt_file(path, enc)

    print(f"🔒 Saved as {enc}")


# ---------------- UNLOCK ----------------

def unlock_file():
    ok, user = authenticate()
    if not ok:
        return

    if not os.path.exists(LOCK_FOLDER):
        print("No files")
        return

    files = [f for f in os.listdir(LOCK_FOLDER) if f.startswith(user)]

    if not files:
        print("No files for this user")
        return

    for i, f in enumerate(files):
        print(f"{i+1}. {f}")

    try:
        choice = int(input("Select file: ")) - 1
        if choice < 0 or choice >= len(files):
            print("Invalid choice")
            return
    except:
        print("Invalid input")
        return

    enc_file = files[choice]
    enc_path = os.path.join(LOCK_FOLDER, enc_file)

    out = os.path.join(LOCK_FOLDER, "unlocked_" + enc_file.replace(".enc", ""))

    decrypt_file(enc_path, out)

    print(f"✅ Decrypted: {out}")


# ---------------- MAIN ----------------

def main():
    while True:
        print("\n==== Voice Locker · SecureVault ====")
        print("1. Register")
        print("2. Lock")
        print("3. Unlock")
        print("4. Reset")
        print("5. Exit")

        ch = input("Choice: ")

        if ch == "1":
            register()
        elif ch == "2":
            lock_file()
        elif ch == "3":
            unlock_file()
        elif ch == "4":
            reset_profile()
        elif ch == "5":
            break


if __name__ == "__main__":
    main()