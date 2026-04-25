# 🎙️ Voice-Based Authentication Using Deep Learning — VoiceLock SecureVault

> A single-user biometric file vault that uses your voice + secret phrase as the key, with AES-256 encryption built in.

---

## Table of Contents
- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [System Architecture](#system-architecture)
- [Module Descriptions](#module-descriptions)
- [How It Works](#how-it-works)
- [Security Design](#security-design)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [Evaluation & Metrics](#evaluation--metrics)
- [Limitations & Future Work](#limitations--future-work)
- [Development Roadmap](#development-roadmap)
- [References](#references)

---

## Overview

**VoiceLock SecureVault** is a single-user biometric security system that replaces passwords with **voice verification + a secret phrase**. The system captures your voice, converts it into a 192-dimensional neural fingerprint using **SpeechBrain's ECAPA-TDNN** model (pre-trained on VoxCeleb), and verifies your identity via **cosine similarity** against a stored voice profile.

All files in the vault are encrypted at rest using **AES-256 (Fernet)**. Access requires passing three independent security checks: anti-spoofing analysis, voice biometric matching, and secret phrase verification.

The project provides two interfaces: a premium **cyberpunk-themed Streamlit web app** (v2.1) with 7 pages, login/logout sessions, profile photos, and activity feeds — and a **CLI** with the same core functionality.

---

## Problem Statement

Traditional authentication is inherently flawed:

| Weakness | Why It Matters |
|---|---|
| Passwords are forgotten, reused, or phished | Users create weak passwords; data breaches expose millions |
| PINs prove secret possession, not identity | Anyone with the PIN gets access |
| No credential answers "who is this person?" | Shared accounts undermine accountability |

**Voice biometrics** authenticates based on inherent vocal characteristics — impossible to forget, difficult to replicate. VoiceLock addresses the additional challenges:

| Challenge | Solution |
|---|---|
| Replay attacks | Spectral flatness + ZCR anti-spoofing heuristics |
| Background noise | `noisereduce` Wiener-filter preprocessing |
| Voice drift over time | Continual learning — profile updates after every successful auth |
| File security at rest | AES-256 Fernet encryption; plaintext never stored |

---

## Key Features

| Feature | Description |
|---|---|
| **5-Sample Registration** | Record voice 5 times to build a robust averaged biometric profile |
| **Two-Factor Auth** | Voice biometric (something you are) + secret phrase (something you know) |
| **AES-256 Encryption** | Files encrypted on disk via `cryptography.Fernet`; plaintext deleted after lock |
| **Anti-Spoofing** | Spectral flatness + ZCR heuristics block replay attacks before embedding extraction |
| **Continual Learning** | Profile auto-updates after successful auth for drift adaptation |
| **Login / Logout Sessions** | Session-based access control with `st.session_state` |
| **Profile Management** | Edit name, phrase, and profile photo; re-record voice samples |
| **Voice-Gated Reset** | Profile deletion requires voice auth + phrase — prevents unauthorized wipes |
| **Activity Feed** | In-app activity log with icons, descriptions, and timestamps |
| **Premium UI** | Cyberpunk-themed Streamlit app with glassmorphism, animated waveforms, rotating rings |
| **CLI Interface** | Terminal-based register / lock / unlock / reset loop |
| **Audit Logging** | Every auth attempt logged with timestamp and similarity score |

---

## Tech Stack

| Component | Library / Tool | Role |
|---|---|---|
| Deep Learning | SpeechBrain ECAPA-TDNN | 192-dim speaker embedding extraction |
| Audio Recording | `sounddevice` + `scipy` | Microphone capture (6s, 16 kHz, mono) |
| Audio Processing | `librosa`, `torchaudio` | Audio loading and feature computation |
| Noise Reduction | `noisereduce` | Wiener-filter stationary noise removal |
| Similarity | `scikit-learn` | Cosine similarity scoring |
| Encryption | `cryptography.Fernet` (AES-256) | File encryption and decryption at rest |
| Embedding Storage | `numpy` (.npy) | Voice profile serialization |
| Web UI | `streamlit` | 7-page interactive dashboard |
| Config | `pyyaml` | YAML-based runtime settings |
| Logging | `csv`, `json` | Auth log + activity feed |

---

## Project Structure

```
Voice-Based-Authentication-Using-Deep-Learning/
│
├── configs/
│   └── config.yaml                   # Audio, paths, threshold settings
│
├── data/
│   ├── raw_audio/                    # Raw .wav from mic (UUID filenames)
│   ├── processed_audio/              # Noise-reduced .wav (UUID filenames)
│   ├── embeddings/                   # .npy voice embeddings (one per sample)
│   ├── profile/
│   │   ├── user_profile.npy          # Averaged voice profile (identity anchor)
│   │   ├── single_user.json          # { name, phrase, registered, photo }
│   │   ├── users.json                # CLI user database
│   │   └── activity_log.json         # In-app activity feed entries
│   ├── locked_file/                  # AES-256 encrypted .enc files
│   ├── security/
│   │   └── key.key                   # Fernet encryption key (auto-generated)
│   └── logs/
│       └── auth_log.csv              # timestamp, score, result
│
├── models/
│   └── speaker_model/                # ECAPA-TDNN model cache (auto-downloaded)
│       └── classifier.pth            # Legacy linear classifier weights
│
├── src/
│   ├── audio/
│   │   ├── recorder.py               # Microphone capture via sounddevice
│   │   └── preprocess.py             # Noise reduction via noisereduce
│   ├── features/
│   │   └── extract_features.py       # ECAPA-TDNN 192-dim embedding extraction
│   ├── model/
│   │   ├── profile_manager.py        # update / load / reset voice profile
│   │   ├── verify_voice.py           # Cosine similarity auth decision
│   │   └── ecapa_classifier.py       # Legacy linear classifier
│   ├── security/
│   │   ├── antispoof.py              # Spectral flatness + ZCR spoof detection
│   │   └── encryption.py             # AES-256 Fernet encrypt / decrypt
│   ├── learning/
│   │   └── continual_learning.py     # save_embedding / save_multiple_embeddings
│   ├── evaluation/
│   │   ├── logger.py                 # Append auth events to CSV
│   │   └── metrics.py                # FAR, FRR computation + scatter plot
│   ├── main.py                       # CLI entry point (5-option menu)
│   └── streamlit_app.py              # Streamlit web app v2.1 (7 pages)
│
├── requirements.txt                  # Python dependencies (13 packages)
├── project.md                        # 10-phase development roadmap
└── Structure.md                      # Full architecture documentation
```

---

## System Architecture

### Registration Flow (5 Voice Samples)

```
User enters Name + Phrase → clicks "Begin Voice Registration"
          │
          ▼  [repeated 5 times]
[recorder.py]     → sounddevice.rec(6s, 16kHz, mono)
                  → data/raw_audio/<uuid>.wav
          │
          ▼
[preprocess.py]   → noisereduce.reduce_noise()
                  → data/processed_audio/<uuid>.wav
          │
          ▼
[extract_features.py]  → ECAPA-TDNN encode_batch()
                       → 192-dim numpy embedding
          │
          ▼  [after all 5 collected]
[save_multiple_embeddings()]
          → saves 5× data/embeddings/<uuid>.npy
          → update_profile()
          → mean(5 embeddings) → data/profile/user_profile.npy

[save_user({name, phrase, registered})]
          → data/profile/single_user.json
```

### Authentication Flow (Login / Unlock)

```
User clicks "Record Voice"
          │
          ▼
[recorder.py] → raw .wav (6 seconds)
          │
          ▼
[preprocess.py] → cleaned .wav
          │
          ▼
[antispoof.detect_spoof()]
   flatness > 0.5 OR zcr < 0.01?
          │ YES → SPOOF → return False
          │ NO (genuine)
          ▼
[extract_features.py] → 192-dim embedding
          │
          ▼
[verify_voice(emb)]
   score = cosine_similarity(emb, user_profile)
   score >= threshold (from config.yaml)?
          │ YES → voice_ok = True
          │ NO  → voice_ok = False
          ▼
User types their secret phrase
   phrase.lower() == stored_phrase.lower()?
          │ YES → phrase_ok = True
          │ NO  → phrase_ok = False
          ▼
voice_ok AND phrase_ok?
   YES → ACCESS GRANTED → decrypt files / login
   NO  → ACCESS DENIED → log failure
```

### Encryption Flow

```
LOCK:  upload → save temp → encrypt_file(temp, temp.enc) → delete temp
       Vault stores: <filename>.enc (ciphertext only)

UNLOCK (after auth passes):
       decrypt_file(.enc, unlocked_<filename>) → download button
```

---

## Module Descriptions

### `src/audio/recorder.py`
Captures 6 seconds of mono audio at 16 kHz from the system microphone using `sounddevice.rec()`. Each recording is saved with a UUID filename to `data/raw_audio/`. Returns the file path.

### `src/audio/preprocess.py`
Loads raw audio via `librosa.load(sr=16000)`, applies `noisereduce.reduce_noise()` (Wiener-filter-based stationary noise removal), and saves the cleaned result to `data/processed_audio/`.

### `src/features/extract_features.py`
The core deep learning module. Loads **SpeechBrain ECAPA-TDNN** at import time and exposes `extract_features(file_path)` which returns a 192-dimensional numpy embedding.

**ECAPA-TDNN** (Emphasized Channel Attention, Propagation and Aggregation in TDNN):
- Dilated 1D convolutions capture temporal speech patterns at multiple time scales
- SE-Res2Net blocks provide channel attention and multi-scale feature aggregation
- Attentive statistics pooling collapses the time axis into a fixed-length vector
- Output: 192-float x-vector encoding pitch, formants, vocal tract shape, and speaking rhythm

### `src/model/profile_manager.py`
Three functions manage the voice profile lifecycle:
- **`update_profile()`** — scans `data/embeddings/` for all `.npy` files, computes element-wise mean, saves to `user_profile.npy`
- **`load_profile()`** — loads `user_profile.npy`; returns `None` if missing/corrupted
- **`reset_profile()`** — deletes `user_profile.npy` and all `.npy` files in `data/embeddings/`

### `src/model/verify_voice.py`
Single-user cosine similarity verification:
```python
score = cosine_similarity(emb, profile)   # range [-1, 1]
threshold = config["model"]["threshold"]  # default 0.75 fallback
return (score >= threshold), float(score)
```
No classifier is used — authentication is purely embedding similarity + phrase check.

### `src/security/antispoof.py`
Lightweight heuristic replay detection:
- **Spectral Flatness** > 0.5 → replay detected (signal becomes noise-like through speakers)
- **Zero Crossing Rate** < 0.01 → spoof detected (DC-shifted or near-silent playback)

### `src/security/encryption.py`
AES-256 file encryption using `cryptography.Fernet`:
- **`generate_key()`** — creates a 256-bit random key on first run → `data/security/key.key`
- **`encrypt_file(input, output)`** — reads file, encrypts with Fernet, writes `.enc`
- **`decrypt_file(input, output)`** — reads `.enc`, decrypts, writes plaintext

> ⚠️ Losing `data/security/key.key` = permanently losing access to all encrypted files.

### `src/learning/continual_learning.py`
- **`save_embedding(emb, update=True)`** — saves single `.npy` + optionally recomputes profile
- **`save_multiple_embeddings(embeddings)`** — saves all 5 registration samples, calls `update_profile()` once

### `src/evaluation/logger.py`
Appends `[timestamp, score, result]` to `data/logs/auth_log.csv` after each auth attempt.

### `src/evaluation/metrics.py`
Reads `auth_log.csv` and computes FAR/FRR at threshold 0.65; generates a scatter plot of score vs. decision.

### `src/main.py` — CLI Interface
5-option terminal menu: **Register** (5 samples + username + phrase), **Lock** (auth → encrypt file), **Unlock** (auth → decrypt + select file), **Reset** (wipe profile), **Exit**.

### `src/streamlit_app.py` — Web Application (v2.1)
1235-line cyberpunk-themed Streamlit app with 7 navigable pages:

| Page | Access | Function |
|---|---|---|
| **👤 Register** | Always | Enter name + phrase + optional photo → record 5 voice samples |
| **🔑 Login** | Registered, not logged in | Voice scan + phrase → session activated |
| **🏠 Dashboard** | Logged in | Profile card, security status, vault summary, activity feed |
| **🔒 Lock File** | Logged in | Upload file → AES-256 encrypt → stored as `.enc` |
| **🔓 Unlock File** | Logged in | Voice + phrase → decrypt all `.enc` → download buttons |
| **✏️ Edit Profile** | Logged in | Change name/phrase/photo; re-record voice samples |
| **🔄 Reset Profile** | Logged in | Voice-gated destructive action — wipes everything |

**UI Design:** Orbitron/Rajdhani/Share Tech Mono fonts, glassmorphism cards, animated grid background, rotating security rings, score progress bars, waveform animation, sidebar with session status.

---

## How It Works

### First-Time Setup
1. Open app → **Register** page appears
2. Enter Full Name, Unlock Phrase, optional profile photo
3. Click "Begin Voice Registration"
4. Speak clearly 5 times (6 seconds each) — waveform animation plays during recording
5. Each sample: recorded → noise-reduced → ECAPA embedding extracted
6. 5 embeddings saved → mean computed → voice profile stored
7. Redirected to **Login** page

### Logging In
1. **Login** page shows two steps
2. **Step 1:** Click "Record Voice" → speak → anti-spoof check → cosine similarity computed → score shown
3. **Step 2:** Type your secret phrase
4. Click "Confirm & Login" → if voice AND phrase match → session activated → redirected to **Dashboard**

### Locking a File
1. **Lock File** page → upload any file (PDF, image, doc, etc.)
2. Click "Encrypt & Lock File"
3. File saved temporarily → `encrypt_file(temp, temp.enc)` → temp deleted
4. `.enc` stored in vault — plaintext never persists on disk
5. Vault contents displayed below

### Unlocking Files
1. **Unlock File** page
2. **Step 1:** Record voice → cosine similarity score displayed
3. **Step 2:** Type unlock phrase
4. Click "Confirm & Decrypt Files" → all `.enc` files decrypted → download buttons appear
5. Activity logged

### Resetting Profile
1. **Reset Profile** page — shows danger warning
2. **Step 1:** Voice authentication required
3. **Step 2:** Type unlock phrase to confirm
4. Click "DELETE & Reset Everything" → profile, embeddings, locked files, logs all wiped
5. App returns to registration state

---

## Security Design

### Three-Layer Authentication

```
Layer 1: Anti-Spoofing (signal analysis)
  spectral_flatness > 0.5 → REJECT (replay detected)
  zcr < 0.01              → REJECT (unnatural signal)

Layer 2: Voice Biometric (neural matching)
  cosine_similarity(live_emb, profile) >= threshold → PASS

Layer 3: Secret Phrase (knowledge factor)
  user_input.lower() == stored_phrase.lower() → PASS

All 3 must pass → ACCESS GRANTED
Any layer fails  → ACCESS DENIED
```

**Two-factor authentication:**
- **Something you are** — your voice (biometric)
- **Something you know** — your unlock phrase (knowledge)

### AES-256 File Encryption

| Aspect | Detail |
|---|---|
| Algorithm | AES-128-CBC + HMAC-SHA256 (Fernet wrapper) |
| Key | 256-bit random, generated once, stored at `data/security/key.key` |
| File format | `.enc` — ciphertext with authentication tag |
| Plaintext | Deleted immediately after encryption (`os.remove`) |
| Decryption | Only triggered after full voice + phrase authentication |

### Session Management
- Login creates `st.session_state["logged_in"] = True`
- Locked pages (Dashboard, Lock, Unlock, Edit, Reset) require active session
- Logout clears session state and redirects to Login
- Reset page requires re-authentication even within active session

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- Working microphone
- ~500 MB disk (for ECAPA-TDNN model download)

### Steps
```bash
# 1. Clone
git clone https://github.com/yourusername/Voice-Based-Authentication-Using-Deep-Learning.git
cd "Voice-Based-Authentication-Using-Deep-Learning"

# 2. Virtual environment
python3 -m venv .venv
source .venv/bin/activate        # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch Streamlit (recommended)
cd src
streamlit run streamlit_app.py   # → http://localhost:8501

# 5. Or use CLI
cd src
python main.py
```

### `requirements.txt`
```
streamlit
numpy
scikit-learn
librosa
noisereduce
sounddevice
scipy
soundfile
pyyaml
speechbrain
torch
torchaudio
cryptography
```

### First Run
- ECAPA-TDNN model (~500 MB) auto-downloads from HuggingFace Hub on first import
- Encryption key auto-generated at `data/security/key.key` on first lock
- All `data/` subdirectories created automatically

### macOS
System Settings → Privacy & Security → Microphone → allow Terminal / IDE.

---

## Configuration

`configs/config.yaml`:
```yaml
audio:
  sample_rate: 16000    # Hz — speech model standard
  duration: 6           # seconds per recording

paths:
  raw_audio: data/raw_audio
  processed_audio: data/processed_audio
  embeddings: data/embeddings

model:
  threshold: 0.60       # cosine similarity threshold (code fallback: 0.75)
```

### Threshold Tuning

| Value | Security | Usability | Recommended For |
|---|---|---|---|
| 0.85+ | Very High | More false rejections | High-security use |
| 0.75 | High | Balanced | General use (code default) |
| 0.60 | Medium | Fewer rejections | Noisy environments (config default) |

---

## Usage

### Streamlit App Pages

**Before login:** Register → Login  
**After login:** Dashboard → Lock File → Unlock File → Edit Profile → Reset Profile

| Action | Steps |
|---|---|
| **Register** | Name + phrase + photo → speak 5× → profile created |
| **Login** | Record voice → type phrase → session activated |
| **Lock** | Upload file → click Encrypt → `.enc` stored in vault |
| **Unlock** | Record voice → type phrase → download decrypted files |
| **Edit** | Change name/phrase/photo; re-record voice with expander |
| **Reset** | Voice auth + phrase → deletes everything → back to register |

### CLI

```
$ python src/main.py

==== Voice Locker · SecureVault ====
1. Register
2. Lock
3. Unlock
4. Reset
5. Exit

Choice: 1
Enter username: alice
Set unlock phrase: open sesame
🎤 Recording 5 voice samples...
✅ User registered!

Choice: 2
[authenticates] → Enter file path: /path/to/report.pdf
🔒 Saved as data/locked_file/alice_report.pdf.enc

Choice: 3
[authenticates] → select file → ✅ Decrypted
```

---

## Evaluation & Metrics

### Log Format
```csv
# data/logs/auth_log.csv
timestamp,score,result
2026-04-25 10:00:01,0.8312,accept
2026-04-25 10:05:44,0.4210,reject
```

### Metrics

| Metric | Meaning | Target |
|---|---|---|
| **FAR** (False Accept Rate) | Impostor attempts incorrectly accepted | < 1% |
| **FRR** (False Reject Rate) | Genuine attempts incorrectly rejected | < 5% |

```bash
cd src && python -c "from evaluation.metrics import compute_metrics; compute_metrics()"
```

---

## Limitations & Future Work

| Limitation | Detail | Planned Fix |
|---|---|---|
| Single user only | One voice profile per installation | Multi-user with per-user keys |
| Basic anti-spoofing | ZCR/flatness won't stop AI voice cloning | Deep learning spoof detector |
| Local key storage | `key.key` on disk — loss = permanent data loss | Secure key derivation / cloud backup |
| Phrase stored plaintext | `single_user.json` stores phrase as-is | Hashed phrase comparison |
| Noise sensitivity | Very loud environments reduce accuracy | Advanced noise suppression |
| No cross-device sync | Embeddings and key are local only | Cloud profile + key management |

---

## Development Roadmap

| Phase | Status | Description |
|---|---|---|
| **1** — Foundation & Audio | ✅ Done | `recorder.py`, `preprocess.py`, project setup |
| **2** — Deep Learning | ✅ Done | ECAPA-TDNN integration, embedding extraction |
| **3** — Verification & Profiles | ✅ Done | Cosine similarity, profile averaging, single-user |
| **4** — Security & Adaptation | ✅ Done | Anti-spoofing, continual learning, AES-256 encryption |
| **5** — UI v2.1 & Logging | ✅ Done | 7-page Streamlit app, login sessions, activity feed, CLI |
| **6** — Advanced Metrics | 🔲 Planned | EER, ROC curves, noise robustness testing |
| **7** — Testing & QA | 🔲 Planned | pytest suite, VoxCeleb benchmark |
| **8** — UI Polish | 🔲 Planned | Real-time spectrogram, live waveform during recording |
| **9** — Standout Features | 🔲 Planned | DL anti-spoof, secure key derivation, multi-modal auth |
| **10** — Deployment | 🔲 Planned | Docker, Streamlit Cloud / AWS |

---

## References

| Resource | Link |
|---|---|
| ECAPA-TDNN Paper | [Desplanques et al. (2020)](https://arxiv.org/abs/2005.07143) |
| SpeechBrain | [speechbrain.github.io](https://speechbrain.github.io) |
| VoxCeleb Dataset | [robots.ox.ac.uk/~vgg/data/voxceleb](https://www.robots.ox.ac.uk/~vgg/data/voxceleb/) |
| Python Cryptography (Fernet) | [cryptography.io/en/latest/fernet](https://cryptography.io/en/latest/fernet/) |
| Librosa | [librosa.org/doc](https://librosa.org/doc/) |
| Noisereduce | [github.com/timsainb/noisereduce](https://github.com/timsainb/noisereduce) |
| Streamlit | [docs.streamlit.io](https://docs.streamlit.io) |

---

*Voice-Based Authentication Using Deep Learning | Semester 4 | Last updated: April 2026*
