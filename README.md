# 🎤 Voice-Based Authentication Using Deep Learning

A speaker verification system that authenticates users using deep learning voice embeddings.

The system extracts **192-dimensional speaker embeddings** using **SpeechBrain's ECAPA-TDNN model** and verifies identity using **cosine similarity matching**.

It also includes **anti-spoofing detection, continual learning, and authentication logging.**

---

## 🚀 Features

- Voice Registration (User Enrollment)
- Voice Authentication (Identity Verification)
- Deep Learning Speaker Embeddings (ECAPA-TDNN)
- Anti-Spoofing Detection (Replay Attack Protection)
- Noise Reduction for better audio quality
- Continual Learning (Profile adapts over time)
- Authentication Logging
- Evaluation Metrics (FAR / FRR)

---

## 🧠 System Architecture

```
User Voice
   │
   ▼
Audio Recording
   │
   ▼
Noise Reduction
   │
   ▼
Anti-Spoof Detection
   │
   ▼
ECAPA-TDNN Model
   │
   ▼
Speaker Embedding (192-dim)
   │
   ▼
Cosine Similarity Matching
   │
   ▼
Authentication Result
```

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python |
| Deep Learning Model | ECAPA-TDNN (SpeechBrain) |
| Dataset | VoxCeleb (Pretrained) |
| Audio Processing | Librosa, Noisereduce |
| Recording | SoundDevice |
| Similarity Metric | Cosine Similarity |
| Storage | NumPy (.npy files) |
| Configuration | YAML |

---

## 📁 Project Structure

```
Voice-Based-Authentication-Using-Deep-Learning
│
├── configs
│   └── config.yaml
│
├── data
│   ├── embeddings
│   ├── logs
│   │   └── auth_log.csv
│   ├── processed_audio
│   ├── raw_audio
│   └── profile
│       └── user_profile.npy
│
├── models
│   └── speaker_model
│
├── src
│   ├── main.py
│   │
│   ├── audio
│   │   ├── recorder.py
│   │   └── preprocess.py
│   │
│   ├── features
│   │   └── extract_features.py
│   │
│   ├── model
│   │   ├── verify_voice.py
│   │   └── profile_manager.py
│   │
│   ├── security
│   │   └── antispoof.py
│   │
│   ├── evaluation
│   │   ├── logger.py
│   │   └── metrics.py
│   │
│   └── learning
│       └── continual_learning.py
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

```bash
git clone https://github.com/klrajput/Voice-Based-Authentication-Using-Deep-Learning.git
cd Voice-Based-Authentication-Using-Deep-Learning
pip install -r requirements.txt
```

If some libraries are missing:

```bash
pip install speechbrain torchaudio noisereduce soundfile pyyaml pandas matplotlib
```

---

## ▶️ Usage

Run the system:

```bash
cd src
python main.py
```

Menu:

```
1 Register Voice
2 Authenticate Voice
3 Exit
```

---

## 📜 License

This project is developed for **academic purposes as a B.Tech Semester Project**.
