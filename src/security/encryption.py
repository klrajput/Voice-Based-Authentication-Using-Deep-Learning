import os
from cryptography.fernet import Fernet

KEY_PATH = "data/security/key.key"


# ---------------- KEY MANAGEMENT ----------------

def generate_key():
    """
    Generate and store encryption key (only once)
    """
    os.makedirs(os.path.dirname(KEY_PATH), exist_ok=True)

    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        with open(KEY_PATH, "wb") as f:
            f.write(key)
        print("Encryption key generated")
    else:
        print("Key already exists")


def load_key():
    """
    Load encryption key
    """
    if not os.path.exists(KEY_PATH):
        generate_key()

    with open(KEY_PATH, "rb") as f:
        return f.read()


# ---------------- ENCRYPT FILE ----------------

def encrypt_file(input_path, output_path):
    """
    Encrypt file and save as .enc
    """
    key = load_key()
    cipher = Fernet(key)

    with open(input_path, "rb") as f:
        data = f.read()

    encrypted_data = cipher.encrypt(data)

    with open(output_path, "wb") as f:
        f.write(encrypted_data)

    print(f"File encrypted: {output_path}")


# ---------------- DECRYPT FILE ----------------

def decrypt_file(input_path, output_path):
    """
    Decrypt file
    """
    key = load_key()
    cipher = Fernet(key)

    with open(input_path, "rb") as f:
        encrypted_data = f.read()

    decrypted_data = cipher.decrypt(encrypted_data)

    with open(output_path, "wb") as f:
        f.write(decrypted_data)

    print(f"File decrypted: {output_path}")

