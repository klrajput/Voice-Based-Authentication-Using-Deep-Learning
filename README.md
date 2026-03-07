🎤 Voice-Based Authentication Using Deep Learning

A speaker verification system that authenticates users using deep learning voice embeddings.

The system extracts 192-dimensional speaker embeddings using SpeechBrain’s ECAPA-TDNN model and verifies identity using cosine similarity matching.

It also includes anti-spoofing detection, continual learning, and authentication logging.

🚀 Features

Voice Registration (User Enrollment)

Voice Authentication (Identity Verification)

Deep Learning Speaker Embeddings (ECAPA-TDNN)

Anti-Spoofing Detection (Replay Attack Protection)

Noise Reduction for better audio quality

Continual Learning (Profile adapts over time)

Authentication Logging

Evaluation Metrics (FAR / FRR)

🧠 System Architecture
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
🛠 Tech Stack
Component	Technology
Language	Python
Deep Learning Model	ECAPA-TDNN (SpeechBrain)
Dataset	VoxCeleb (Pretrained)
Audio Processing	Librosa, Noisereduce
Recording	SoundDevice
Similarity Metric	Cosine Similarity
Storage	NumPy (.npy files)
Configuration	YAML
📁 Project Structure
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
⚙️ System Workflow
Voice Registration
User Voice
   │
   ▼
Record Audio (6s @ 16kHz)
   │
   ▼
Noise Reduction
   │
   ▼
Embedding Extraction (ECAPA-TDNN)
   │
   ▼
Save Embedding
   │
   ▼
Update User Profile (Average)
Voice Authentication
User Voice
   │
   ▼
Record Audio
   │
   ▼
Noise Reduction
   │
   ▼
Anti-Spoof Detection
   │
   ▼
Extract Embedding
   │
   ▼
Cosine Similarity Comparison
   │
   ▼
Score > Threshold ?
   │
   ├── YES → Access Granted
   │
   └── NO → Access Denied
🔍 How It Works
1️⃣ Audio Recording

The system records 6 seconds of audio using the microphone at 16kHz sampling rate.

2️⃣ Audio Preprocessing

Noise reduction is applied using the noisereduce library to remove background noise.

3️⃣ Speaker Embedding Extraction

The processed audio is passed through the ECAPA-TDNN model from SpeechBrain, producing a 192-dimensional embedding vector representing the speaker’s voice.

4️⃣ Anti-Spoofing Detection

Two acoustic features are used:

Spectral Flatness

Zero Crossing Rate (ZCR)

Spoof rule:

if spectral_flatness > 0.5 or ZCR < 0.01:
    reject_audio()
5️⃣ Voice Verification

Cosine similarity is used to compare the stored profile with the new embedding.

score = (A · B) / (||A|| * ||B||)

Where:

A = Stored profile embedding

B = New voice embedding

Threshold:

score > 0.80  → Access Granted
score ≤ 0.80  → Access Denied
6️⃣ Continual Learning

After successful authentication:

New embedding is saved

All embeddings are averaged

User profile is updated

This helps the system adapt to gradual voice changes.

📦 Installation
Clone Repository
git clone https://github.com/klrajput/Voice-Based-Authentication-Using-Deep-Learning.git
cd Voice-Based-Authentication-Using-Deep-Learning
Install Dependencies
pip install -r requirements.txt

If some libraries are missing:

pip install speechbrain torchaudio noisereduce soundfile pyyaml pandas matplotlib
▶️ Usage

Run the system:

cd src
python main.py

Menu:

1  Register Voice
2  Authenticate Voice
3  Exit
⚙️ Configuration

Configuration file:

configs/config.yaml

Example configuration:

audio:
  sample_rate: 16000
  duration: 6

model:
  threshold: 0.80

paths:
  raw_audio: data/raw_audio
  processed_audio: data/processed_audio
  embeddings: data/embeddings
📊 Evaluation Metrics

The system logs every authentication attempt.

Metrics supported:

FAR — False Accept Rate

FRR — False Reject Rate

Logs stored in:

data/logs/auth_log.csv
📜 License

This project is developed for academic purposes as a B.Tech Semester Project.
