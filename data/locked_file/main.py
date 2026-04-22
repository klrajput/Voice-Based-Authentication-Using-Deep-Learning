from audio.recorder import record_voice
from audio.preprocess import preprocess_audio
from features.extract_features import extract_features
from model.verify_voice import verify_voice
from learning.continual_learning import save_embedding
from security.antispoof import detect_spoof
from evaluation.logger import log_auth

def register():

    print("Registering voice...")

    raw = record_voice()
    processed = preprocess_audio(raw)

    embedding = extract_features(processed)

    save_embedding(embedding)

    print("Voice registered successfully")

def authenticate():

    print("Authenticating...")

    raw = record_voice()
    processed = preprocess_audio(raw)

    # anti spoof check
    if detect_spoof(processed):

        print("⚠️ Spoof attack detected!")
        return

    embedding = extract_features(processed)

    result, score = verify_voice(embedding)

    print("Similarity Score:", score)

    if result:

        print("Access Granted")

        save_embedding(embedding)

        log_auth(score, "accept")

    else:

        print("Access Denied")

        log_auth(score, "reject")

def main():

    while True:

        print("\n1 Register Voice")
        print("2 Authenticate Voice")
        print("3 Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            register()

        elif choice == "2":
            authenticate()

        else:
            break

if __name__ == "__main__":
    main()