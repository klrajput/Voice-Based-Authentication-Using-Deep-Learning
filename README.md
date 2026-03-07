# Voice-Based Authentication Using Deep Learning

A speaker verification system that uses deep learning to authenticate users based on their voice. The system extracts speaker embeddings using SpeechBrain's ECAPA-TDNN model and performs identity verification through cosine similarity matching.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [System Workflow](#system-workflow)
- [Data Flow Diagrams](#data-flow-diagrams)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Evaluation Metrics](#evaluation-metrics)

---

## Overview

This project implements a voice-based biometric authentication system that:

1. Records a user's voice and converts it into a unique numerical fingerprint (embedding) using a pretrained deep learning model.
2. Stores and averages these embeddings to build a robust user voice profile.
3. Authenticates users by comparing new voice samples against the stored profile using cosine similarity.
4. Includes anti-spoofing detection to prevent replay attacks.
5. Implements continual learning — the voice profile adapts over time with each successful authentication.

---

## Features

- **Voice Registration** — Enroll a user by recording and storing voice embeddings
- **Voice Authentication** — Verify identity via cosine similarity scoring
- **Anti-Spoofing** — Detects replay attacks using spectral flatness and zero-crossing rate
- **Continual Learning** — Profile auto-updates after each successful authentication
- **Noise Reduction** — Preprocesses audio to remove background noise
- **Authentication Logging** — Records all authentication attempts with timestamps and scores
- **Evaluation Metrics** — Computes FAR (False Accept Rate) and FRR (False Reject Rate)

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python |
| Deep Learning Model | ECAPA-TDNN (SpeechBrain) |
| Training Data | VoxCeleb (pretrained) |
| Audio Processing | Librosa, Noisereduce, SoundDevice |
| Similarity Metric | Cosine Similarity (scikit-learn) |
| Embedding Storage | NumPy (.npy files) |
| Configuration | YAML |

---

## Project Structure

```
Voice-Based-Authentication-Using-Deep-Learning/
│
├── configs/
│   └── config.yaml                  # Audio, path, and model configurations
│
├── data/
│   ├── embeddings/                  # Stored voice embeddings (.npy)
│   ├── logs/
│   │   └── auth_log.csv             # Authentication attempt logs
│   ├── processed_audio/             # Noise-reduced audio files
│   ├── profile/
│   │   ├── profile_manager.py       # Profile management (data copy)
│   │   └── user_profile.npy         # Averaged user voice profile
│   └── raw_audio/                   # Raw recorded audio files
│
├── models/
│   └── speaker_model/               # Pretrained ECAPA-TDNN model files
│       ├── classifier.ckpt
│       ├── embedding_model.ckpt
│       ├── hyperparams.yaml
│       ├── label_encoder.ckpt
│       └── mean_var_norm_emb.ckpt
│
├── src/
│   ├── main.py                      # Entry point (CLI menu)
│   ├── audio/
│   │   ├── recorder.py              # Voice recording module
│   │   └── preprocess.py            # Noise reduction & preprocessing
│   ├── features/
│   │   └── extract_features.py      # ECAPA-TDNN embedding extraction
│   ├── model/
│   │   ├── verify_voice.py          # Cosine similarity verification
│   │   ├── profile_manager.py       # User profile load/update logic
│   │   └── train_model.py           # (Reserved for future use)
│   ├── security/
│   │   └── antispoof.py             # Spoof detection module
│   ├── evaluation/
│   │   ├── logger.py                # Authentication event logger
│   │   └── metrics.py               # FAR/FRR computation
│   └── learning/
│       └── continual_learning.py    # Embedding storage & profile update
│
├── requirements.txt
└── README.md
```

---

## System Workflow

### Registration Workflow

```
┌──────────────┐     ┌──────────────────┐     ┌────────────────────┐     ┌──────────────────┐
│  User speaks │────▶│  Record Audio    │────▶│ Preprocess Audio   │────▶│ Extract Embedding│
│  into mic    │     │  (6s @ 16kHz)    │     │ (Noise Reduction)  │     │ (ECAPA-TDNN)     │
└──────────────┘     └──────────────────┘     └────────────────────┘     └────────┬─────────┘
                                                                                  │
                                                                                  ▼
                                                                         ┌──────────────────┐
                                                                         │ Save Embedding   │
                                                                         │ (.npy file)      │
                                                                         └────────┬─────────┘
                                                                                  │
                                                                                  ▼
                                                                         ┌──────────────────┐
                                                                         │ Update Profile   │
                                                                         │ (Average all     │
                                                                         │  embeddings)     │
                                                                         └──────────────────┘
```

### Authentication Workflow

```
┌──────────────┐     ┌──────────────────┐     ┌────────────────────┐     ┌──────────────────┐
│  User speaks │────▶│  Record Audio    │────▶│ Preprocess Audio   │────▶│  Anti-Spoof      │
│  into mic    │     │  (6s @ 16kHz)    │     │ (Noise Reduction)  │     │  Check           │
└──────────────┘     └──────────────────┘     └────────────────────┘     └────────┬─────────┘
                                                                                  │
                                                                    ┌─────────────┼─────────────┐
                                                                    │ Spoof       │ Genuine     │
                                                                    ▼             ▼             │
                                                              ┌──────────┐  ┌──────────────┐   │
                                                              │ REJECTED │  │ Extract      │   │
                                                              │ (Spoof)  │  │ Embedding    │   │
                                                              └──────────┘  └──────┬───────┘   │
                                                                                   │           │
                                                                                   ▼           │
                                                                            ┌──────────────┐   │
                                                                            │ Compare with │   │
                                                                            │ Stored       │   │
                                                                            │ Profile      │   │
                                                                            │ (Cosine Sim) │   │
                                                                            └──────┬───────┘   │
                                                                                   │           │
                                                                     ┌─────────────┴──────┐    │
                                                                     │                    │    │
                                                               Score > 0.80         Score ≤ 0.80
                                                                     │                    │
                                                                     ▼                    ▼
                                                              ┌──────────────┐   ┌──────────────┐
                                                              │ ACCESS       │   │ ACCESS       │
                                                              │ GRANTED      │   │ DENIED       │
                                                              │ + Update     │   │              │
                                                              │   Profile    │   │              │
                                                              └──────────────┘   └──────────────┘
                                                                     │                    │
                                                                     └────────┬───────────┘
                                                                              ▼
                                                                     ┌──────────────┐
                                                                     │ Log Result   │
                                                                     │ (CSV)        │
                                                                     └──────────────┘
```

---

## Data Flow Diagrams

### Level 0 — Context Diagram

```
                         ┌─────────────────────────────────────┐
                         │                                     │
    Voice Input          │    Voice-Based Authentication       │       Authentication
   ─────────────────────▶│            System                   │──────── Result
                         │                                     │    (Accept / Reject)
    User Choice          │                                     │
   (Register/Auth)──────▶│                                     │
                         └─────────────────────────────────────┘
```

### Level 1 — Major Processes

```
┌──────┐     Voice      ┌─────────────┐    Raw Audio     ┌─────────────────┐
│      │───────────────▶│  1.0        │─────────────────▶│  2.0            │
│      │                │  Record     │                   │  Preprocess     │
│      │                │  Audio      │                   │  Audio          │
│ USER │                └─────────────┘                   └────────┬────────┘
│      │                                                           │
│      │                                                  Cleaned Audio
│      │                                                           │
│      │                                                           ▼
│      │                                                  ┌─────────────────┐
│      │                                                  │  3.0            │
│      │                                                  │  Anti-Spoof     │
│      │                                                  │  Detection      │
│      │                                                  └────────┬────────┘
│      │                                                           │
│      │                                                  Validated Audio
│      │                                                           │
│      │                                                           ▼
│      │                                                  ┌─────────────────┐
│      │                                                  │  4.0            │
│      │                                                  │  Extract        │
│      │                                                  │  Embedding      │──────────┐
│      │                                                  │  (ECAPA-TDNN)   │          │
│      │                                                  └─────────────────┘          │
│      │                                                                          Embedding
│      │                                                                               │
│      │                                                                               ▼
│      │                ┌─────────────┐                   ┌─────────────────┐    ┌──────────────┐
│      │   Result       │  7.0        │    Score          │  5.0            │    │              │
│      │◀───────────────│  Log        │◀──────────────────│  Verify         │◀───│  D1          │
│      │                │  Auth       │                   │  Voice          │    │  User Profile│
│      │                │  Event      │                   │  (Cosine Sim)   │    │  Store       │
│      │                └──────┬──────┘                   └─────────────────┘    │              │
│      │                       │                                                └──────────────┘
│      │                       ▼                                                       ▲
│      │                ┌──────────────┐                  ┌─────────────────┐           │
│      │                │              │                  │  6.0            │           │
│      │                │  D2          │                  │  Update         │───────────┘
│      │                │  Auth Log    │                  │  Profile        │
│      │                │  (CSV)       │                  │  (Continual     │
└──────┘                │              │                  │   Learning)     │
                        └──────────────┘                  └─────────────────┘
```

### Level 2 — Detailed Process Breakdown

```
┌────────────────────────────────────────────────────────────────────────────┐
│ Process 4.0 — Extract Embedding (Detail)                                  │
│                                                                            │
│   Audio File ──▶ Load with ──▶ Convert to ──▶ ECAPA-TDNN ──▶ 192-dim     │
│                  torchaudio    Mono            Encoder        Embedding    │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ Process 5.0 — Verify Voice (Detail)                                       │
│                                                                            │
│   New Embedding ──┐                                                        │
│                    ├──▶ Cosine Similarity ──▶ Compare with ──▶ Accept /    │
│   User Profile ───┘                          Threshold (0.80)   Reject    │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────────┐
│ Process 6.0 — Update Profile (Detail)                                     │
│                                                                            │
│   New Embedding ──▶ Save to ──▶ Load ALL ──▶ Compute ──▶ Save Updated    │
│                     /embeddings  Embeddings   Mean        user_profile.npy│
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## How It Works

### 1. Audio Recording
The system records **6 seconds** of audio at **16 kHz** sample rate using the microphone. Each recording is saved as a `.wav` file with a unique UUID filename.

### 2. Audio Preprocessing
Raw audio undergoes **noise reduction** using the `noisereduce` library to remove background noise. The cleaned audio is saved separately for feature extraction.

### 3. Feature Extraction (Speaker Embedding)
The preprocessed audio is fed into **SpeechBrain's ECAPA-TDNN** model, pretrained on the **VoxCeleb** dataset. This model produces a **192-dimensional embedding vector** — a compact numerical representation of the speaker's voice characteristics.

### 4. Anti-Spoofing
Before verification, the system checks for replay attacks using two acoustic features:
- **Spectral Flatness** — Measures how noise-like the signal is (spoofed audio tends to be unnaturally flat)
- **Zero-Crossing Rate (ZCR)** — Measures how often the signal crosses zero (very low ZCR indicates synthetic audio)

If `spectral_flatness > 0.5` or `ZCR < 0.01`, the audio is flagged as a spoof.

### 5. Voice Verification
The new embedding is compared against the stored **user profile** using **cosine similarity**:

$$\text{score} = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \cdot \|\mathbf{B}\|}$$

Where **A** = stored profile (mean of all embeddings), **B** = new embedding.

- Score ranges from **0 to 1** (higher = more similar)
- Threshold: **0.80** — scores above this grant access

### 6. Continual Learning
On successful authentication, the new embedding is **stored** and the user profile is **recomputed** as the average of all embeddings. This allows the system to adapt to gradual changes in the user's voice over time.

---

## Installation

### Prerequisites
- Python 3.8+
- Working microphone

### Setup

```bash
# Clone the repository
git clone https://github.com/klrajput/Voice-Based-Authentication-Using-Deep-Learning.git
cd Voice-Based-Authentication-Using-Deep-Learning

# Install dependencies
pip install -r requirements.txt

# Additional dependencies (if not in requirements.txt)
pip install speechbrain torchaudio noisereduce soundfile pyyaml pandas matplotlib
```

---

## Usage

```bash
# Run from the src directory
cd src
python main.py
```

### Menu Options

```
1  Register Voice    — Record and enroll your voice
2  Authenticate Voice — Verify your identity
3  Exit
```

### First-Time Setup
1. Select **Option 1** (Register Voice) to record your voice
2. Speak clearly for 6 seconds when prompted
3. Repeat registration a few times for a stronger profile

### Authentication
1. Select **Option 2** (Authenticate Voice)
2. Speak into the microphone
3. System displays the similarity score and grants/denies access

---

## Configuration

All configurable parameters are in `configs/config.yaml`:

```yaml
audio:
  sample_rate: 16000    # Audio sampling rate in Hz
  duration: 6           # Recording duration in seconds

paths:
  raw_audio: data/raw_audio
  processed_audio: data/processed_audio
  embeddings: data/embeddings

model:
  threshold: 0.80       # Cosine similarity threshold for authentication
```

---

## Evaluation Metrics

The system logs every authentication attempt and supports computing:

- **FAR (False Accept Rate)** — Proportion of impostor attempts incorrectly accepted
- **FRR (False Reject Rate)** — Proportion of genuine attempts incorrectly rejected

Run the metrics module separately to analyze authentication performance from the collected logs.

---

## Module Dependency Graph

```
main.py
 ├── audio/recorder.py           ← Records voice via microphone
 ├── audio/preprocess.py         ← Applies noise reduction
 ├── features/extract_features.py ← Generates 192-dim embedding (ECAPA-TDNN)
 ├── security/antispoof.py       ← Checks for spoofing attacks
 ├── model/verify_voice.py       ← Cosine similarity matching
 │    └── model/profile_manager.py ← Loads stored user profile
 ├── learning/continual_learning.py ← Saves embedding & updates profile
 │    └── model/profile_manager.py   ← Recomputes mean profile
 └── evaluation/logger.py        ← Logs authentication events to CSV
```

---

## License

This project is developed as a semester project for academic purposes.
