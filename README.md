# Voice-Based Authentication Using Deep Learning (VoiceLock)

**VoiceLock** is a comprehensive voice biometric authentication system that replaces traditional passwords with speaker verification technology. It leverages deep learning (ECAPA-TDNN embeddings) combined with anti-spoofing measures and continual learning to provide a secure, user-friendly, passwordless authentication experience. The system includes multi-user support, file encryption capabilities, and comprehensive audit logging.

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [System Architecture](#system-architecture)
  - [Architecture Diagram](#architecture-diagram)
  - [Data Flow Diagram](#data-flow-diagram)
  - [Entity-Relationship Diagram](#entity-relationship-diagram)
- [Project Structure](#project-structure)
- [Detailed Module Descriptions](#detailed-module-descriptions)
- [How It Works](#how-it-works)
  - [Voice Registration (Lock Workflow)](#voice-registration-lock-workflow)
  - [Voice Verification (Unlock Workflow)](#voice-verification-unlock-workflow)
- [Security Design](#security-design)
  - [Anti-Spoofing & Liveness Detection](#anti-spoofing--liveness-detection)
  - [Authentication Logs](#authentication-logs)
  - [File Encryption](#file-encryption)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Evaluation Metrics](#evaluation-metrics)
- [Testing & Troubleshooting](#testing--troubleshooting)
- [Deployment Notes](#deployment-notes)
- [Performance Considerations](#performance-considerations)
- [Limitations](#limitations)
- [Development Roadmap](#development-roadmap)
- [Demonstration Checklist](#demonstration-checklist)
- [References](#references)

---

## Executive Summary

VoiceLock revolutionizes user authentication by replacing traditional passwords with **voice biometrics**. Each user's unique vocal characteristics serve as their authentication credential—impossible to forget, steal, or share like passwords. The system:

- **Records voice samples** and extracts 192-dimensional speaker embeddings using SpeechBrain's ECAPA-TDNN model (pretrained on VoxCeleb).
- **Performs identity verification** through cosine similarity matching between live samples and stored voice profiles.
- **Detects spoofing attempts** using active liveness checks (random numeric challenge-response) and signal analysis (Zero-Crossing Rate, spectral features).
- **Adapts over time** through continual learning—profiles automatically update with each successful authentication.
- **Logs all events** for accountability and audit trails.
- **Supports file encryption** (optional AES-256) to protect locked files at rest.
- **Enables multi-user scenarios** with independent voice profiles and file locks.

Unlike passwords or PINs (which can be stolen, shared, or forgotten), voice authentication is natural, convenient, and inherently tied to the user. This makes VoiceLock ideal for both academic projects and real-world security applications.

---

## Problem Statement

Traditional authentication (username/password) has well-known vulnerabilities:

- **Weak passwords:** Users often choose simple passwords or reuse them across multiple sites.
- **Credential theft:** Passwords can be stolen via phishing, keylogging, or leaked databases.
- **Usability burden:** Users must remember complex passwords, leading to poor practices (sticky notes, password managers).
- **No true identity:** A password doesn't prove identity; anyone with the password gains access.

**Biometric authentication** mitigates these issues by authenticating based on inherent characteristics (fingerprints, iris, voice) that cannot be stolen, forgotten, or shared. In particular, **voice authentication** offers:

- **User-friendly:** Hands-free, natural interaction—just speak.
- **Accessibility:** Works for users with mobility limitations.
- **Security:** Voice characteristics are difficult to forge (though spoofing attacks like replay exist).

However, biometric systems face unique challenges:

- **Spoofing attacks:** Replay attacks (playing back a recording) or synthetic audio (deepfakes) can fool naive systems.
- **Environmental variation:** Background noise, microphone differences, and speaker variability affect accuracy.
- **False accept/reject rates:** Balancing security (rejecting impostors) with usability (accepting legitimate users).

**Our goal** is to build a **secure, multi-user voice-based file locking system** that:
- Eliminates passwords by using voice biometrics.
- Implements liveness checks (active challenge-response) to prevent replay/deepfake attacks.
- Supports continual learning so profiles improve over time.
- Logs all actions for audit trails and accountability.
- Optionally encrypts files for added confidentiality.

---

## Solution Overview

VoiceLock is built as an interactive **Streamlit web application** that coordinates voice processing, verification, and file management. The workflow:

1. **User registration (file lock):** A user enters their ID/name, uploads a file, and records a voice sample by repeating a random spoken number.
2. **Voice encoding:** The audio is preprocessed (noise reduction, resampling to 16kHz, normalization) and fed to the ECAPA-TDNN model to generate a 192-dimensional embedding.
3. **Profile storage:** The embedding is saved to the user's profile directory (`data/profile/users/<user_id>/`). On first use, an average embedding represents the user's voice "fingerprint."
4. **File locking:** The file is moved to `data/locked_file/` and metadata is recorded in `lock_meta.json`.
5. **User authentication (file unlock):** To access a locked file, the same user must:
   - Respond correctly to a new random numeric challenge (active liveness).
   - Pass anti-spoof checks (ZCR, spectral analysis, and challenge matching).
   - Provide a voice sample matching their stored profile (cosine similarity above threshold).
6. **Adaptive learning:** On successful unlock, the new voice sample is added to the profile, improving future matching.
7. **Audit logging:** All attempts (successful and failed) are logged with timestamps, scores, and outcomes.

The design leverages standard libraries (Streamlit for UI, Librosa for audio features, SciPy for similarity, cryptography for encryption) ensuring both robustness and maintainability.

---

## Features

### Core Authentication
- **Voice Registration (Lock):** Users upload a file, record their voice for a random numeric challenge, and create a voice profile.
- **Voice Verification (Unlock):** Users prove identity by reproducing a new random challenge and having their voice verified against their stored profile.
- **Multi-User Support:** Each user has an independent voice profile directory (`data/profile/users/<user_id>/`), enabling isolated authentication for multiple users.

### Security & Spoofing Defense
- **Active Liveness Detection:** The system requires users to repeat a randomly generated number during registration and unlock. An attacker cannot simply replay a static recording.
- **Signal Analysis:** Computes Zero-Crossing Rate (ZCR), spectral flatness, and energy features to detect anomalies typical of replay attacks or synthetic audio.
- **Dual-Verification Strategy:** Access is only granted if both the cosine similarity score exceeds the threshold AND the predicted speaker class matches the claimed identity.

### Adaptive Learning
- **Continual Learning:** Each successful authentication adds the voice sample to the user's profile. Over time, profiles average multiple samples, adapting to gradual voice changes (aging, different recording environments, etc.).

### Logging & Auditing
- **Comprehensive Logging:** All authentication attempts (successful and failed) are logged to `data/evaluation/log.csv` with timestamps, user IDs, similarity scores, and outcomes.
- **Audit Trail:** Provides accountability and enables detection of repeated failed attempts (potential attacks).

### File Management
- **File Locking:** Uploads are stored in `data/locked_file/` with metadata tracking which user locked each file.
- **File Encryption (Optional):** Symmetric encryption (AES-256 recommended) can protect locked file contents at rest.
- **Easy Download:** Successful authentication triggers automatic file download.

### Configuration & Extensibility
- **YAML Configuration:** System parameters (sample rate, recording duration, model paths, decision thresholds) are defined in `configs/config.yaml`.
- **JSON Profiles:** User metadata (names, file associations) is stored in `data/profile/user_info.json`, enabling easy customization.

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.8+ | Core implementation language |
| **Deep Learning Model** | ECAPA-TDNN (SpeechBrain) | Speaker embeddings (192-dimensional) |
| **Training Data** | VoxCeleb | Pretrained model foundation |
| **Feature Extraction** | Librosa | MFCC computation and audio analysis |
| **Audio Recording** | SoundDevice / Streamlit `st.audio_input` | Microphone interface |
| **Preprocessing** | Noisereduce, SciPy | Noise removal and signal cleaning |
| **Similarity Metric** | Cosine Similarity (scikit-learn) | Voice matching |
| **Embedding Storage** | NumPy (.npy files) | Profile serialization |
| **Web UI** | Streamlit | Interactive dashboard and user interface |
| **Configuration** | YAML | Parameter management |
| **Logging** | CSV + Python logging | Event tracking and audit trail |
| **Encryption (Optional)** | Python cryptography (Fernet/AES) | File and profile protection |

---

## System Architecture

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Streamlit Web Application                   │
├─────────────────────────────────────────────────────────────────┤
│                      Frontend (UI)                              │
│  - User ID & Name Input                                        │
│  - File Upload/Download                                        │
│  - Voice Recording Interface                                   │
│  - Status Messages & Results                                   │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
    ┌───▼────────────┐      ┌────────▼────────┐
    │  Lock Process  │      │ Unlock Process  │
    └───┬────────────┘      └────────┬────────┘
        │                             │
        ├─► Record Voice              ├─► Load Lock Metadata
        ├─► Preprocess Audio          ├─► Random Challenge
        ├─► Extract Embeddings        ├─► Record Voice
        ├─► Anti-Spoof Check          ├─► Preprocess Audio
        └─► Save to Profile           ├─► Anti-Spoof Check
                                      ├─► Compare Embeddings
                                      ├─► Decision (Accept/Reject)
                                      └─► File Download
                                      
┌─────────────────────────────────────────────────────────────────┐
│                      Data Stores                                │
├─────────────────────────────────────────────────────────────────┤
│ - User Profiles: data/profile/users/<user_id>/embeddings/      │
│ - Locked Files: data/locked_file/                              │
│ - Lock Metadata: data/locked_file/lock_meta.json               │
│ - User Info: data/profile/user_info.json                       │
│ - Audit Log: data/evaluation/log.csv                           │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
User Input (ID, File) → Streamlit UI
                           │
                ┌──────────┴──────────┐
                │                     │
            [LOCK]               [UNLOCK]
              │                     │
              ├─► Record Voice      ├─► Load lock_meta.json
              ├─► Preprocess        ├─► Show Challenge
              ├─► Extract MFCC      ├─► Record Voice
              ├─► Save Embedding    ├─► Preprocess
              └─► Update Profile    ├─► Anti-Spoof Check
                                    ├─► Extract MFCC
                                    ├─► Load Profile
                                    ├─► Compute Similarity
                                    ├─► Compare Score
                                    │
                        ┌───────────┴────────────┐
                        │                        │
                    [ACCEPT]                [REJECT]
                        │                        │
                        ├─► Update Profile      ├─► Log Attempt
                        ├─► Log Success         └─► Deny Access
                        └─► Download File
```

### Entity-Relationship Diagram

```
┌─────────────────────┐         ┌──────────────────────┐
│       USER          │────────◄│     FILE_LOCK        │
├─────────────────────┤         ├──────────────────────┤
│ user_id (PK)        │1        │ locked_file (PK)     │
│ name                │    locks │ user_id (FK)         │
│ profile_path        │many      │ timestamp            │
│ threshold           │         │ encryption_key       │
└─────────────────────┘         └──────────────────────┘
         │
         │ contains
         │
         ▼
┌─────────────────────────────────────┐
│     EMBEDDING (Voice Profile)       │
├─────────────────────────────────────┤
│ embedding_id (PK)                   │
│ user_id (FK)                        │
│ embedding_vector (192-dim)          │
│ timestamp                           │
│ authentication_context              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│     AUTH_LOG (Audit Trail)          │
├─────────────────────────────────────┤
│ log_id (PK)                         │
│ timestamp                           │
│ user_id                             │
│ action (lock/unlock)                │
│ similarity_score                    │
│ spoof_detected                      │
│ result (success/failure)            │
└─────────────────────────────────────┘
```

---

## Project Structure

```
Voice-Based-Authentication-Using-Deep-Learning/
│
├── configs/
│   └── config.yaml                  # System configuration (sample rate, duration, thresholds, paths)
│
├── data/
│   ├── embeddings/                  # Individual voice embedding (.npy) files
│   │   ├── 0124649c-7fa9-4671-93a4-f9fd25bfdbcf.npy
│   │   ├── 017b2c5c-3097-443c-a1fa-30402266ff58.npy
│   │   └── ... (one file per voice sample)
│   ├── locked_file/                 # Stores locked files and lock metadata
│   │   ├── lock_meta.json           # Metadata: which user locked which file
│   │   └── <uploaded_files>
│   ├── logs/                        # System audit trails
│   │   └── auth_log.csv             # Authentication attempt history
│   ├── processed_audio/             # Noise-reduced audio files
│   │   └── <preprocessed_audio_files>
│   ├── profile/                     # User voice profiles and metadata
│   │   ├── users/                   # Each subfolder is a user_id
│   │   │   ├── user_1/
│   │   │   │   └── embeddings/      # User's voice embeddings
│   │   │   ├── user_2/
│   │   │   │   └── embeddings/
│   │   │   └── ...
│   │   ├── user_profile.npy         # Averaged profile for each user
│   │   ├── user_info.json           # Global user metadata (names, IDs, status)
│   │   └── speaker_map.json         # Mapping of user IDs to model classes
│   └── raw_audio/                   # Original recorded audio files
│       └── <raw_voice_recordings>
│
├── models/
│   └── speaker_model/               # Pretrained ECAPA-TDNN model files
│       ├── classifier.ckpt          # SpeechBrain classifier checkpoint
│       ├── embedding_model.ckpt     # Embedding model checkpoint
│       ├── hyperparams.yaml         # Model hyperparameters
│       ├── label_encoder.ckpt       # Label encoding
│       └── mean_var_norm_emb.ckpt   # Normalization parameters
│
├── src/
│   ├── main.py                      # CLI entry point (menu-driven interface)
│   ├── streamlit_app.py             # Streamlit web application (main UI)
│   │
│   ├── audio/                       # Voice capture and preprocessing
│   │   ├── recorder.py              # Microphone recording interface
│   │   │   - record_voice()         # Captures audio from microphone
│   │   │   - record_with_device()   # Device-specific recording
│   │   │
│   │   └── preprocess.py            # Audio preprocessing and cleaning
│   │       - preprocess_audio()     # Noise reduction, resampling, normalization
│   │       - normalize_amplitude()  # Peak/RMS normalization
│   │       - convert_to_mono()      # Stereo to mono conversion
│   │       - resample_to_16khz()    # Resample to standard 16 kHz
│   │
│   ├── features/                    # Feature extraction and embedding generation
│   │   └── extract_features.py      # ECAPA-TDNN embedding extraction
│   │       - extract_features()     # Generates 192-dim embeddings
│   │       - extract_mfcc()         # MFCC feature extraction (13 coefficients)
│   │       - load_model()           # Loads pretrained SpeechBrain model
│   │
│   ├── model/                       # Core verification and profile management
│   │   ├── verify_voice.py          # Voice matching and verification logic
│   │   │   - verify()               # Main verification function
│   │   │   - compute_cosine_similarity()
│   │   │   - compare_with_threshold()
│   │   │
│   │   ├── profile_manager.py       # Profile loading, saving, and management
│   │   │   - load_profile()         # Load user embeddings
│   │   │   - save_embedding()       # Save new embeddings
│   │   │   - update_profile()       # Update user profile average
│   │   │   - create_user_dir()      # Create user directory structure
│   │   │   - get_profile_path()     # Get path to user profile
│   │   │
│   │   ├── ecapa_classifier.py      # (Optional) Neural network-based ID prediction
│   │   │   - classify_speaker()     # Predict speaker ID
│   │   │   - softmax_prediction()   # Compute class probabilities
│   │   │
│   │   └── train_model.py           # (Reserved for future use)
│   │
│   ├── security/                    # Anti-spoofing and defense mechanisms
│   │   └── antispoof.py             # Spoof detection and liveness verification
│   │       - detect_spoof()         # Main anti-spoof function
│   │       - compute_zcr()          # Zero-Crossing Rate analysis
│   │       - compute_spectral_flatness()
│   │       - check_challenge_response()
│   │       - validate_liveness()    # Overall liveness validation
│   │
│   ├── learning/                    # Continual learning and profile adaptation
│   │   └── continual_learning.py    # Profile update with new samples
│   │       - save_embedding()       # Save embedding to user profile
│   │       - update_user_profile()  # Recompute mean profile
│   │       - enable_adaptive_learning()
│   │
│   └── evaluation/                  # Performance metrics and logging
│       ├── logger.py                # Event logging to CSV
│       │   - log_auth_event()       # Log authentication attempt
│       │   - log_file_lock()        # Log file lock event
│       │   - log_file_unlock()      # Log file unlock event
│       │   - get_logs()             # Retrieve logs
│       │
│       └── metrics.py               # Performance evaluation metrics
│           - compute_far()          # False Accept Rate
│           - compute_frr()          # False Reject Rate
│           - compute_equal_error_rate()  # EER
│           - plot_roc_curve()       # ROC curve generation
│
├── requirements.txt                 # Python dependencies
├── README.md                        # Original project documentation
├── Updated README.md                # This comprehensive documentation
├── project.md                       # Project roadmap (10-phase development plan)
├── structure.md                     # Detailed project architecture
├── deep-research-report.md          # In-depth system analysis
└── LICENSE                          # Project license
```

---

## Detailed Module Descriptions

### `src/streamlit_app.py`

**Purpose:** Main web application entry point. Provides the Streamlit UI for user registration, file locking, and voice verification.

**Key Functions:**
- **UI Layout:** Displays tabs/sections for Lock and Unlock operations.
- **Lock Workflow:**
  1. User enters ID and name.
  2. User uploads a file.
  3. App generates a random numeric challenge (e.g., "Say 7").
  4. Records user's voice via microphone.
  5. Preprocesses audio and extracts embeddings.
  6. Saves embedding to user profile.
  7. Moves file to `data/locked_file/` and records metadata.
  8. Displays success message.

- **Unlock Workflow:**
  1. User enters ID and name.
  2. App loads lock metadata to verify file association.
  3. Generates a new random challenge.
  4. Records voice and preprocesses audio.
  5. Runs anti-spoof checks.
  6. Compares embeddings using cosine similarity.
  7. Grants or denies access based on score and anti-spoof results.
  8. Logs attempt to audit trail.
  9. Triggers file download on success.

**Inputs/Outputs:**
- **Inputs:** User interactions via Streamlit widgets (`st.text_input`, `st.file_uploader`, `st.button`).
- **Outputs:** Status messages, file downloads, error alerts.
- **Integration:** Delegates audio, feature, security, and profile operations to specialized modules.

---

### `src/audio/recorder.py`

**Purpose:** Capture audio from the user's microphone.

**Key Functions:**
```python
def record_voice(duration=6, sample_rate=16000, device=None):
    """
    Record voice for specified duration.
    
    Args:
        duration (float): Recording duration in seconds (default 6s)
        sample_rate (int): Sample rate in Hz (default 16000)
        device (int): Audio device index (None = default device)
    
    Returns:
        tuple: (audio_array, sample_rate)
    """
    import sounddevice as sd
    recording = sd.rec(int(duration * sample_rate), 
                       samplerate=sample_rate, 
                       channels=1, 
                       device=device)
    sd.wait()
    return recording.flatten(), sample_rate
```

**Implementation Details:**
- Uses `sounddevice` or `soundfile` libraries to interface with the microphone.
- Captures mono (single channel) audio at the specified sample rate.
- Returns a NumPy array and the sample rate.
- Provides visual/audio feedback to guide the user through recording.

---

### `src/audio/preprocess.py`

**Purpose:** Clean and standardize raw audio for feature extraction.

**Key Functions:**
```python
def preprocess_audio(signal, orig_sample_rate, target_sample_rate=16000):
    """
    Preprocess audio: convert to mono, resample, normalize.
    
    Args:
        signal (np.ndarray): Raw audio signal (mono or stereo)
        orig_sample_rate (int): Original sample rate
        target_sample_rate (int): Target sample rate (default 16000)
    
    Returns:
        tuple: (preprocessed_signal, target_sample_rate)
    """
    # Convert to mono
    if signal.ndim > 1:
        signal = np.mean(signal, axis=1)
    
    # Resample to target rate
    if orig_sample_rate != target_sample_rate:
        signal = librosa.resample(signal, orig_sample_rate, target_sample_rate)
    
    # Normalize amplitude (peak normalization)
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val
    
    return signal, target_sample_rate
```

**Processing Steps:**
1. **Mono Conversion:** Averages stereo channels into a single channel.
2. **Resampling:** Converts to 16 kHz (standard for speaker recognition models).
3. **Normalization:** Peak normalization to prevent clipping and ensure consistent amplitude.
4. **Optional Noise Reduction:** Using `noisereduce` library to remove stationary background noise.

**Why Important:**
- ECAPA-TDNN expects 16 kHz mono audio.
- Inconsistent preprocessing leads to poor embedding quality and authentication failures.
- Normalization prevents quiet speakers from generating weak embeddings.

---

### `src/features/extract_features.py`

**Purpose:** Convert preprocessed audio into speaker embeddings (192-dimensional vectors).

**Key Functions:**
```python
def load_ecapa_model():
    """Load pretrained ECAPA-TDNN model from SpeechBrain."""
    from speechbrain.pretrained import SpeakerRecognition
    classifier = SpeakerRecognition.from_hparams(
        source="speechbrain/speaker-recognition-ecapa-voxceleb",
        savedir="models/speaker_model"
    )
    return classifier

def extract_features(audio_signal, sample_rate=16000):
    """
    Extract 192-dimensional speaker embedding from audio.
    
    Args:
        audio_signal (np.ndarray): Preprocessed audio (mono, 16kHz)
        sample_rate (int): Sample rate (should be 16000)
    
    Returns:
        np.ndarray: 192-dimensional embedding vector
    """
    classifier = load_ecapa_model()
    # Convert numpy to torch tensor
    import torch
    signal_tensor = torch.from_numpy(audio_signal).float()
    signal_tensor = signal_tensor.unsqueeze(0)  # Add batch dimension
    
    # Extract embedding
    with torch.no_grad():
        embeddings = classifier.encode_batch(signal_tensor)
    
    return embeddings.squeeze().numpy()
```

**Model Details:**
- **ECAPA-TDNN:** Emphasized Channel Attention, Propagation, and Aggregation in Time-Delay Neural Networks.
- **Output:** 192-dimensional vector (embedding).
- **Pretrained on:** VoxCeleb dataset (diverse speaker corpus).
- **Advantages:** Fast inference, robust to variations, proven accuracy.

**Alternative Features (MFCC-based):**
```python
def extract_mfcc(signal, sr=16000, n_mfcc=13):
    """Extract Mel-Frequency Cepstral Coefficients (simpler alternative)."""
    mfcc = librosa.feature.mfcc(y=signal, sr=sr, n_mfcc=n_mfcc)
    return np.mean(mfcc.T, axis=0)  # Returns 13-dim vector
```

---

### `src/model/profile_manager.py`

**Purpose:** Manage user voice profiles, embeddings, and persistent storage.

**Key Functions:**
```python
def load_profile(user_id):
    """
    Load user's voice profile (averaged embedding).
    
    Args:
        user_id (str): User identifier
    
    Returns:
        np.ndarray: Averaged embedding vector (192-dim)
    """
    profile_path = f"data/profile/users/{user_id}/user_profile.npy"
    if os.path.exists(profile_path):
        return np.load(profile_path)
    return None

def save_embedding(user_id, embedding):
    """
    Save a new embedding to user's profile.
    
    Args:
        user_id (str): User identifier
        embedding (np.ndarray): New embedding vector (192-dim)
    """
    user_dir = f"data/profile/users/{user_id}"
    os.makedirs(user_dir, exist_ok=True)
    
    # Save individual embedding with unique filename
    embedding_path = f"{user_dir}/embeddings/{uuid.uuid4()}.npy"
    os.makedirs(f"{user_dir}/embeddings", exist_ok=True)
    np.save(embedding_path, embedding)
    
    # Update averaged profile
    update_profile_average(user_id)

def update_profile_average(user_id):
    """
    Recompute and save the averaged user profile.
    
    Aggregates all individual embeddings into a single profile vector.
    """
    embedding_dir = f"data/profile/users/{user_id}/embeddings"
    embeddings = []
    
    for filename in os.listdir(embedding_dir):
        if filename.endswith('.npy'):
            emb = np.load(os.path.join(embedding_dir, filename))
            embeddings.append(emb)
    
    if embeddings:
        avg_embedding = np.mean(embeddings, axis=0)
        profile_path = f"data/profile/users/{user_id}/user_profile.npy"
        np.save(profile_path, avg_embedding)

def create_user_directory(user_id):
    """Create directory structure for new user."""
    user_dir = f"data/profile/users/{user_id}"
    os.makedirs(f"{user_dir}/embeddings", exist_ok=True)
    
    # Create user metadata
    user_info = {
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        "embeddings_count": 0
    }
    with open(f"{user_dir}/user_metadata.json", 'w') as f:
        json.dump(user_info, f)
```

**Design:**
- **Individual Embeddings:** Each voice sample is saved as a separate `.npy` file for versioning and auditing.
- **Averaged Profile:** The mean of all embeddings serves as the user's canonical voice profile.
- **Continual Learning:** New embeddings are added over time; the average is recomputed, allowing the profile to adapt.

---

### `src/model/verify_voice.py`

**Purpose:** Compare test voice embeddings against stored user profiles for authentication.

**Key Functions:**
```python
def verify_voice(user_id, test_embedding, threshold=0.80):
    """
    Verify if test embedding matches user's stored profile.
    
    Args:
        user_id (str): User identifier
        test_embedding (np.ndarray): New embedding (192-dim)
        threshold (float): Cosine similarity threshold (0-1, default 0.80)
    
    Returns:
        tuple: (is_match: bool, score: float)
    """
    stored_profile = load_profile(user_id)
    if stored_profile is None:
        return False, 0.0
    
    # Compute cosine similarity
    similarity = compute_cosine_similarity(test_embedding, stored_profile)
    
    # Decision based on threshold
    is_match = similarity >= threshold
    
    return is_match, similarity

def compute_cosine_similarity(vec1, vec2):
    """
    Compute cosine similarity between two vectors.
    
    Formula: cos(θ) = (A·B) / (||A|| * ||B||)
    Range: 0 to 1 (higher = more similar)
    
    Args:
        vec1, vec2 (np.ndarray): Vectors to compare
    
    Returns:
        float: Similarity score
    """
    from sklearn.metrics.pairwise import cosine_similarity
    similarity = cosine_similarity([vec1], [vec2])[0][0]
    return similarity
```

**Verification Process:**
1. Load the user's stored profile embedding (average of past samples).
2. Compute cosine similarity between new test embedding and stored profile.
3. Compare score against configurable threshold (typically 0.75–0.85).
4. Return match verdict and similarity score.

**Dual-Verification (Optional Enhancement):**
For enhanced security, implement:
```python
def dual_verify(user_id, test_embedding, claimed_id, threshold=0.80):
    """
    Verify using both:
    1. Cosine similarity threshold
    2. Speaker classification (NN predicts who spoke)
    """
    # Method 1: Cosine similarity
    is_match_similarity, score = verify_voice(user_id, test_embedding, threshold)
    
    # Method 2: Speaker classification
    predicted_id = classify_speaker(test_embedding)
    is_match_classifier = (predicted_id == claimed_id)
    
    # Grant access only if both pass
    return is_match_similarity and is_match_classifier, score
```

---

### `src/security/antispoof.py`

**Purpose:** Detect spoofing attacks (replay, synthetic, deepfake) and verify active liveness.

**Key Functions:**
```python
def detect_spoof(audio_signal, sample_rate, challenge_phrase, user_response):
    """
    Main anti-spoofing check using multiple signal analyses.
    
    Args:
        audio_signal (np.ndarray): Preprocessed audio
        sample_rate (int): Sample rate (16000)
        challenge_phrase (str): Expected challenge (e.g., "7")
        user_response (str): What user actually said
    
    Returns:
        tuple: (is_spoof: bool, confidence: float, reason: str)
    """
    # Check 1: Active challenge verification
    if not matches_challenge(challenge_phrase, user_response):
        return True, 0.95, "Challenge phrase mismatch"
    
    # Check 2: Zero-Crossing Rate analysis
    zcr = compute_zcr(audio_signal)
    if is_zcr_abnormal(zcr):
        return True, 0.80, "Abnormal ZCR (possible replay)"
    
    # Check 3: Spectral flatness (indicates unnatural speech)
    flatness = compute_spectral_flatness(audio_signal, sample_rate)
    if flatness > FLATNESS_THRESHOLD:
        return True, 0.75, "High spectral flatness (possible synthetic audio)"
    
    # Check 4: Energy/Volume check
    energy = compute_energy(audio_signal)
    if energy < ENERGY_THRESHOLD:
        return True, 0.60, "Low energy (possible silent/muffled recording)"
    
    # All checks passed
    return False, 0.05, "Liveness verified"

def compute_zcr(signal):
    """
    Zero-Crossing Rate: number of times signal crosses zero per frame.
    Live speech has higher ZCR than replayed audio.
    """
    zcr = librosa.feature.zero_crossing_rate(signal)[0]
    return np.mean(zcr)

def compute_spectral_flatness(signal, sample_rate):
    """
    Spectral flatness (Wiener entropy): 1 = noise-like, 0 = tonal.
    Replayed audio tends to have low flatness (more tonal).
    """
    from scipy.signal import periodogram
    frequencies, power = periodogram(signal, sample_rate)
    # Wiener entropy: -sum(p * log(p)) where p is normalized power
    p = power / np.sum(power)
    flatness = -np.sum(p * np.log(p + 1e-10))
    return flatness

def matches_challenge(challenge, response):
    """
    Verify user responded with correct challenge phrase.
    Could use simple string matching or speech-to-text.
    """
    # Simple matching (could be enhanced with speech recognition)
    challenge_words = challenge.lower().split()
    response_words = response.lower().split()
    
    # Check if challenge words appear in response
    for word in challenge_words:
        if word in response_words:
            return True
    return False
```

**Anti-Spoofing Strategies:**
1. **Active Liveness:** Random challenge-response requires real-time synthesis.
2. **Signal Analysis:** ZCR, spectral features, energy detect acoustic anomalies.
3. **Multi-Factor:** Combining multiple checks increases robustness.

**Detection Thresholds (configurable):**
- **ZCR:** Normal speech 0.1–0.3; replayed audio 0.05–0.15.
- **Spectral Flatness:** Normal speech 5–7; synthetic audio 8–10.
- **Energy:** Normal speech > -40 dB; silence/muffled < -50 dB.

---

### `src/learning/continual_learning.py`

**Purpose:** Implement continual learning—profile updates based on new successful authentications.

**Key Functions:**
```python
def save_embedding_after_auth(user_id, embedding, success=True):
    """
    Save embedding after successful authentication.
    
    Args:
        user_id (str): User identifier
        embedding (np.ndarray): New embedding (192-dim)
        success (bool): Whether authentication was successful
    
    Returns:
        bool: Success status
    """
    if not success:
        # Optionally log failed attempts but don't update profile
        log_failed_embedding(user_id, embedding)
        return False
    
    # Save to profile manager
    profile_manager.save_embedding(user_id, embedding)
    
    # Update profile average
    profile_manager.update_profile_average(user_id)
    
    return True

def enable_weighted_continual_learning(user_id, embedding, recency_weight=0.7):
    """
    Advanced: Weighted average favoring recent samples.
    
    This allows profiles to adapt to gradual voice changes while
    preserving core characteristics.
    
    Args:
        user_id (str): User identifier
        embedding (np.ndarray): New embedding
        recency_weight (float): Weight for new sample (0-1)
    """
    existing_profile = profile_manager.load_profile(user_id)
    
    if existing_profile is None:
        # First sample
        profile_manager.save_embedding(user_id, embedding)
        return
    
    # Weighted average: new sample has higher weight
    updated_profile = (recency_weight * embedding + 
                      (1 - recency_weight) * existing_profile)
    
    # Save updated profile
    profile_path = f"data/profile/users/{user_id}/user_profile.npy"
    np.save(profile_path, updated_profile)
```

**Continual Learning Benefits:**
- **Voice Adaptation:** Profiles evolve with natural voice changes (aging, accent, emotion).
- **Environmental Adaptation:** Adjust to different microphone or acoustic conditions.
- **Improving Accuracy:** More samples lead to better average profile.
- **Robustness:** System becomes more resilient to variations over time.

**Considerations:**
- Only update on **successful** authentication to avoid poisoning profile with impostors.
- Optionally use **weighted averaging** to give recent samples more influence.
- Periodically **review profiles** for drift or anomalies.

---

### `src/evaluation/logger.py`

**Purpose:** Log all authentication events for auditing and analysis.

**Key Functions:**
```python
def log_auth_event(user_id, action, score, spoof_detected, result):
    """
    Log authentication attempt to CSV.
    
    Args:
        user_id (str): User identifier
        action (str): "lock" or "unlock"
        score (float): Similarity score (0-1)
        spoof_detected (bool): Whether spoof was detected
        result (str): "success" or "failure"
    """
    import csv
    log_path = "data/evaluation/log.csv"
    
    os.makedirs("data/evaluation", exist_ok=True)
    
    # Create header if file doesn't exist
    if not os.path.exists(log_path):
        with open(log_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'timestamp', 'user_id', 'action', 'score', 
                'spoof_detected', 'result'
            ])
    
    # Append new entry
    with open(log_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            user_id,
            action,
            f"{score:.4f}",
            spoof_detected,
            result
        ])

def retrieve_auth_logs(user_id=None, start_date=None, end_date=None):
    """Retrieve and filter authentication logs."""
    log_path = "data/evaluation/log.csv"
    logs = []
    
    with open(log_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if user_id and row['user_id'] != user_id:
                continue
            # Optional date filtering
            logs.append(row)
    
    return logs
```

**Log CSV Schema:**
```
timestamp,user_id,action,score,spoof_detected,result
2024-04-22T10:15:30.123456,user_1,lock,0.9234,False,success
2024-04-22T10:16:45.234567,user_1,unlock,0.8756,False,success
2024-04-22T10:17:12.345678,user_2,unlock,0.4123,True,failure
```

**Use Cases:**
- **Audit Trails:** Track who accessed what and when.
- **Security Monitoring:** Detect repeated failed attempts (brute force attempts).
- **Performance Analysis:** Monitor FAR/FRR rates, identify problematic users.
- **Compliance:** Evidence of authentication for regulatory purposes.

---

### `src/evaluation/metrics.py`

**Purpose:** Compute performance metrics for authentication system evaluation.

**Key Functions:**
```python
def compute_far(logs, threshold=0.80):
    """
    False Accept Rate (FAR): % of impostor attempts incorrectly accepted.
    
    Lower is better (more secure).
    """
    impostor_attempts = [log for log in logs if log['is_impostor']]
    if not impostor_attempts:
        return 0.0
    
    false_accepts = sum(1 for log in impostor_attempts if float(log['score']) >= threshold)
    far = false_accepts / len(impostor_attempts)
    return far

def compute_frr(logs, threshold=0.80):
    """
    False Reject Rate (FRR): % of genuine attempts incorrectly rejected.
    
    Lower is better (more usable).
    """
    genuine_attempts = [log for log in logs if not log['is_impostor']]
    if not genuine_attempts:
        return 0.0
    
    false_rejects = sum(1 for log in genuine_attempts if float(log['score']) < threshold)
    frr = false_rejects / len(genuine_attempts)
    return frr

def compute_equal_error_rate(logs):
    """
    Equal Error Rate (EER): Threshold where FAR == FRR.
    
    Lower EER indicates better system performance.
    Balances security and usability.
    """
    thresholds = np.linspace(0, 1, 100)
    min_diff = float('inf')
    eer = 0.5
    
    for t in thresholds:
        far = compute_far(logs, t)
        frr = compute_frr(logs, t)
        diff = abs(far - frr)
        if diff < min_diff:
            min_diff = diff
            eer = (far + frr) / 2
    
    return eer
```

**Metrics Interpretation:**
- **FAR (False Accept Rate):** % of unauthorized access attempts that succeed. Target: < 1%
- **FRR (False Reject Rate):** % of legitimate users denied access. Target: < 5%
- **EER (Equal Error Rate):** Balance point where FAR = FRR. Lower is better. Typical: 2–5%
- **ROC Curve:** Plots FAR vs FRR across thresholds to visualize system performance.

---

## How It Works

### Voice Registration (Lock Workflow)

```
User Action                      System Response
─────────────────────────────────────────────────────────────
1. Enter ID & Name               └─► Validate inputs
                                 └─► Check if user exists

2. Upload File                   └─► Store file reference
                                 └─► Create user dir if needed

3. See Challenge                 └─► Generate random number (0-9)
                                 └─► Display: "Say 3"

4. Speak Number                  └─► Record 6 seconds audio
                                 └─► Receive raw waveform

5. Processing...                 └─► Preprocess audio
                                     - Convert to mono
                                     - Resample to 16 kHz
                                     - Normalize amplitude
                                 
                                 └─► Extract ECAPA embedding
                                     - Load pretrained model
                                     - Compute 192-dim vector
                                 
                                 └─► Save embedding
                                     - Store as .npy file
                                     - Update profile average

6. "File Locked!"                └─► Move file to locked_file/
                                 └─► Record metadata
                                 └─► Display success
```

**Data Stored:**
- User profile directory created at `data/profile/users/<user_id>/`
- Individual embedding saved: `data/profile/users/<user_id>/embeddings/<uuid>.npy`
- Average profile updated: `data/profile/users/<user_id>/user_profile.npy`
- Locked file stored: `data/locked_file/<filename>`
- Metadata saved: `data/locked_file/lock_meta.json`

---

### Voice Verification (Unlock Workflow)

```
User Action                      System Response
─────────────────────────────────────────────────────────────
1. Enter ID & Name               └─► Load lock metadata
                                 └─► Verify user/file association

2. See New Challenge             └─► Generate different random number
                                 └─► Display: "Say 7"

3. Speak Number                  └─► Record 6 seconds audio
                                 └─► Receive raw waveform

4. Processing...                 └─► Preprocess audio
                                     (same as registration)
                                 
                                 └─► ANTI-SPOOF CHECK
                                     - Compute ZCR
                                     - Check spectral flatness
                                     - Verify challenge match
                                     ❌ If spoof detected → REJECT
                                 
                                 └─► Extract ECAPA embedding
                                 
                                 └─► VOICE VERIFICATION
                                     - Load user profile
                                     - Compute cosine similarity
                                     ❌ If score < 0.80 → REJECT
                                 
                                 └─► LOG ATTEMPT
                                     - Timestamp, user, score, result

5a. GRANTED (score ≥ 0.80)      └─► Update profile (optional)
                                 └─► Stream file for download
                                 └─► Clear metadata

5b. DENIED (spoof or low score)  └─► Display error message
                                 └─► Suggest retry
```

**Decision Logic:**
```
IF (spoof_detected == True)  THEN
    REJECT with reason "Spoofing detected"
ELSE IF (cosine_similarity < 0.80) THEN
    REJECT with reason "Voice does not match profile"
ELSE
    ACCEPT and download file
    OPTIONALLY update profile with new embedding
END IF
```

---

## Security Design

### Anti-Spoofing & Liveness Detection

**Multi-Layer Defense:**

1. **Active Liveness (Challenge-Response)**
   - User must repeat a random number spoken by the system.
   - Attackers cannot simply replay a static recording.
   - Each unlock requires a new number, preventing pre-recorded attacks.

2. **Signal Analysis**
   - **Zero-Crossing Rate (ZCR):** Live speech has natural variation; replayed audio is often cleaner (lower ZCR).
   - **Spectral Flatness:** Measures how noise-like the signal is; synthetic/replayed audio often has unnatural spectral characteristics.
   - **Energy/Volume:** Legitimate speech has expected energy levels; extremely quiet or distorted recordings are flagged.

3. **Challenge Matching**
   - Simple word/number matching verifies user actually said the challenge.
   - Could be enhanced with speech-to-text for robustness.

4. **Multi-Factor Gate**
   - Access is denied if ANY check fails:
     - Spoof detection → REJECT (even if similarity passes)
     - Similarity below threshold → REJECT

**Limitations:**
- **Simple ZCR checks** may not catch sophisticated deepfakes.
- **Deep learning-based spoofing detection** (future enhancement) would provide stronger protection.

---

### Authentication Logs

All authentication events are logged to `data/evaluation/log.csv`:

```csv
timestamp,user_id,action,score,spoof_detected,result
2024-04-22T14:30:15,user_1,unlock,0.85,False,success
2024-04-22T14:32:40,user_2,unlock,0.42,False,failure
2024-04-22T14:35:10,attacker,unlock,0.78,True,failure
```

**Use Cases:**
- **Intrusion Detection:** Multiple failed attempts from same user/IP.
- **Compliance:** Audit trail for regulatory requirements.
- **Performance Monitoring:** Track FAR/FRR and adjust thresholds.
- **User Support:** Review logs to help users troubleshoot.

---

### File Encryption

**Optional Feature:** Protect locked files at rest using symmetric encryption.

**Implementation (AES-256):**
```python
from cryptography.fernet import Fernet
import os

def encrypt_file(input_path, output_path):
    """Encrypt file using AES."""
    # Generate or load key
    key = Fernet.generate_key()
    cipher = Fernet(key)
    
    # Read file
    with open(input_path, 'rb') as f:
        data = f.read()
    
    # Encrypt
    encrypted = cipher.encrypt(data)
    
    # Save encrypted file
    with open(output_path, 'wb') as f:
        f.write(encrypted)
    
    # Store key securely (e.g., in lock_meta.json)
    return key

def decrypt_file(input_path, key):
    """Decrypt file using stored key."""
    cipher = Fernet(key)
    with open(input_path, 'rb') as f:
        encrypted_data = f.read()
    decrypted = cipher.decrypt(encrypted_data)
    return decrypted
```

**Encryption Comparison:**

| Method | Speed | Security | Complexity | Use Case |
|--------|-------|----------|-----------|----------|
| **AES-256 (Fernet)** | Fast | Excellent | Medium | Large files (recommended) |
| **RSA-2048** | Slow | Excellent | High | Small payloads, key exchange |
| **No Encryption** | N/A | None | Low | Testing, trusted environments |

**Deployment:**
- Files are encrypted when locked and decrypted only on successful unlock.
- Keys can be stored in `lock_meta.json` or derived from user credentials.
- In production, use environment variables or secure key management (e.g., AWS KMS).

---

## Installation & Setup

### Prerequisites

- **Python 3.8+** (tested on 3.8–3.11)
- **Microphone:** Working audio input device
- **Disk Space:** ~500 MB for models and data
- **RAM:** ~2–4 GB (depending on concurrent users)

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/Voice-Based-Authentication-Using-Deep-Learning.git
cd Voice-Based-Authentication-Using-Deep-Learning
```

### Step 2: Create Virtual Environment

```bash
# Using venv (recommended)
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Key Dependencies:**
```
streamlit>=1.20.0          # Web UI
numpy>=1.21.0              # Numerical computing
scipy>=1.8.0               # Scientific computing
librosa>=0.10.0            # Audio processing
sounddevice>=0.4.5         # Microphone recording
soundfile>=0.12.0          # Audio file I/O
speechbrain>=0.5.12        # ECAPA-TDNN model
torch>=1.10.0              # PyTorch (for SpeechBrain)
torchaudio>=0.10.0         # Audio support for PyTorch
scikit-learn>=1.0.0        # ML utilities (cosine similarity)
cryptography>=3.4.8        # File encryption (optional)
noisereduce>=2.0.0         # Noise reduction (optional)
pyyaml>=6.0                # Configuration files
pandas>=1.3.0              # Data analysis
matplotlib>=3.4.0          # Visualization (optional)
```

### Step 4: Create Directory Structure

```bash
mkdir -p data/locked_file
mkdir -p data/profile/users
mkdir -p data/evaluation
mkdir -p data/processed_audio
mkdir -p data/raw_audio
mkdir -p models/speaker_model
```

### Step 5: Download Pretrained Model

The ECAPA-TDNN model will be automatically downloaded on first use. Alternatively, pre-download:

```bash
python3 -c "
from speechbrain.pretrained import SpeakerRecognition
classifier = SpeakerRecognition.from_hparams(
    source='speechbrain/speaker-recognition-ecapa-voxceleb',
    savedir='models/speaker_model'
)
print('Model downloaded successfully!')
"
```

### Step 6: Configure Application

Edit `configs/config.yaml`:

```yaml
audio:
  sample_rate: 16000        # Standard for speaker recognition
  duration: 6               # Recording duration in seconds
  bit_depth: 16             # 16-bit audio

paths:
  raw_audio: data/raw_audio
  processed_audio: data/processed_audio
  embeddings: data/embeddings
  locked_files: data/locked_file
  logs: data/evaluation

model:
  threshold: 0.80           # Cosine similarity threshold
  model_name: "ecapa-voxceleb"
  embedding_dim: 192

anti_spoof:
  zcr_threshold: 0.15
  flatness_threshold: 0.5
  energy_threshold: -40     # dB
```

### Step 7: Start Application

```bash
# Web UI (Streamlit)
streamlit run src/streamlit_app.py

# CLI (optional)
cd src
python main.py
```

The app opens at `http://localhost:8501` (Streamlit default).

---

## Configuration

### `configs/config.yaml`

Controls system behavior and thresholds:

```yaml
audio:
  sample_rate: 16000           # Hz - standard for speaker models
  duration: 6                  # seconds per recording
  bit_depth: 16                # audio resolution

paths:
  base_data: data              # Root data directory
  raw_audio: data/raw_audio    # Original recordings
  processed_audio: data/processed_audio  # After preprocessing
  embeddings: data/embeddings
  locked_files: data/locked_file
  profiles: data/profile/users
  logs: data/evaluation

model:
  # ECAPA-TDNN configuration
  embedding_model: "speechbrain/speaker-recognition-ecapa-voxceleb"
  embedding_dim: 192           # Output dimension
  model_checkpoint: models/speaker_model

verification:
  threshold: 0.80              # Cosine similarity threshold (0-1)
  # Higher threshold = more secure but more false rejections
  # Lower threshold = more permissive but higher false accepts
  
  confidence_required: 0.75    # Min confidence for classification
  
anti_spoof:
  enabled: true
  zcr_threshold: 0.15          # Zero-Crossing Rate threshold
  flatness_threshold: 0.5      # Spectral flatness threshold
  energy_threshold: -40        # Energy threshold (dB)
  
continual_learning:
  enabled: true
  recency_weight: 0.7          # Weight for new samples (0-1)
  max_embeddings_per_user: 100 # Limit profile size

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  log_file: data/evaluation/system.log
  
encryption:
  enabled: false               # Enable file encryption (AES-256)
  algorithm: "Fernet"          # Encryption algorithm
  key_storage: "metadata"      # Store key in lock_meta.json
```

### `data/profile/user_info.json`

Global user metadata:

```json
{
  "users": [
    {
      "user_id": "user_1",
      "name": "Alice",
      "created_at": "2024-04-22T10:00:00",
      "last_auth": "2024-04-22T14:30:15",
      "embeddings_count": 8,
      "status": "active"
    },
    {
      "user_id": "user_2",
      "name": "Bob",
      "created_at": "2024-04-21T09:00:00",
      "last_auth": "2024-04-22T13:45:00",
      "embeddings_count": 5,
      "status": "active"
    }
  ]
}
```

### `data/locked_file/lock_meta.json`

Metadata for locked files:

```json
{
  "locks": [
    {
      "locked_file": "report.pdf",
      "user_id": "user_1",
      "locked_at": "2024-04-22T10:15:30",
      "encryption_enabled": false,
      "access_count": 2
    }
  ]
}
```

---

## Usage Examples

### Example 1: Basic Registration (Lock)

```
Step 1: Enter ID and Name
┌────────────────────────────┐
│ User ID: [alice           ]│
│ Name: [Alice Johnson      ]│
└────────────────────────────┘

Step 2: Upload File
┌────────────────────────────┐
│ Choose File: [report.pdf  ]│
└────────────────────────────┘

Step 3: Voice Recording
┌────────────────────────────┐
│ Say the number: 5           │
│ [Recording... 3 seconds]    │
│ [Processing...]            │
│ File locked successfully! ✓ │
└────────────────────────────┘
```

### Example 2: Authentication (Unlock)

```
Step 1: Enter Credentials
┌────────────────────────────┐
│ User ID: [alice           ]│
│ Name: [Alice Johnson      ]│
└────────────────────────────┘

Step 2: Challenge
┌────────────────────────────┐
│ Say the number: 8           │
│ [Recording... 6 seconds]    │
│ [Processing...]            │
│ Similarity Score: 0.87      │
│ Liveness: Verified ✓        │
│ Access Granted! Download ▼  │
└────────────────────────────┘
```

### Example 3: Failed Authentication

```
Scenario: Different voice or replay attempt
┌────────────────────────────────────────┐
│ User ID: [attacker                    ]│
│ Say the number: 3                      │
│ [Recording... 6 seconds]               │
│ [Processing...]                        │
│ ❌ Access Denied                        │
│ Reason: Spoof detected (abnormal ZCR) │
│ Attempted: 2024-04-22 14:35:10        │
│ Please try again...                    │
└────────────────────────────────────────┘
```

### Example 4: CLI Usage (main.py)

```bash
$ python src/main.py

========================================
   Voice-Based Authentication System
========================================

1. Register Voice
2. Authenticate Voice
3. View Authentication History
4. Exit

Choose option: 1

Enter User ID: alice
Enter Name: Alice Johnson
Enter file path to lock: /path/to/report.pdf

Say the number: 4
Recording...
Processing embedding...
File locked successfully!
Profile updated. Total embeddings: 3

========================================
Choose option: 2

Enter User ID: alice
Enter Name: Alice Johnson
Say the number: 7
Recording...
Verifying voice...
Similarity: 0.85
ACCESS GRANTED! File ready for download.

Authentication logged to data/evaluation/log.csv
```

---

## Evaluation Metrics

The system supports comprehensive performance evaluation:

### Metrics Computed

1. **False Accept Rate (FAR):** % of impostor attempts incorrectly accepted.
   - Lower is better (more secure)
   - Target: < 1%
   - Formula: `FAR = (False Accepts) / (Total Impostor Attempts)`

2. **False Reject Rate (FRR):** % of genuine attempts incorrectly rejected.
   - Lower is better (more usable)
   - Target: < 5%
   - Formula: `FRR = (False Rejects) / (Total Genuine Attempts)`

3. **Equal Error Rate (EER):** Threshold where FAR = FRR.
   - Lower EER = better overall performance
   - Typical: 2–5% for voice systems
   - Balance point between security and usability

4. **ROC Curve:** Trade-off between FAR and FRR across thresholds.

### Example Evaluation Script

```python
from src.evaluation.metrics import compute_far, compute_frr, compute_equal_error_rate
import pandas as pd

# Load logs
logs_df = pd.read_csv('data/evaluation/log.csv')

# Compute metrics
far = compute_far(logs_df, threshold=0.80)
frr = compute_frr(logs_df, threshold=0.80)
eer = compute_equal_error_rate(logs_df)

print(f"FAR @ 0.80: {far:.2%}")
print(f"FRR @ 0.80: {frr:.2%}")
print(f"EER: {eer:.2%}")

# Interpret results
if far < 0.01 and frr < 0.05:
    print("✓ System performance is acceptable")
elif far > 0.05:
    print("⚠ FAR is high; raise threshold to improve security")
elif frr > 0.20:
    print("⚠ FRR is high; lower threshold to improve usability")
```

### Benchmark

Typical performance on a well-tuned system:

| Metric | Target | Typical | Notes |
|--------|--------|---------|-------|
| FAR | < 0.5% | 0.1–1% | Lower = more secure |
| FRR | < 5% | 2–8% | Lower = more usable |
| EER | 2–5% | 1–5% | Balance metric |
| Inference Time | < 500ms | 200–400ms | Per unlock |
| Model Size | < 50MB | 30–40MB | ECAPA-TDNN |

---

## Testing & Troubleshooting

### Common Issues

#### 1. **Microphone Not Detected**

**Symptoms:** "No audio device found" error.

**Solutions:**
```bash
# List available audio devices
python -c "import sounddevice; print(sounddevice.query_devices())"

# Specify device in code
from src.audio.recorder import record_voice
audio, sr = record_voice(device=1)  # Use device index 1
```

#### 2. **Poor Authentication Performance (High FRR)**

**Symptoms:** Legitimate users frequently denied access.

**Solutions:**
- **Lower threshold:** Reduce from 0.80 to 0.75 in `config.yaml`.
- **Improve audio quality:** Use a better microphone or quieter environment.
- **Add more training samples:** Have users register multiple times.

```yaml
model:
  threshold: 0.75  # More permissive
```

#### 3. **Spoof Detection Too Strict**

**Symptoms:** Legitimate attempts flagged as spoofing.

**Solutions:**
```yaml
anti_spoof:
  zcr_threshold: 0.20      # Increase from 0.15
  flatness_threshold: 0.6  # Increase from 0.5
```

#### 4. **FileNotFoundError: User Profile**

**Symptoms:** `data/profile/users/<id>/embeddings` not found.

**Solution:** Ensure user has registered (locked a file) first. User directories are created on first lock.

```bash
# Manually create if needed
mkdir -p data/profile/users/alice/embeddings
```

#### 5. **Model Download Fails**

**Symptoms:** `ConnectionError` or slow model loading.

**Solution:** Pre-download model or use offline mode:
```bash
python -c "
from speechbrain.pretrained import SpeakerRecognition
# Download once
classifier = SpeakerRecognition.from_hparams(
    source='speechbrain/speaker-recognition-ecapa-voxceleb',
    savedir='models/speaker_model',
    run_opts={'device': 'cpu'}
)
"
```

#### 6. **TypeError: Expected 1D or 2D array**

**Symptoms:** Shape mismatch in cosine_similarity.

**Solution:** Ensure embeddings are 1D (192,) not (1, 192):
```python
# Correct
embedding = embedding.flatten()  # (192,)

# Verify
assert embedding.ndim == 1 and embedding.shape[0] == 192
```

### Running Tests

```bash
# Unit tests (if provided)
pytest tests/ -v

# Manual testing
python src/main.py

# Audio device test
python -c "
import sounddevice as sd
import numpy as np
print('Testing audio...')
recording = sd.rec(int(3*16000), samplerate=16000, channels=1)
sd.wait()
print(f'Recorded shape: {recording.shape}')
print('✓ Audio test passed')
"
```

---

## Deployment Notes

### Local Deployment

```bash
streamlit run src/streamlit_app.py
# App opens at http://localhost:8501
```

### Cloud Deployment (Streamlit Cloud)

1. Push repository to GitHub
2. Go to https://share.streamlit.io
3. Create new app → Select repository and main file (`src/streamlit_app.py`)
4. Deploy

**Considerations:**
- Streamlit Cloud has audio limitations; test microphone access.
- File size limits (~200 MB); cache models locally if possible.

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "src/streamlit_app.py"]
```

Build and run:
```bash
docker build -t voicelock .
docker run -p 8501:8501 --device /dev/snd voicelock
# --device /dev/snd passes audio device to container
```

### Environment Variables

```bash
# Optional configurations
export VOICELOCK_THRESHOLD=0.75
export VOICELOCK_ANTI_SPOOF=true
export VOICELOCK_ENCRYPTION=false
export VOICELOCK_LOG_LEVEL=DEBUG
```

---

## Performance Considerations

### Scalability

| Component | Limit | Mitigation |
|-----------|-------|-----------|
| **Users** | ~100 (file-based) | Switch to database for > 100 users |
| **Files per user** | 1 (current) | Extend metadata schema for multiple locks |
| **Embeddings per user** | 100 (config) | Trim old embeddings or archive |
| **Inference time** | < 500ms | Use GPU or batch processing |

### Optimization Tips

1. **Model Caching:** Load ECAPA-TDNN once and reuse:
```python
# Global model cache
_model_cache = None

def get_model():
    global _model_cache
    if _model_cache is None:
        _model_cache = SpeakerRecognition.from_hparams(...)
    return _model_cache
```

2. **Batch Processing:** Process multiple embeddings in parallel.

3. **GPU Acceleration:** Use CUDA-enabled GPU for faster inference:
```python
classifier = SpeakerRecognition.from_hparams(
    source="speechbrain/speaker-recognition-ecapa-voxceleb",
    savedir="models/speaker_model",
    run_opts={"device": "cuda"}  # Use GPU
)
```

4. **Database Migration:** For production, migrate from file storage to SQLite/PostgreSQL:
```python
import sqlite3
conn = sqlite3.connect('voicelock.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    name TEXT,
    created_at TIMESTAMP
)''')
```

### Resource Requirements

| Resource | Requirement | Notes |
|----------|-------------|-------|
| **RAM** | 2–4 GB | Model + concurrent users |
| **Disk** | 500 MB–2 GB | Models + user data |
| **CPU** | 2+ cores | Inference feasible on any CPU |
| **GPU** (optional) | 2 GB VRAM | ~3x faster inference |
| **Network** | Broadband | For cloud deployment |

---

## Limitations

1. **Anti-Spoofing:** Simple ZCR checks may not catch sophisticated deepfakes or high-quality replay attacks. Advanced detection (e.g., fine-tuned Wav2Vec2) is needed.

2. **Single File Lock:** Currently supports one locked file per user. Multi-file locking requires schema changes.

3. **No Encryption by Default:** Files are stored unencrypted. Encryption must be explicitly enabled.

4. **Environmental Sensitivity:** Performance varies with microphone quality, background noise, and speaker variability.

5. **Voice Variability:** Speaker characteristics can change due to illness, emotion, age, or recording conditions.

6. **Database Scalability:** File-based storage is limited. Production systems should use SQL databases.

7. **User Management:** No GUI for admin functions. All management requires manual file/code changes.

8. **Liveness Bypass:** Sophisticated attacks (e.g., voice cloning) may eventually bypass the system. Regular security audits are recommended.

---

## Development Roadmap

### Phase 1–5: Core Implementation (Completed)

- ✅ Audio recording and preprocessing
- ✅ ECAPA-TDNN embeddings
- ✅ Voice verification
- ✅ Anti-spoofing detection
- ✅ Continual learning
- ✅ CLI & Streamlit UI

### Phase 6–10: Advanced Features (Planned)

#### Phase 6: Advanced Metrics & Analysis
- Scientific validation (EER, ROC curves)
- Robustness testing with synthetic noise
- Benchmark against VoxCeleb test set

#### Phase 7: Testing & QA
- Comprehensive pytest suite
- Dataset benchmarking
- Accuracy on diverse speakers

#### Phase 8: UI/UX Overhaul
- Dark mode, glassmorphism design
- Real-time waveform visualization
- Optimized inference for instant feedback

#### Phase 9: Hackathon-Winning Features
- Multi-modal authentication (voice + PIN/face)
- Physiological liveness (voiceprint variance)
- Embedded privacy (local-only processing, no cloud)

#### Phase 10: Deployment & Documentation
- Docker containerization
- Cloud deployment (Streamlit Cloud, AWS)
- High-quality documentation and video demo

### Future Enhancements

1. **Encrypted Profiles & Files:** Integrate `cryptography.Fernet` for AES encryption.
2. **Robust Anti-Spoofing:** Fine-tune Wav2Vec2 deepfake detector.
3. **Multi-File Support:** Extend metadata to track multiple locks per user.
4. **Database Backend:** Migrate from JSON/files to SQLite/PostgreSQL.
5. **Mobile App:** React Native or Flutter frontend.
6. **Advanced UI:** WebGL waveform visualization, progress animations.
7. **Cross-Platform:** Ensure macOS, Linux, Windows, and mobile compatibility.
8. **Continuous Deployment:** GitHub Actions CI/CD, automated testing.
9. **API Server:** RESTful backend for remote authentication.
10. **Blockchain Integration:** Immutable audit logs on public ledger (optional, experimental).

---

## Demonstration Checklist

Use this checklist to ensure a successful demo or evaluation:

- [ ] **1. User Registration & Lock**
  - Create new user (e.g., "Demo User")
  - Upload sample file (PDF, image, etc.)
  - Record voice for challenge
  - Confirm file locked successfully

- [ ] **2. Correct Voice Unlock**
  - Log in as same user
  - Respond to new challenge correctly
  - Verify high similarity score (> 0.85)
  - Confirm file downloads successfully

- [ ] **3. Incorrect Voice Rejection**
  - Attempt unlock with different voice or wrong phrase
  - Observe "Access Denied" message
  - Verify attempt logged with low score

- [ ] **4. Spoof Detection**
  - Try playing back original recording (replay attack)
  - Confirm system detects spoof
  - Verify "Spoofing detected" message
  - Check anti-spoof triggered correctly

- [ ] **5. Multi-User Isolation**
  - Create 2nd user and lock different file
  - Attempt 1st user to unlock 2nd user's file
  - Confirm access denied (user mismatch)
  - Verify users' profiles are isolated

- [ ] **6. Audit Logging**
  - Open `data/evaluation/log.csv`
  - Confirm all attempts recorded with timestamps
  - Verify success/failure marked correctly
  - Show similarity scores for each attempt

- [ ] **7. Error Handling**
  - Attempt unlock with non-existent user
  - Try unlock before any lock is registered
  - Observe graceful error messages (no crashes)
  - Confirm system recovers and allows retry

- [ ] **8. (Optional) Encryption**
  - Enable encryption in config
  - Lock a file with encryption
  - Verify on-disk file is encrypted (binary, not readable)
  - Unlock and confirm file decrypts correctly

- [ ] **9. Configuration**
  - Show `config.yaml` and adjustable parameters
  - Mention threshold tuning
  - Explain anti-spoof settings
  - Demonstrate config-driven behavior

- [ ] **10. Performance**
  - Measure recording-to-verification time (target < 10 seconds)
  - Show model size (~30–40 MB)
  - Demonstrate fast inference (< 500ms)
  - Discuss scalability for 10–100 users

- [ ] **11. Code Quality**
  - Show modular architecture (separate modules for audio, features, security)
  - Explain function responsibilities
  - Demonstrate logging and debugging
  - Highlight documentation

- [ ] **12. Security Highlights**
  - Explain anti-spoofing strategy (active challenge + signal analysis)
  - Show audit log for accountability
  - Discuss encryption option
  - Mention future deepfake detection

---

## References

### Academic Papers & Resources

1. **ECAPA-TDNN Model**
   - Desplanques, B., Thienpondt, J., & Demuynck, K. (2020). "ECAPA-TDNN: Emphasized Channel Attention, Propagation and Aggregation in TDNN Based Speaker Verification." In Proc. Interspeech.
   - Repository: https://github.com/speechbrain/speechbrain

2. **Speaker Recognition Overview**
   - Kinnunen, T., & Li, H. (2010). "An overview of speaker recognition." Handbook of Speaker and Language Recognition, 1-31.

3. **Voice Biometrics**
   - Campbell, J. P. (1997). "Speaker Recognition: A tutorial." Proceedings of the IEEE, 85(9), 1437-1462.

4. **Anti-Spoofing & Liveness Detection**
   - Todisco, M., Wang, X., & Evans, N. (2018). "ASVspoof 2019: Future Horizons through Short-term Spectral Features." arXiv preprint arXiv:1905.12986.
   - Pindrop Security: "Biometric Liveness Detection" – Uses ZCR, spectral features.

5. **Deep Learning Security**
   - Carlini, N., & Wagner, D. (2018). "Audio Adversarial Examples: Targeted Attacks on Speech-to-Text." arXiv preprint arXiv:1801.01944.
   - Discusses challenges in voice authentication security.

6. **Feature Extraction**
   - Logan, B. (2000). "Mel Frequency Cepstral Coefficients for Music Modeling." In ISMIR.
   - MFCCs as features for speech/speaker recognition.

7. **Cryptography & Encryption**
   - NIST Special Publication 800-38D: "Recommendation for Block Cipher Modes of Operation: Galois/Counter Mode (GCM) and GMAC."
   - AES recommended for file encryption.

8. **Deepfake Detection**
   - Baevski, A., Zhou, H., Mohamed, A., & Auli, M. (2020). "wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations." In NeurIPS.

### Libraries & Tools

- **Streamlit:** https://streamlit.io
- **SpeechBrain:** https://speechbrain.github.io
- **Librosa:** https://librosa.org
- **SciPy:** https://www.scipy.org
- **PyTorch:** https://pytorch.org
- **Cryptography:** https://cryptography.io
- **Noisereduce:** https://github.com/timsainb/noisereduce

### Datasets

- **VoxCeleb:** https://www.robots.ox.ac.uk/~vgg/data/voxceleb/ (Speaker recognition benchmark)
- **ASVspoof:** https://www.asvspoof.org (Anti-spoofing challenge)

---

## License

This project is developed as an academic semester project for educational purposes. It is provided as-is without any warranty. Use at your own discretion and adapt as needed for your specific use case.

---

## Contributors

- **Developer:** KARAN LODHI, AYUSH AGARAWAL, ANKUSH SHAKYA
- **Advisor:** DR. RUBY PANWAR
- **Institution:** GLA UNIVERSITY, MATHURA

---

## Contact & Support

For questions, issues, or contributions:

1. **GitHub Issues:** Open an issue with detailed reproduction steps.
2. **Email:** karanlodhi0552@gmail.com
3. **Documentation:** README.md for more details.

---

## Final Notes

VoiceLock demonstrates a complete voice biometric authentication system combining:
- **Deep Learning:** ECAPA-TDNN for robust speaker embeddings.
- **Security:** Multi-layer anti-spoofing and active liveness detection.
- **Usability:** Intuitive web UI with real-time feedback.
- **Adaptability:** Continual learning and profile updates.
- **Transparency:** Comprehensive logging and audit trails.

Whether used for academic study or as a foundation for production systems, this project provides insights into modern biometric authentication and serves as a template for secure, user-centric design.

**Thank you for exploring VoiceLock!**

---

*Last Updated: April 22, 2024*

