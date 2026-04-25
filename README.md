# 🎙️ Voice-Based Authentication Using Deep Learning — VoiceLock

> A single-user biometric security system that uses your voice as the key, with AES-256 file encryption built in.

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
- [Limitations](#limitations)
- [Development Roadmap](#development-roadmap)
- [References](#references)

---

## Overview

**VoiceLock** is a single-user biometric security system that replaces traditional passwords with **speaker verification technology**. Instead of typing a password, you speak — the system extracts a deep neural fingerprint from your voice and uses it to control access to your encrypted files.

The system uses **SpeechBrain's ECAPA-TDNN** model (pre-trained on VoxCeleb) to generate a unique 192-dimensional embedding from audio. This embedding is compared against your stored voice profile using **cosine similarity** to grant or deny access. All locked files are encrypted on disk with **AES-256 (Fernet)** and only decrypted when voice authentication succeeds.

---

## Problem Statement

Traditional authentication is broken in key ways:
- Passwords can be stolen, phished, or forgotten
- PINs prove possession of a secret, not true identity
- No credential proves **who** the person actually is

**Voice biometrics** authenticates the user's inherent vocal characteristics — unique to every person, impossible to forget, and very hard to replicate. VoiceLock solves the additional challenges voice systems face:

| Challenge | Our Solution |
|---|---|
| Replay attacks | Spectral flatness + ZCR anti-spoofing detection |
| Background noise | `noisereduce` Wiener-filter preprocessing |
| Voice drift over time | Continual learning — profile updates after every successful login |
| File security at rest | AES-256 encryption via `cryptography.Fernet` |

---

## Key Features

| Feature | Description |
|---|---|
| **Single-User Registration** | Record 5 voice samples + set a secret unlock phrase |
| **Voice Authentication** | Cosine similarity against averaged profile + phrase match |
| **Anti-Spoofing** | Spectral flatness + ZCR signal analysis catches replay attacks |
| **AES-256 Encryption** | All locked files encrypted on disk; decrypted only on auth success |
| **Continual Learning** | Profile auto-updates after every successful authentication |
| **Profile Reset** | One-click wipe of all embeddings and profile for re-registration |
| **Premium Web UI** | Cyberpunk-themed Streamlit app with glassmorphism, animated waveforms |
| **Audit Logging** | Every auth attempt logged with timestamp and similarity score |
| **Performance Metrics** | FAR/FRR computation from log history |
| **CLI Interface** | Terminal-based register/authenticate loop |

---

## Tech Stack

| Component | Library / Tool | Role |
|---|---|---|
| Deep Learning Model | SpeechBrain ECAPA-TDNN | 192-dim speaker embedding extraction |
| Audio Recording | `sounddevice` + `scipy` | Microphone capture |
| Audio Loading | `torchaudio`, `librosa` | File-based audio processing |
| Noise Reduction | `noisereduce` | Wiener-filter stationary noise removal |
| Feature Extraction | `torch`, `speechbrain` | ECAPA-TDNN inference |
| Similarity Metric | `scikit-learn` | Cosine similarity scoring |
| Embedding Storage | `numpy` (.npy files) | Profile serialization |
| Encryption | `cryptography.Fernet` (AES-256) | File encryption at rest |
| Web UI | `streamlit` | Interactive dashboard |
| Configuration | `pyyaml` | YAML-based settings |
| Logging | `csv`, `datetime` | Authentication audit trail |
| Analysis | `pandas`, `matplotlib` | Metrics and visualization |

---

## Project Structure

```
Voice-Based-Authentication-Using-Deep-Learning/
│
├── configs/
│   └── config.yaml                   # Audio settings, paths, threshold
│
├── data/
│   ├── raw_audio/                    # Raw .wav recordings (UUID filenames)
│   ├── processed_audio/              # Noise-reduced .wav files (UUID filenames)
│   ├── embeddings/                   # .npy voice embedding files (one per sample)
│   ├── profile/
│   │   ├── user_profile.npy          # Averaged voice profile (identity anchor)
│   │   └── single_user.json          # { name, phrase } for the registered user
│   ├── locked_file/                  # AES-256 encrypted files (.enc extension)
│   └── security/
│       └── key.key                   # Fernet encryption key (auto-generated)
│
├── models/
│   └── speaker_model/               # ECAPA-TDNN model cache (auto-downloaded)
│       └── classifier.pth            # Trained linear classifier weights
│
├── src/
│   ├── audio/
│   │   ├── recorder.py               # Microphone capture via sounddevice
│   │   └── preprocess.py             # Noise reduction + format normalization
│   ├── features/
│   │   └── extract_features.py       # ECAPA-TDNN 192-dim embedding extraction
│   ├── model/
│   │   ├── profile_manager.py        # Load/update/reset voice profile (.npy)
│   │   ├── verify_voice.py           # Cosine similarity authentication decision
│   │   └── ecapa_classifier.py       # PyTorch linear classifier (legacy)
│   ├── security/
│   │   ├── antispoof.py              # Spectral flatness + ZCR spoof detection
│   │   └── encryption.py             # AES-256 encrypt/decrypt via Fernet
│   ├── learning/
│   │   └── continual_learning.py     # Save embeddings; batch-save for registration
│   ├── evaluation/
│   │   ├── logger.py                 # Append auth events to auth_log.csv
│   │   └── metrics.py                # FAR, FRR, scatter plot
│   ├── main.py                       # CLI interface (Register/Authenticate/Exit)
│   └── streamlit_app.py              # Full web application (cyberpunk UI)
│
├── requirements.txt
├── project.md                        # 10-phase development roadmap
└── Structure.md                      # Full architecture documentation
```

---

## System Architecture

### Registration Flow (5 Voice Samples)

```
User speaks 5 times (6 seconds each)
          │
          ▼  [for each sample]
[recorder.py]
  sounddevice.rec() → data/raw_audio/<uuid>.wav
          │
          ▼
[preprocess.py]
  librosa.load() + noisereduce() → data/processed_audio/<uuid>.wav
          │
          ▼
[extract_features.py]
  ECAPA-TDNN encode_batch() → 192-dim embedding
          │
          ▼  [collect all 5 embeddings]
[continual_learning.save_multiple_embeddings()]
  saves each as data/embeddings/<uuid>.npy
          │
          ▼
[profile_manager.update_profile()]
  mean of all 5 embeddings → data/profile/user_profile.npy

[save_user(name, phrase)]
  → data/profile/single_user.json
```

### Authentication (Unlock) Flow

```
User clicks "Authenticate & Unlock"
          │
          ▼
[recorder.py] → raw .wav (6 seconds)
          │
          ▼
[preprocess.py] → cleaned .wav
          │
          ▼
[antispoof.detect_spoof()]
  ├── spectral_flatness > 0.5? ──► SPOOF → REJECT
  └── zcr < 0.01?              ──► SPOOF → REJECT
          │ GENUINE
          ▼
[extract_features.py] → 192-dim embedding
          │
          ▼
[verify_voice.verify_voice(emb)]
  cosine_similarity(emb, user_profile) → score
  score >= threshold? (from config.yaml)
          │
  ┌───────┴───────┐
  │ YES           │ NO
  ▼               ▼
score shown    REJECTED
          │
          ▼
User types their secret phrase
phrase == stored phrase?
  │ YES           │ NO
  ▼               ▼
ACCESS GRANTED  REJECTED
          │
          ▼
[encryption.decrypt_file()] → unlocked_<filename>
Download button shown
```

### Encryption Flow

```
LOCK:
  Upload file → save as temp → encrypt_file(temp, temp.enc)
              → delete temp  → vault stores <filename>.enc

UNLOCK:
  Auth passes → decrypt_file(<filename>.enc, unlocked_<filename>)
              → stream to browser download → temp unlocked file
```

---

## Module Descriptions

### `src/audio/recorder.py`
Captures 6 seconds of mono audio from the system microphone:
- Reads `duration` and `sample_rate` from `config.yaml`
- Uses `sounddevice.rec()` + `sd.wait()` for blocking capture
- Saves to `data/raw_audio/<uuid>.wav` via `scipy.io.wavfile.write`
- Returns the file path

**Why 16 kHz?** Speech energy lives below 8 kHz; Nyquist theorem requires 2× = 16 kHz, which is the universal standard for speech models.

---

### `src/audio/preprocess.py`
Cleans raw audio before the neural model processes it:
- `librosa.load(sr=16000)` — loads and resamples to float32
- `noisereduce.reduce_noise()` — Wiener-filter stationary noise removal
- Saves cleaned audio to `data/processed_audio/<uuid>.wav`
- Returns processed file path

---

### `src/features/extract_features.py`
Core deep learning module. Loads **SpeechBrain ECAPA-TDNN** at import:

```python
verification = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="models/speaker_model"
)
```

`extract_features(file_path)`:
1. `torchaudio.load()` → waveform tensor `[channels, samples]`
2. Convert to mono if stereo (`torch.mean` on channel dim)
3. `verification.encode_batch(signal)` → runs ECAPA-TDNN
4. Returns `embedding.numpy()` — shape `[1, 1, 192]`

**ECAPA-TDNN internals:**
- Dilated 1D convolutions capture temporal patterns at scales 1→4
- SE-Res2Net blocks: channel attention + multi-scale aggregation
- Attentive statistics pooling collapses the time axis
- Output: 192-float vector encoding pitch, formants, vocal tract shape

---

### `src/model/profile_manager.py`
Manages the single-user voice profile:

| Function | What It Does |
|---|---|
| `update_profile()` | Scans `data/embeddings/`, stacks all `.npy` files, computes element-wise mean → saves `user_profile.npy` |
| `load_profile()` | Loads `user_profile.npy`; returns `None` if missing or corrupted |
| `reset_profile()` | Deletes `user_profile.npy` and all `.npy` files in `data/embeddings/` |

**Why average N embeddings?** Each recording varies slightly (energy, distance from mic, phrasing). Averaging 5 registration samples creates a centroid in 192-dim space that is robust to these natural variations.

---

### `src/model/verify_voice.py`
The authentication decision engine (updated for single-user):

```python
def verify_voice(emb, user_id=None):
    profile = load_profile()          # Load user_profile.npy
    emb     = np.array(emb).squeeze() # [192]
    profile = np.array(profile).squeeze()

    score = cosine_similarity(emb.reshape(1,-1), profile.reshape(1,-1))[0][0]

    threshold = config["model"]["threshold"]   # from config.yaml (default 0.75)

    return (score >= threshold), float(score)
```

**Key change from old version:** The `ECAPAClassifier` (speaker class lookup) has been removed. Authentication is now **purely cosine similarity** against the stored averaged profile, plus the **secret phrase check** in the UI layer.

---

### `src/security/antispoof.py`
Lightweight acoustic heuristic to catch replay attacks before embedding extraction:

```python
def detect_spoof(audio_file):
    y, sr = librosa.load(audio_file, sr=16000)
    flatness = np.mean(librosa.feature.spectral_flatness(y=y))
    zcr      = np.mean(librosa.feature.zero_crossing_rate(y))
    if flatness > 0.5 or zcr < 0.01:
        return True   # SPOOF DETECTED
    return False
```

| Feature | What It Measures | Live Speech | Replay Signal |
|---|---|---|---|
| Spectral Flatness | Tonal vs noise-like spectrum | Low (< 0.5) | High (> 0.5) |
| Zero Crossing Rate | Signal sign-change frequency | Moderate (> 0.01) | Very low (< 0.01) |

---

### `src/security/encryption.py`
**AES-256 file encryption using Python's `cryptography.Fernet`.**

Fernet is a symmetric encryption scheme built on AES-128-CBC with HMAC-SHA256 authentication — effectively AES-256-level security in a simple API.

```python
KEY_PATH = "data/security/key.key"

def generate_key():
    key = Fernet.generate_key()   # 256-bit random key
    with open(KEY_PATH, "wb") as f:
        f.write(key)

def encrypt_file(input_path, output_path):
    cipher = Fernet(load_key())
    data   = open(input_path, "rb").read()
    open(output_path, "wb").write(cipher.encrypt(data))   # saves as .enc

def decrypt_file(input_path, output_path):
    cipher = Fernet(load_key())
    data   = open(input_path, "rb").read()
    open(output_path, "wb").write(cipher.decrypt(data))
```

**Key lifecycle:**
1. On first run, `generate_key()` creates a 256-bit random key → `data/security/key.key`
2. The key persists between sessions (same key encrypts and decrypts)
3. Losing `key.key` = **permanently losing access** to all encrypted files

**Lock flow:** File uploaded → saved as temp → `encrypt_file(temp, temp.enc)` → temp deleted → `.enc` stored in vault  
**Unlock flow:** Auth passes → `decrypt_file(.enc, unlocked_file)` → streamed as download

---

### `src/learning/continual_learning.py`
Manages embedding persistence:

```python
def save_embedding(embedding, update=True):
    # Saves single .npy; optionally calls update_profile()
    # Used after successful authentication (continual learning)

def save_multiple_embeddings(embeddings):
    # Saves all 5 registration embeddings, then calls update_profile() once
    # More efficient than calling update_profile() 5 times
```

**Continual learning effect:** After every successful login, the new embedding is added to `data/embeddings/`, and the profile mean is recomputed. Over time, the profile centroid becomes more representative of the user's actual voice in real conditions.

---

### `src/evaluation/logger.py`
Appends one row per auth attempt to `data/logs/auth_log.csv`:
```
timestamp, score, result
2026-04-25 10:00:01, 0.8312, accept
2026-04-25 10:05:44, 0.4210, reject
```

---

### `src/evaluation/metrics.py`
Reads `auth_log.csv` and computes metrics at threshold 0.65:
- **FAR** — rejected rows with score > threshold (near-misses by impostors)
- **FRR** — accepted rows with score ≤ threshold (near-misses by genuine user)
- Scatter plot of score vs. decision for visual threshold tuning

---

### `src/main.py` — CLI Interface
```
python src/main.py

1 → Register Voice
      record → preprocess → extract → save_multiple_embeddings → update_profile

2 → Authenticate Voice
      record → preprocess → antispoof
      → extract → verify_voice
      → if granted: save_embedding + log_auth("accept")
      → if denied:  log_auth("reject")

3 → Exit
```

---

### `src/streamlit_app.py` — Web Application
A cyberpunk-themed Streamlit app with glassmorphism cards, animated waveforms, rotating security rings, and a sidebar navigation.

**Three pages (sidebar radio):**

| Page | What Happens |
|---|---|
| 👤 **Profile** | First run: enter Name + Unlock Phrase → record 5 voice samples → profile built. Already registered: shows Status/Encryption/Anti-Spoof status cards + Reset button |
| 🔒 **Lock File** | Upload any file → click "Encrypt & Lock File" → `encrypt_file()` → `.enc` stored in vault |
| 🔓 **Unlock File** | Click "Authenticate & Unlock" → speak into mic → antispoof + cosine similarity + phrase check → if pass: `decrypt_file()` for every `.enc` in vault → download buttons appear |

**Single-user data store:**
```json
// data/profile/single_user.json
{ "name": "Alice", "phrase": "open the vault" }
```
No user ID, no multi-user isolation — one profile, one person.

---

## How It Works

### Step-by-Step: First-Time Registration

```
1. Open app → Profile tab
2. Enter your Full Name and a secret Unlock Phrase
3. Click "Begin Voice Registration"
4. Speak clearly 5 times (6 seconds each)
   → Each sample: recorded → noise-reduced → ECAPA embedding extracted
   → 5 embeddings saved to data/embeddings/
   → Mean of all 5 saved to data/profile/user_profile.npy
   → Name + phrase saved to data/profile/single_user.json
5. "Voice profile registered successfully!" shown
```

### Step-by-Step: Locking a File

```
1. Go to Lock File tab
2. Upload any file (PDF, image, doc, video, etc.)
3. Click "Encrypt & Lock File"
   → File saved temporarily
   → encrypt_file(temp_path, temp_path + ".enc")
   → Original (plain) file deleted
   → Encrypted .enc stored in data/locked_file/
4. "File encrypted and stored in the vault" shown
```

### Step-by-Step: Unlocking a File

```
1. Go to Unlock File tab
2. Click "Authenticate & Unlock"
3. Speak into microphone for 6 seconds
   → Anti-spoof check (spectral flatness + ZCR)
   → ECAPA-TDNN embedding extracted
   → Cosine similarity computed against user_profile.npy
   → Similarity score shown as progress bar
4. Type your secret unlock phrase
5. If score >= threshold AND phrase matches:
   → SUCCESS: All .enc files in vault are decrypted
   → Download buttons appear for each file
6. If voice or phrase fails:
   → "Authentication Failed — Voice or phrase mismatch"
```

---

## Security Design

### Three-Layer Authentication

```
Layer 1: Anti-Spoofing (signal analysis)
  spectral_flatness > 0.5 → REJECT (replay detected)
  zcr < 0.01             → REJECT (unnatural signal)

Layer 2: Voice Biometric (neural matching)
  cosine_similarity(live_emb, profile) >= threshold → PASS

Layer 3: Secret Phrase (knowledge factor)
  user_input.lower() == stored_phrase.lower() → PASS

All 3 must pass → ACCESS GRANTED
Any fails       → ACCESS DENIED
```

This is effectively **multi-factor authentication**:
- **Something you are** — your voice (biometric)
- **Something you know** — your unlock phrase (knowledge)

### AES-256 File Encryption

Files are **never stored in plaintext** in the vault:

```
Vault contents:
  data/locked_file/report.pdf.enc     ← encrypted
  data/locked_file/photo.jpg.enc      ← encrypted
  data/security/key.key               ← encryption key
```

The key is generated once with `Fernet.generate_key()` (256-bit random) and stored locally. Without both the key AND the authentication passing, the `.enc` files cannot be decrypted.

> ⚠️ **Important:** Back up `data/security/key.key`. If it is lost or deleted, all encrypted files are permanently inaccessible.

### Anti-Spoofing Details

| Attack Type | How It's Caught |
|---|---|
| Replay (speaker playback) | High spectral flatness (signal becomes noise-like through speaker) |
| DC-offset / muffled recording | Very low ZCR (signal rarely crosses zero) |
| Static recording attack | Phrase check — static recordings can't respond to "say your phrase" |

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- Working microphone
- ~500 MB disk space (ECAPA-TDNN model download)
- macOS / Linux / Windows

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/Voice-Based-Authentication-Using-Deep-Learning.git
cd "Voice-Based-Authentication-Using-Deep-Learning"
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate       # macOS / Linux
# .venv\Scripts\activate        # Windows
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt`:
```
numpy
librosa
sounddevice
scipy
scikit-learn
speechbrain
torch
torchaudio
noisereduce
pyyaml
streamlit
cryptography
```

### 4. macOS Microphone Permission
**System Settings → Privacy & Security → Microphone** → allow Terminal / your IDE.

### 5. Launch

**Streamlit Web App (recommended):**
```bash
cd src
streamlit run streamlit_app.py
# Opens at http://localhost:8501
```

**CLI:**
```bash
cd src
python main.py
```

### 6. First-Time Model Download
On the very first run, SpeechBrain automatically downloads the ECAPA-TDNN model (~500 MB) from HuggingFace Hub into `models/speaker_model/`. This happens once and is cached.

To pre-download manually:
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

---

## Configuration

All settings live in `configs/config.yaml`:

```yaml
audio:
  sample_rate: 16000    # Hz — standard for speech models
  duration: 6           # seconds captured per recording

paths:
  raw_audio: data/raw_audio
  processed_audio: data/processed_audio
  embeddings: data/embeddings

model:
  threshold: 0.75       # cosine similarity threshold for authentication
```

### Threshold Tuning Guide

| Threshold | Security | Usability | Recommended For |
|---|---|---|---|
| `0.85+` | Very High | Lower (more rejections) | High-security environments |
| `0.75` | High | Balanced | **Default — recommended** |
| `0.65` | Medium | Higher (more accepts) | Noisy microphone environments |
| `< 0.60` | Low | Very High | Testing only |

---

## Usage

### Streamlit Web App

**Sidebar navigation:**
- **👤 Profile** — register or manage your voice profile
- **🔒 Lock File** — upload and encrypt files into the vault
- **🔓 Unlock File** — authenticate and decrypt vault files

**First use:**
1. Go to Profile → enter Name + Unlock Phrase → speak 5 times
2. Go to Lock File → upload file → click Encrypt & Lock
3. Go to Unlock File → click Authenticate → speak → type phrase → download

**Reset profile** (if you want to re-register):
- Go to Profile tab (while registered) → click "Reset Profile & Re-register"
- All embeddings and profile are deleted; app returns to registration state

### CLI

```
$ python src/main.py

1 Register Voice
2 Authenticate Voice
3 Exit

Enter choice: 1
Speak now...
[records 5 samples for registration]
Voice registered successfully

Enter choice: 2
Speak now...
Similarity Score: 0.8712
Access Granted
```

### Run Evaluation Metrics
```bash
cd src
python -c "from evaluation.metrics import compute_metrics; compute_metrics()"
```

---

## Evaluation & Metrics

### Log File Schema
```
data/logs/auth_log.csv
──────────────────────────────────────
timestamp            | score  | result
──────────────────────────────────────
2026-04-25 10:00:01  | 0.8312 | accept
2026-04-25 10:05:44  | 0.4210 | reject
```

### Biometric Performance Metrics

| Metric | Formula | Target | Meaning |
|---|---|---|---|
| **FAR** (False Accept Rate) | Impostors accepted / Total impostor attempts | < 1% | Security — lower is better |
| **FRR** (False Reject Rate) | Genuine user rejected / Total genuine attempts | < 5% | Usability — lower is better |
| **EER** (Equal Error Rate) | Point where FAR = FRR | < 5% | Overall system balance |

The scatter plot in `metrics.py` plots similarity score vs. decision, letting you visually identify where to place the threshold.

---

## Limitations

| Limitation | Detail | Planned Fix |
|---|---|---|
| **Single user only** | One voice profile, one encryption key | Multi-user with per-user key management |
| **Basic anti-spoofing** | ZCR/flatness won't stop AI voice cloning | Deep learning spoof detector (Phase 9) |
| **Local key storage** | `key.key` on disk — losing it = losing all files | Secure key derivation / cloud key management |
| **No cross-device support** | Embeddings and key are local | Cloud profile + key sync |
| **Noise sensitivity** | Very loud rooms reduce accuracy | Advanced noise suppression pipeline |
| **Phrase is plaintext** | Stored as plain JSON | Hashed phrase comparison |

---

## Development Roadmap

Based on `project.md` — 10-phase plan:

| Phase | Status | Description |
|---|---|---|
| **1** — Foundation & Audio | ✅ Complete | Project setup, `recorder.py`, `preprocess.py` |
| **2** — Deep Learning | ✅ Complete | ECAPA-TDNN integration, `extract_features.py` |
| **3** — Verification & Profiles | ✅ Complete | Cosine similarity, profile averaging, single-user |
| **4** — Security & Adaptation | ✅ Complete | Anti-spoofing, continual learning, AES-256 encryption |
| **5** — UI & Logging | ✅ Complete | Cyberpunk Streamlit UI, CLI, auth logger |
| **6** — Advanced Metrics | 🔲 Planned | EER, ROC curves, noise robustness testing |
| **7** — Testing & QA | 🔲 Planned | pytest suite, VoxCeleb benchmark |
| **8** — UI/UX Overhaul | 🔲 Planned | Real-time spectrogram, waveform recording visualization |
| **9** — Standout Features | 🔲 Planned | Multi-modal auth, deep learning anti-spoof, secure key derivation |
| **10** — Deployment | 🔲 Planned | Docker, Streamlit Cloud / AWS |

---

## References

| Resource | Link |
|---|---|
| ECAPA-TDNN Paper | [Desplanques et al. (2020), arXiv:2005.07143](https://arxiv.org/abs/2005.07143) |
| SpeechBrain Library | [speechbrain.github.io](https://speechbrain.github.io) |
| VoxCeleb Dataset | [robots.ox.ac.uk/~vgg/data/voxceleb](https://www.robots.ox.ac.uk/~vgg/data/voxceleb/) |
| Python Cryptography (Fernet) | [cryptography.io/en/latest/fernet](https://cryptography.io/en/latest/fernet/) |
| Librosa Documentation | [librosa.org/doc](https://librosa.org/doc/) |
| Noisereduce | [github.com/timsainb/noisereduce](https://github.com/timsainb/noisereduce) |
| Streamlit Documentation | [docs.streamlit.io](https://docs.streamlit.io) |

---

*Project: Voice-Based Authentication Using Deep Learning | Semester 4 | Last updated: April 2026*
