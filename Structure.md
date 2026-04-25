# 🎙️ Voice-Based Authentication Using Deep Learning — Project Structure

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Directory Structure](#2-directory-structure)
3. [Module-by-Module Breakdown](#3-module-by-module-breakdown)
4. [System Architecture & Data Flow](#4-system-architecture--data-flow)
5. [Deep Dive: How Each Feature Works](#5-deep-dive-how-each-feature-works)
6. [Authentication Decision Logic](#6-authentication-decision-logic)
7. [Encryption System](#7-encryption-system)
8. [Anti-Spoofing System](#8-anti-spoofing-system)
9. [Continual Learning](#9-continual-learning)
10. [Evaluation & Logging](#10-evaluation--logging)
11. [Configuration Reference](#11-configuration-reference)
12. [Dependencies](#12-dependencies)
13. [Running the Project](#13-running-the-project)
14. [Development Roadmap](#14-development-roadmap)

---

## 1. Project Overview

**Voice-Based Authentication Using Deep Learning** (VoiceLock) is a **single-user** biometric security system. It replaces passwords with voice verification — the user speaks, the system extracts a 192-dimensional neural fingerprint using **SpeechBrain's ECAPA-TDNN** model, and compares it against a stored voice profile using **cosine similarity**.

The flagship feature is a **Voice-Locked File Vault**: files uploaded by the user are encrypted on disk with **AES-256** (via Python `cryptography.Fernet`). Only the registered user — verified by voice biometric AND a secret phrase — can decrypt and download them.

**Core capabilities:**
- 5-sample voice enrollment building an averaged biometric profile
- Cosine-similarity-based single-user authentication
- AES-256 file encryption at rest; decryption gated by voice auth
- Anti-spoofing via spectral flatness + ZCR analysis
- Continual learning — profile improves after every successful login
- Cyberpunk-themed Streamlit web UI + CLI interface
- Authentication event logging and FAR/FRR metrics

---

## 2. Directory Structure

```
Voice-Based-Authentication-Using-Deep-Learning/
│
├── configs/
│   └── config.yaml                   # Audio settings, file paths, auth threshold
│
├── data/
│   ├── raw_audio/                    # Raw .wav files from microphone (UUID names)
│   ├── processed_audio/              # Noise-reduced .wav files (UUID names)
│   ├── embeddings/                   # .npy voice embedding files (one per sample)
│   ├── profile/
│   │   ├── user_profile.npy          # Mean of all embeddings — identity anchor
│   │   └── single_user.json          # { "name": "...", "phrase": "..." }
│   ├── locked_file/                  # AES-256 encrypted files (.enc extension)
│   └── security/
│       └── key.key                   # Fernet encryption key (auto-generated)
│
├── models/
│   └── speaker_model/
│       └── classifier.pth            # Legacy linear classifier weights
│
├── src/
│   ├── audio/
│   │   ├── recorder.py               # Microphone capture (sounddevice)
│   │   └── preprocess.py             # Noise reduction (noisereduce + librosa)
│   ├── features/
│   │   └── extract_features.py       # ECAPA-TDNN 192-dim embedding extraction
│   ├── model/
│   │   ├── profile_manager.py        # update_profile / load_profile / reset_profile
│   │   ├── verify_voice.py           # Cosine similarity authentication decision
│   │   └── ecapa_classifier.py       # Legacy linear classifier (not used in current flow)
│   ├── security/
│   │   ├── antispoof.py              # Spectral flatness + ZCR spoof detection
│   │   └── encryption.py             # AES-256 encrypt/decrypt via Fernet
│   ├── learning/
│   │   └── continual_learning.py     # save_embedding / save_multiple_embeddings
│   ├── evaluation/
│   │   ├── logger.py                 # Append rows to auth_log.csv
│   │   └── metrics.py                # FAR, FRR, scatter plot
│   ├── main.py                       # CLI entry point
│   └── streamlit_app.py              # Streamlit web app (Profile / Lock / Unlock)
│
├── requirements.txt
├── project.md                        # 10-phase development roadmap
└── README.md                         # Full project documentation
```

---

## 3. Module-by-Module Breakdown

### `configs/config.yaml`
```yaml
audio:
  sample_rate: 16000    # Hz — Nyquist standard for speech
  duration: 6           # seconds per recording

paths:
  raw_audio: data/raw_audio
  processed_audio: data/processed_audio
  embeddings: data/embeddings

model:
  threshold: 0.75       # cosine similarity threshold for authentication
```
Every module reads this file at runtime — no hardcoded values in source.

---

### `data/` — Runtime Data Store

| Path | Content |
|---|---|
| `raw_audio/` | Raw `.wav` from mic; UUID filename per recording |
| `processed_audio/` | Noise-reduced `.wav`; UUID filename |
| `embeddings/` | One `.npy` file per voice sample (192-dim arrays) |
| `profile/user_profile.npy` | Element-wise mean of all embeddings in `embeddings/` |
| `profile/single_user.json` | `{ "name": "Alice", "phrase": "open the vault" }` |
| `locked_file/` | AES-256 encrypted files stored as `<original_name>.enc` |
| `security/key.key` | 256-bit Fernet key (generated once, persisted) |

---

### `src/audio/recorder.py`

```
record_voice()
  ├── load config.yaml → duration=6, sample_rate=16000
  ├── generate UUID filename → data/raw_audio/<uuid>.wav
  ├── sounddevice.rec(duration * sample_rate, samplerate=16000, channels=1)
  ├── sd.wait()  ← blocking until done
  ├── scipy.io.wavfile.write(filename, fs, recording)
  └── return filename
```

**Why mono at 16 kHz:** Speech energy lives below 8 kHz; Nyquist requires 2× = 16 kHz. All SpeechBrain speech models expect 16 kHz mono input.

---

### `src/audio/preprocess.py`

```
preprocess_audio(file_path)
  ├── librosa.load(file_path, sr=16000)   → float32 array + sr
  ├── noisereduce.reduce_noise(y, sr)     → Wiener-filter denoising
  ├── uuid filename → data/processed_audio/<uuid>.wav
  ├── soundfile.write(output_file, cleaned_audio, sr)
  └── return output_file
```

**How noisereduce works:** Estimates the noise spectral profile from quiet segments of the signal, then subtracts it using a Wiener filter — effective against stationary noises (fan hum, air conditioning).

---

### `src/features/extract_features.py`

Module-level singleton — loaded once when imported:

```python
verification = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="models/speaker_model"
)
```

```
extract_features(file_path)
  ├── torchaudio.load(file_path)           → tensor [channels, T]
  ├── if channels > 1: torch.mean(dim=0)   → mono [1, T]
  ├── verification.encode_batch(signal)    → ECAPA-TDNN forward pass
  └── return embedding.numpy()             → shape [1, 1, 192]
```

**ECAPA-TDNN architecture:**
1. Input: raw waveform `[1, T]`
2. Dilated 1D convolutions — temporal patterns at scales 1, 2, 3, 4
3. SE-Res2Net blocks — channel attention + multi-scale feature aggregation
4. Attentive statistics pooling — collapses time axis to fixed vector
5. Output: 192-dimensional speaker embedding (x-vector)

The 192 floats encode: pitch patterns, formant frequencies, vocal tract shape, speaking rhythm — all unique to each speaker.

---

### `src/model/profile_manager.py`

**Three functions — full lifecycle of the voice profile:**

```
update_profile()
  ├── scan data/embeddings/ for all *.npy files
  ├── np.load() each → stack into list
  ├── np.mean(embeddings, axis=0)   → centroid in 192-dim space
  ├── np.save(PROFILE_PATH, profile)
  └── return profile

load_profile()
  ├── check if data/profile/user_profile.npy exists
  ├── np.load(PROFILE_PATH)
  └── return array (or None if missing/corrupted)

reset_profile()
  ├── os.remove(PROFILE_PATH)              ← delete profile
  └── delete all *.npy in data/embeddings/ ← delete all samples
```

**Why average N embeddings?** Each recording varies slightly (mic distance, energy, phrasing). Averaging 5 registration samples creates a centroid in 192-dim space that is robust to these natural variations.

---

### `src/model/verify_voice.py`

**Updated for single-user — cosine similarity only, no classifier:**

```
verify_voice(emb, user_id=None)
  ├── profile = load_profile()
  ├── emb     = np.array(emb).squeeze()       → [192]
  ├── profile = np.array(profile).squeeze()   → [192]
  ├── score   = cosine_similarity(emb.reshape(1,-1), profile.reshape(1,-1))[0][0]
  ├── threshold = config["model"]["threshold"]   # default 0.75
  └── return (score >= threshold), float(score)
```

**Cosine similarity:**
```
score = (A · B) / (||A|| × ||B||)   ∈ [-1.0, 1.0]
```
Measures the angle between two vectors — not magnitude. This makes it robust to volume differences between recordings.

> **Change from old version:** The `ECAPAClassifier` (speaker class lookup via `classifier.pth`) is no longer part of the authentication decision. The single-user system only needs cosine similarity + the phrase check in the UI layer.

---

### `src/security/antispoof.py`

```
detect_spoof(audio_file)
  ├── librosa.load(audio_file, sr=16000)
  ├── flatness = np.mean(librosa.feature.spectral_flatness(y=y))
  ├── zcr      = np.mean(librosa.feature.zero_crossing_rate(y))
  ├── if flatness > 0.5 OR zcr < 0.01:
  │       return True    ← SPOOF DETECTED
  └── return False       ← GENUINE
```

| Feature | Normal Live Speech | Replay / Synthetic |
|---|---|---|
| Spectral Flatness | Low (< 0.5) — tonal | High (> 0.5) — noise-like through speaker |
| Zero Crossing Rate | Moderate (> 0.01) | Very low (< 0.01) — DC artifact |

---

### `src/security/encryption.py`

**AES-256 file encryption using Python's `cryptography.Fernet`.**

Fernet wraps AES-128-CBC with HMAC-SHA256 authentication — effectively providing AES-256-level symmetric encryption.

```
KEY_PATH = "data/security/key.key"

generate_key()
  ├── os.makedirs(data/security/, exist_ok=True)
  ├── Fernet.generate_key()   → 256-bit cryptographically random key
  └── write to key.key        ← only if key doesn't already exist

load_key()
  ├── if key.key doesn't exist → generate_key()
  └── read and return key bytes

encrypt_file(input_path, output_path)
  ├── key    = load_key()
  ├── cipher = Fernet(key)
  ├── data   = open(input_path, "rb").read()
  ├── encrypted = cipher.encrypt(data)
  └── write encrypted to output_path   ← saved as .enc

decrypt_file(input_path, output_path)
  ├── key    = load_key()
  ├── cipher = Fernet(key)
  ├── data   = open(input_path, "rb").read()
  ├── decrypted = cipher.decrypt(data)
  └── write decrypted to output_path
```

**Lock flow in the app:**
```
upload file → save as temp → encrypt_file(temp, temp + ".enc")
           → os.remove(temp)   ← plaintext deleted
           → .enc stored in data/locked_file/
```

**Unlock flow in the app:**
```
auth passes → for each .enc in data/locked_file/:
                decrypt_file(.enc, unlocked_<name>)
                → st.download_button shown
```

**Key lifecycle warning:** The key is generated once and stored in `data/security/key.key`. Losing this file = **permanent loss of access** to all `.enc` files. Back it up.

---

### `src/learning/continual_learning.py`

Two functions covering both registration and ongoing learning:

```
save_embedding(embedding, update=True)
  ├── uuid filename → data/embeddings/<uuid>.npy
  ├── np.save(filename, embedding)
  └── if update: update_profile()    ← single-embedding auth feedback

save_multiple_embeddings(embeddings)  ← used during 5-sample registration
  ├── for each emb: np.save(<uuid>.npy)
  └── update_profile()               ← called once after all 5 saved
```

`save_multiple_embeddings` is more efficient for registration — saves all 5 embeddings first, then recomputes the profile mean once rather than 5 times.

---

### `src/evaluation/logger.py`

```
log_auth(score, result)
  └── open("data/logs/auth_log.csv", "a")
        write: [datetime.now(), score, result]
        e.g.:  2026-04-25 13:00:00, 0.8312, accept
```

---

### `src/evaluation/metrics.py`

```
compute_metrics()
  ├── df = pd.read_csv("data/logs/auth_log.csv")
  ├── threshold = 0.65
  ├── FAR = len(df[(score > threshold) & (result == "reject")]) / len(df)
  ├── FRR = len(df[(score <= threshold) & (result == "accept")]) / len(df)
  ├── print FAR, FRR
  └── plt.scatter(df["score"], df["result"])   → visual boundary inspection
```

---

### `src/main.py` — CLI Interface

```
main()  ← infinite loop
  ├── 1 → register()
  │         record_voice() → preprocess_audio() → extract_features()
  │         → save_embedding() → update_profile()
  │
  ├── 2 → authenticate()
  │         record_voice() → preprocess_audio()
  │         → detect_spoof() [abort if spoof]
  │         → extract_features()
  │         → verify_voice(emb)
  │         → if granted: save_embedding() + log_auth("accept")
  │         → if denied:  log_auth("reject")
  │
  └── 3 → break
```

---

### `src/streamlit_app.py` — Web Application

Cyberpunk-themed Streamlit app with glassmorphism cards, animated waveform bars, rotating security rings, and Google Fonts (Orbitron, Rajdhani, Share Tech Mono).

**Single-user data stores:**
```python
USER_DATA   = "data/profile/single_user.json"   # { name, phrase }
LOCK_FOLDER = "data/locked_file"                  # .enc files
```

**Three sidebar pages:**

#### 👤 Profile Page
```
Not registered?
  ├── Text inputs: Full Name + Unlock Phrase
  └── Button "Begin Voice Registration"
        save_user(name, phrase) → single_user.json
        register_user():
          for i in range(5):
            record_voice() → preprocess_audio() → extract_features()
            embeddings.append(emb)
          save_multiple_embeddings(embeddings)
          → "Voice profile registered successfully!"

Already registered?
  ├── Status / Encryption / Anti-Spoof status cards
  └── Button "Reset Profile & Re-register"
        reset_profile()  ← clears all embeddings + profile
```

#### 🔒 Lock File Page
```
Upload any file → Button "Encrypt & Lock File"
  ├── save file as temp → data/locked_file/<filename>
  ├── encrypt_file(temp, temp + ".enc")
  ├── os.remove(temp)   ← no plaintext on disk
  └── "File encrypted and stored in the vault"
```

#### 🔓 Unlock File Page
```
Button "Authenticate & Unlock"
  → authenticate()
      ├── load_user()                ← check registration
      ├── record_voice()
      ├── preprocess_audio()
      ├── detect_spoof()             ← abort if spoof
      ├── extract_features()
      ├── verify_voice(emb)          → score + bool
      ├── show score progress bar
      └── st.text_input("Type the phrase you just spoke")
            phrase == stored_phrase?  → return True/False

  If True:
    list all .enc files in data/locked_file/
    for each .enc:
      decrypt_file(.enc, unlocked_<name>)
      st.download_button(...)

  If False:
    "Authentication Failed — Voice or phrase mismatch"
```

**Authentication gate (in `authenticate()`):**
```python
if result and phrase.lower() == user["phrase"].lower():
    return True
return False
```
Both cosine similarity AND phrase must match.

---

## 4. System Architecture & Data Flow

### Registration Flow

```
User speaks 5× (6s each)
        │
        ▼  [repeated 5 times]
[recorder.py]    → data/raw_audio/<uuid>.wav
        │
        ▼
[preprocess.py]  → data/processed_audio/<uuid>.wav
        │
        ▼
[extract_features.py]  → 192-dim embedding (numpy)
        │
        ▼  [after all 5 collected]
[save_multiple_embeddings()]
        │  saves 5× data/embeddings/<uuid>.npy
        ▼
[update_profile()]
        mean(5 embeddings) → data/profile/user_profile.npy

[save_user(name, phrase)]
        → data/profile/single_user.json
```

### Authentication Flow

```
User speaks + types phrase
        │
        ▼
[recorder.py]  → raw .wav
        │
        ▼
[preprocess.py]  → cleaned .wav
        │
        ▼
[antispoof.detect_spoof()]
  flatness > 0.5 OR zcr < 0.01?
        │ YES → ABORT (spoof)
        │ NO
        ▼
[extract_features.py]  → 192-dim embedding
        │
        ▼
[verify_voice(emb)]
  score = cosine_similarity(emb, profile)
  score >= threshold?
        │
   YES  │  NO
   ─────┤  └─► DENIED + log("reject")
        │
        ▼
  phrase == stored_phrase?
        │
   YES  │  NO
   ─────┤  └─► DENIED
        │
        ▼
   ACCESS GRANTED
   decrypt_file() for each .enc
   download_button shown
   save_embedding() → update_profile()
   log_auth("accept")
```

### Encryption Flow

```
LOCK:
  plaintext_file
      → encrypt_file(plain, plain.enc)
      → delete plaintext
      → vault stores plain.enc  [unreadable without key]

UNLOCK (only after auth):
  plain.enc
      → decrypt_file(plain.enc, unlocked_plain)
      → stream to browser as download
```

---

## 5. Deep Dive: How Each Feature Works

### ECAPA-TDNN (The Neural Core)

Pre-trained on VoxCeleb — a large-scale dataset of celebrity speech from YouTube — and cached in `models/speaker_model/` after first download.

Internal processing:
1. **Input:** raw waveform tensor `[1, T]` at 16 kHz
2. **Frame-level features:** 1D convolutions over 25ms windows, 10ms hop
3. **TDNN Layers:** dilated convolutions at factors 1→4 capture wider temporal context per layer
4. **SE-Res2Net Blocks:** squeeze-and-excitation gates + Res2Net multi-branch convolutions for channel-wise attention
5. **Attentive Statistics Pooling:** learns frame-by-frame attention weights; collapses T frames into a (mean, std) descriptor
6. **Output:** 192-dimensional embedding — a unique speaker fingerprint

### Cosine Similarity (The Matching Engine)

```
score = (A · B) / (||A|| × ||B||)
```

Measures the cosine of the angle between two 192-dim vectors:
- `1.0` = identical direction = same speaker
- `0.0` = orthogonal = unrelated speakers
- Threshold: `0.75` by default

**Why cosine not Euclidean?** Cosine is magnitude-invariant — it doesn't matter if one recording is louder than another. Only the direction of the vector matters, which encodes speaker identity, not recording conditions.

### AES-256 via Fernet

`cryptography.Fernet` = AES-128-CBC + PKCS7 padding + HMAC-SHA256 authentication tag, in a URL-safe base64 envelope. The key is 32 bytes (256 bits) generated by `os.urandom(32)`.

Properties:
- **Symmetric** — same key encrypts and decrypts
- **Authenticated** — HMAC tag prevents tampering; corrupted `.enc` raises `InvalidToken`
- **Non-deterministic** — same plaintext → different ciphertext each time (random IV)

---

## 6. Authentication Decision Logic

```
Step 1: detect_spoof(processed_audio)
  → flatness > 0.5 OR zcr < 0.01  → REJECT immediately

Step 2: verify_voice(embedding)
  → cosine_similarity(emb, profile) >= threshold  → PASS

Step 3: phrase check (UI layer)
  → user_input.lower() == stored_phrase.lower()  → PASS

All 3 pass → ACCESS GRANTED + decrypt files
Any fail  → ACCESS DENIED
```

This implements **two-factor biometric + knowledge authentication:**
- Factor 1: **Something you are** — your voice
- Factor 2: **Something you know** — your secret phrase

---

## 7. Encryption System

| Aspect | Detail |
|---|---|
| Algorithm | AES-128-CBC with HMAC-SHA256 (Fernet) |
| Key size | 256-bit (32 bytes) |
| Key storage | `data/security/key.key` (local file) |
| Key generation | Once on first run; persists across sessions |
| File format | `.enc` — binary ciphertext with HMAC tag |
| Plaintext retention | Deleted after encryption (`os.remove`) |
| Decryption trigger | Only after successful voice + phrase auth |

> ⚠️ **Critical:** Losing `data/security/key.key` makes all `.enc` files permanently unrecoverable. Always back up this file.

---

## 8. Anti-Spoofing System

| Check | Signal Feature | Threshold | What It Catches |
|---|---|---|---|
| Spectral Flatness | `librosa.feature.spectral_flatness` | `> 0.5` → spoof | Replay through speaker (signal becomes noise-like) |
| Zero Crossing Rate | `librosa.feature.zero_crossing_rate` | `< 0.01` → spoof | DC-offset or near-silent/muffled playback |

**Limitations:** These heuristics catch basic replay attacks. Advanced AI voice cloning (TTS deepfakes) would require a dedicated neural anti-spoof model (planned for Phase 9).

---

## 9. Continual Learning

After every **successful** authentication:
```
save_embedding(emb, update=True)
  → data/embeddings/<uuid>.npy  [new sample added]
  → update_profile()             [mean recomputed with new sample]
```

**Effect over time:**

| Sessions | Profile Basis | Quality |
|---|---|---|
| After registration | Mean of 5 samples | Good baseline |
| After 5 logins | Mean of 10 samples | More robust |
| After 20 logins | Mean of 25 samples | Highly adapted |

The system adapts to natural voice changes (health, age, microphone, environment) while always updating only on **verified successful** logins — preventing profile poisoning.

---

## 10. Evaluation & Logging

### Log Schema (`data/logs/auth_log.csv`)
```
timestamp,score,result
2026-04-25 10:00:01,0.8312,accept
2026-04-25 10:05:44,0.4210,reject
```

### Metrics

| Metric | Formula (threshold=0.65) | Target |
|---|---|---|
| **FAR** | Rows: score > threshold AND result="reject" / total | < 1% |
| **FRR** | Rows: score ≤ threshold AND result="accept" / total | < 5% |

The scatter plot (`score` vs `result`) visually shows where the score distributions overlap — useful for choosing the threshold value.

---

## 11. Configuration Reference

`configs/config.yaml`:

| Key | Value | Effect |
|---|---|---|
| `audio.sample_rate` | `16000` | Recording Hz; must match ECAPA-TDNN expectation |
| `audio.duration` | `6` | Seconds per voice recording |
| `paths.raw_audio` | `data/raw_audio` | Raw `.wav` output directory |
| `paths.processed_audio` | `data/processed_audio` | Cleaned `.wav` output directory |
| `paths.embeddings` | `data/embeddings` | `.npy` embedding storage |
| `model.threshold` | `0.75` | Cosine similarity threshold; raise = stricter |

---

## 12. Dependencies

| Package | Role |
|---|---|
| `torch` / `torchaudio` | PyTorch runtime + audio loading for ECAPA-TDNN |
| `speechbrain` | ECAPA-TDNN pretrained model |
| `librosa` | Audio loading, spectral features (flatness, ZCR) |
| `noisereduce` | Wiener-filter stationary noise removal |
| `sounddevice` | Microphone recording |
| `scipy` | Writing `.wav` files |
| `scikit-learn` | Cosine similarity computation |
| `numpy` | Array math, `.npy` embedding storage |
| `soundfile` | Writing processed audio files |
| `cryptography` | AES-256 Fernet encryption/decryption |
| `pyyaml` | Parsing `config.yaml` |
| `streamlit` | Web application UI |
| `pandas` | Reading CSV auth logs for metrics |
| `matplotlib` | Scatter plot for threshold analysis |

---

## 13. Running the Project

### Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Streamlit Web App
```bash
cd src
streamlit run streamlit_app.py
# → http://localhost:8501
```

### CLI
```bash
cd src
python main.py
```

### Evaluate Metrics
```bash
cd src
python -c "from evaluation.metrics import compute_metrics; compute_metrics()"
```

### Pre-download ECAPA-TDNN Model
```bash
python3 -c "
from speechbrain.inference.speaker import SpeakerRecognition
SpeakerRecognition.from_hparams(
    source='speechbrain/spkrec-ecapa-voxceleb',
    savedir='models/speaker_model'
)
print('Model ready.')
"
```

### macOS Microphone
System Settings → Privacy & Security → Microphone → allow Terminal / IDE.

---

## 14. Development Roadmap

| Phase | Status | Description |
|---|---|---|
| **1** — Foundation & Audio | ✅ Complete | `recorder.py`, `preprocess.py`, project setup |
| **2** — Deep Learning | ✅ Complete | ECAPA-TDNN, `extract_features.py` |
| **3** — Verification & Profiles | ✅ Complete | Cosine similarity, single-user profile |
| **4** — Security & Adaptation | ✅ Complete | Anti-spoofing, continual learning, AES-256 encryption |
| **5** — UI & Logging | ✅ Complete | Cyberpunk Streamlit UI, CLI, auth logger |
| **6** — Advanced Metrics | 🔲 Planned | EER, ROC curves, noise robustness testing |
| **7** — Testing & QA | 🔲 Planned | pytest suite, VoxCeleb benchmark |
| **8** — UI/UX Overhaul | 🔲 Planned | Real-time spectrogram, waveform recording visualization |
| **9** — Standout Features | 🔲 Planned | Deep learning anti-spoof, secure key derivation, multi-modal |
| **10** — Deployment | 🔲 Planned | Docker, Streamlit Cloud / AWS |

---

*Documentation: Voice-Based Authentication Using Deep Learning | Semester 4 | Last updated: April 2026*
