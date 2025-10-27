# VoiceGuard
# 🎙️ VoiceGuard - Voice-Authenticated Document Security System

A secure document management system that uses **voice biometrics** and **anti-spoofing detection** to protect sensitive files. Only the authenticated user's live voice can unlock their documents.

## 🔐 Key Features

- **Voice Biometric Authentication**: Uses MFCC (Mel-Frequency Cepstral Coefficients) and pitch analysis for unique voice identification
- **Anti-Spoofing Detection**: Prevents replay attacks by analyzing spectral characteristics, zero-crossing rate, and dynamic range
- **Secure Document Locking**: Upload documents that remain encrypted until voice authentication succeeds
- **Real-time Voice Recording**: Browser-based voice capture with waveform visualization
- **Multi-User Support**: Each user has isolated voice templates and document storage
- **Session Management**: Secure login/logout with Flask sessions

## 🛡️ Security Architecture

### Two-Factor Voice Verification:
1. **Liveness Detection** (Anti-Spoofing)
   - Spectral flux analysis
   - High-frequency energy ratio
   - Zero-crossing rate detection
   - Dynamic range verification
   - Signal-to-noise ratio estimation

2. **Voice Matching** (Biometric Authentication)
   - MFCC feature extraction (52 features)
   - Pitch analysis (fundamental frequency)
   - Cosine similarity comparison
   - Threshold-based authentication (70% match required)

## 🏗️ Tech Stack

- **Backend**: Flask, Python 3.x
- **Database**: SQLAlchemy + SQLite
- **Audio Processing**: 
  - `soundfile` - Audio I/O
  - `scipy` - Signal processing
  - `python_speech_features` - MFCC extraction
  - `numpy` - Numerical operations
- **Frontend**: HTML5, JavaScript, Web Audio API
- **Authentication**: Werkzeug password hashing, Flask sessions

## 📁 Project Structure
```
voiceguard/
├── app.py                  # Main Flask application
├── models.py               # Database models (User, Document)
├── extraction.py           # MFCC & pitch feature extraction
├── testing.py              # Voice authentication & spoof detection
├── record.py               # Audio file handling
├── templates/              # HTML templates
│   ├── index.html          # Login/Signup page
│   ├── record_template.html # One-time voice registration
│   ├── dashboard.html      # Document management
│   ├── unlock.html         # Voice authentication interface
│   └── admin.html          # Admin panel
└── data/                   # User data storage
    └── <user_id>/
        ├── template/       # Voice template audio
        ├── features/       # Extracted MFCC features
        ├── live/           # Live authentication recordings
        └── documents/      # Locked documents
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- FFmpeg (for audio conversion)

### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/voiceguard.git
cd voiceguard
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Access at `http://localhost:5000`

## 📖 Usage

### 1. User Registration
- Create account with username/password
- Record a 3-5 second voice template (one-time setup)
- Template is processed and stored as biometric signature

### 2. Upload Documents
- Upload files (PDF, TXT, DOC, images)
- Documents are automatically locked upon upload
- Maximum file size: 16MB

### 3. Unlock Documents
- Select a locked document
- Record live voice authentication
- System verifies:
  - ✅ Liveness (not a recording)
  - ✅ Voice match (your unique biometrics)
- Document unlocks on successful authentication

### 4. Download & Manage
- Download unlocked documents
- Delete documents anytime
- Track unlock history

## 🎯 Authentication Flow
```
User speaks → Browser records audio → Converts to WAV (16kHz mono)
                                              ↓
                                    Extract 57 features:
                                    - 52 MFCC statistics
                                    - 2 pitch features  
                                    - 3 spectral features
                                              ↓
                        ┌─────────────────────┴─────────────────────┐
                        ↓                                           ↓
              Spoof Detection                            Voice Matching
        (Spectral analysis)                      (Cosine similarity)
                Score > 50%                              Score > 70%
                        ↓                                           ↓
                        └─────────────────────┬─────────────────────┘
                                              ↓
                                    Both checks pass?
                                              ↓
                                      🔓 Document Unlocked
```

## 🔬 Feature Extraction Details

### MFCC Features (52 total):
- 13 coefficients × 4 statistics (mean, std, min, max)
- Captures vocal tract characteristics
- Robust to noise and pitch variations

### Pitch Features (2 total):
- Mean fundamental frequency (80-400 Hz)
- Standard deviation of pitch
- Identifies unique vocal cord vibrations

### Spectral Features (3 total):
- Energy (signal power)
- Zero-crossing rate (frequency estimate)
- Spectral centroid (brightness)

## 🧪 Testing

Test feature extraction:
```bash
python extraction.py path/to/audio.wav
```

Test authentication:
```bash
python testing.py data/1/live/live.wav data/1/features/features.npy
```

## 🔒 Security Considerations

✅ **Implemented:**
- Password hashing (Werkzeug)
- Session-based authentication
- User data isolation
- Anti-replay attack detection
- Voice biometric verification

⚠️ **Production Recommendations:**
- Use HTTPS in production
- Implement rate limiting
- Add CAPTCHA for signup/login
- Use stronger secret keys
- Consider encryption at rest for documents
- Add audit logging

## 📊 Performance

- **Template Recording**: 3-5 seconds
- **Feature Extraction**: ~0.5 seconds per audio file
- **Authentication**: ~1 second total
- **Supported Audio**: 0.5-10 seconds, 16kHz, mono

## 🐛 Troubleshooting

**Issue**: Verification shows 0.0% scores
- Ensure FFmpeg is installed
- Check audio files are properly converted to WAV
- Verify template was saved correctly

**Issue**: Microphone not working
- Grant browser microphone permissions
- Use HTTPS (required for some browsers)
- Check browser compatibility

**Issue**: Import errors
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check Python version (3.8+)

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Deep learning models for better accuracy
- Real-time streaming authentication
- Multi-language support
- Mobile app integration
- Cloud storage integration

## 📄 License

MIT License - see LICENSE file for details

## 👨‍💻 Author

Your Name - Aditi Nagendra
https://github.com/aditinagendra05

# 🎙️ VoiceGuard - Voice-Authenticated Document Security System

A secure document management system that uses **voice biometrics** and **anti-spoofing detection** to protect sensitive files. Only the authenticated user's live voice can unlock their documents.

## 🔐 Key Features

- **Voice Biometric Authentication**: Uses MFCC (Mel-Frequency Cepstral Coefficients) and pitch analysis for unique voice identification
- **Anti-Spoofing Detection**: Prevents replay attacks by analyzing spectral characteristics, zero-crossing rate, and dynamic range
- **Secure Document Locking**: Upload documents that remain encrypted until voice authentication succeeds
- **Real-time Voice Recording**: Browser-based voice capture with waveform visualization
- **Multi-User Support**: Each user has isolated voice templates and document storage
- **Session Management**: Secure login/logout with Flask sessions

## 🛡️ Security Architecture

### Two-Factor Voice Verification:
1. **Liveness Detection** (Anti-Spoofing)
   - Spectral flux analysis
   - High-frequency energy ratio
   - Zero-crossing rate detection
   - Dynamic range verification
   - Signal-to-noise ratio estimation

2. **Voice Matching** (Biometric Authentication)
   - MFCC feature extraction (52 features)
   - Pitch analysis (fundamental frequency)
   - Cosine similarity comparison
   - Threshold-based authentication (70% match required)

## 🏗️ Tech Stack

- **Backend**: Flask, Python 3.x
- **Database**: SQLAlchemy + SQLite
- **Audio Processing**: 
  - `soundfile` - Audio I/O
  - `scipy` - Signal processing
  - `python_speech_features` - MFCC extraction
  - `numpy` - Numerical operations
- **Frontend**: HTML5, JavaScript, Web Audio API
- **Authentication**: Werkzeug password hashing, Flask sessions

## 📁 Project Structure
```
voiceguard/
├── app.py                  # Main Flask application
├── models.py               # Database models (User, Document)
├── extraction.py           # MFCC & pitch feature extraction
├── testing.py              # Voice authentication & spoof detection
├── record.py               # Audio file handling
├── templates/              # HTML templates
│   ├── index.html          # Login/Signup page
│   ├── record_template.html # One-time voice registration
│   ├── dashboard.html      # Document management
│   ├── unlock.html         # Voice authentication interface
│   └── admin.html          # Admin panel
└── data/                   # User data storage
    └── <user_id>/
        ├── template/       # Voice template audio
        ├── features/       # Extracted MFCC features
        ├── live/           # Live authentication recordings
        └── documents/      # Locked documents
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- FFmpeg (for audio conversion)

### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/voiceguard.git
cd voiceguard
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Access at `http://localhost:5000`

## 📖 Usage

### 1. User Registration
- Create account with username/password
- Record a 3-5 second voice template (one-time setup)
- Template is processed and stored as biometric signature

### 2. Upload Documents
- Upload files (PDF, TXT, DOC, images)
- Documents are automatically locked upon upload
- Maximum file size: 16MB

### 3. Unlock Documents
- Select a locked document
- Record live voice authentication
- System verifies:
  - ✅ Liveness (not a recording)
  - ✅ Voice match (your unique biometrics)
- Document unlocks on successful authentication

### 4. Download & Manage
- Download unlocked documents
- Delete documents anytime
- Track unlock history

## 🎯 Authentication Flow
```
User speaks → Browser records audio → Converts to WAV (16kHz mono)
                                              ↓
                                    Extract 57 features:
                                    - 52 MFCC statistics
                                    - 2 pitch features  
                                    - 3 spectral features
                                              ↓
                        ┌─────────────────────┴─────────────────────┐
                        ↓                                           ↓
              Spoof Detection                            Voice Matching
        (Spectral analysis)                      (Cosine similarity)
                Score > 50%                              Score > 70%
                        ↓                                           ↓
                        └─────────────────────┬─────────────────────┘
                                              ↓
                                    Both checks pass?
                                              ↓
                                      🔓 Document Unlocked
```

## 🔬 Feature Extraction Details

### MFCC Features (52 total):
- 13 coefficients × 4 statistics (mean, std, min, max)
- Captures vocal tract characteristics
- Robust to noise and pitch variations

### Pitch Features (2 total):
- Mean fundamental frequency (80-400 Hz)
- Standard deviation of pitch
- Identifies unique vocal cord vibrations

### Spectral Features (3 total):
- Energy (signal power)
- Zero-crossing rate (frequency estimate)
- Spectral centroid (brightness)

## 🧪 Testing

Test feature extraction:
```bash
python extraction.py path/to/audio.wav
```

Test authentication:
```bash
python testing.py data/1/live/live.wav data/1/features/features.npy
```

## 🔒 Security Considerations

✅ **Implemented:**
- Password hashing (Werkzeug)
- Session-based authentication
- User data isolation
- Anti-replay attack detection
- Voice biometric verification

⚠️ **Production Recommendations:**
- Use HTTPS in production
- Implement rate limiting
- Add CAPTCHA for signup/login
- Use stronger secret keys
- Consider encryption at rest for documents
- Add audit logging

## 📊 Performance

- **Template Recording**: 3-5 seconds
- **Feature Extraction**: ~0.5 seconds per audio file
- **Authentication**: ~1 second total
- **Supported Audio**: 0.5-10 seconds, 16kHz, mono

## 🐛 Troubleshooting

**Issue**: Verification shows 0.0% scores
- Ensure FFmpeg is installed
- Check audio files are properly converted to WAV
- Verify template was saved correctly

**Issue**: Microphone not working
- Grant browser microphone permissions
- Use HTTPS (required for some browsers)
- Check browser compatibility

**Issue**: Import errors
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check Python version (3.8+)

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Deep learning models for better accuracy
- Real-time streaming authentication
- Multi-language support
- Mobile app integration
- Cloud storage integration

## 📄 License

MIT License - see LICENSE file for details

## 👨‍💻 Author

Your Name -# 🎙️ VoiceGuard - Voice-Authenticated Document Security System

A secure document management system that uses **voice biometrics** and **anti-spoofing detection** to protect sensitive files. Only the authenticated user's live voice can unlock their documents.

## 🔐 Key Features

- **Voice Biometric Authentication**: Uses MFCC (Mel-Frequency Cepstral Coefficients) and pitch analysis for unique voice identification
- **Anti-Spoofing Detection**: Prevents replay attacks by analyzing spectral characteristics, zero-crossing rate, and dynamic range
- **Secure Document Locking**: Upload documents that remain encrypted until voice authentication succeeds
- **Real-time Voice Recording**: Browser-based voice capture with waveform visualization
- **Multi-User Support**: Each user has isolated voice templates and document storage
- **Session Management**: Secure login/logout with Flask sessions

## 🛡️ Security Architecture

### Two-Factor Voice Verification:
1. **Liveness Detection** (Anti-Spoofing)
   - Spectral flux analysis
   - High-frequency energy ratio
   - Zero-crossing rate detection
   - Dynamic range verification
   - Signal-to-noise ratio estimation

2. **Voice Matching** (Biometric Authentication)
   - MFCC feature extraction (52 features)
   - Pitch analysis (fundamental frequency)
   - Cosine similarity comparison
   - Threshold-based authentication (70% match required)

## 🏗️ Tech Stack

- **Backend**: Flask, Python 3.x
- **Database**: SQLAlchemy + SQLite
- **Audio Processing**: 
  - `soundfile` - Audio I/O
  - `scipy` - Signal processing
  - `python_speech_features` - MFCC extraction
  - `numpy` - Numerical operations
- **Frontend**: HTML5, JavaScript, Web Audio API
- **Authentication**: Werkzeug password hashing, Flask sessions

## 📁 Project Structure
```
voiceguard/
├── app.py                  # Main Flask application
├── models.py               # Database models (User, Document)
├── extraction.py           # MFCC & pitch feature extraction
├── testing.py              # Voice authentication & spoof detection
├── record.py               # Audio file handling
├── templates/              # HTML templates
│   ├── index.html          # Login/Signup page
│   ├── record_template.html # One-time voice registration
│   ├── dashboard.html      # Document management
│   ├── unlock.html         # Voice authentication interface
│   └── admin.html          # Admin panel
└── data/                   # User data storage
    └── <user_id>/
        ├── template/       # Voice template audio
        ├── features/       # Extracted MFCC features
        ├── live/           # Live authentication recordings
        └── documents/      # Locked documents
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- FFmpeg (for audio conversion)

### Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [gyan.dev/ffmpeg](https://www.gyan.dev/ffmpeg/builds/)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/voiceguard.git
cd voiceguard
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Access at `http://localhost:5000`

## 📖 Usage

### 1. User Registration
- Create account with username/password
- Record a 3-5 second voice template (one-time setup)
- Template is processed and stored as biometric signature

### 2. Upload Documents
- Upload files (PDF, TXT, DOC, images)
- Documents are automatically locked upon upload
- Maximum file size: 16MB

### 3. Unlock Documents
- Select a locked document
- Record live voice authentication
- System verifies:
  - ✅ Liveness (not a recording)
  - ✅ Voice match (your unique biometrics)
- Document unlocks on successful authentication

### 4. Download & Manage
- Download unlocked documents
- Delete documents anytime
- Track unlock history

## 🎯 Authentication Flow
```
User speaks → Browser records audio → Converts to WAV (16kHz mono)
                                              ↓
                                    Extract 57 features:
                                    - 52 MFCC statistics
                                    - 2 pitch features  
                                    - 3 spectral features
                                              ↓
                        ┌─────────────────────┴─────────────────────┐
                        ↓                                           ↓
              Spoof Detection                            Voice Matching
        (Spectral analysis)                      (Cosine similarity)
                Score > 50%                              Score > 70%
                        ↓                                           ↓
                        └─────────────────────┬─────────────────────┘
                                              ↓
                                    Both checks pass?
                                              ↓
                                      🔓 Document Unlocked
```

## 🔬 Feature Extraction Details

### MFCC Features (52 total):
- 13 coefficients × 4 statistics (mean, std, min, max)
- Captures vocal tract characteristics
- Robust to noise and pitch variations

### Pitch Features (2 total):
- Mean fundamental frequency (80-400 Hz)
- Standard deviation of pitch
- Identifies unique vocal cord vibrations

### Spectral Features (3 total):
- Energy (signal power)
- Zero-crossing rate (frequency estimate)
- Spectral centroid (brightness)

## 🧪 Testing

Test feature extraction:
```bash
python extraction.py path/to/audio.wav
```

Test authentication:
```bash
python testing.py data/1/live/live.wav data/1/features/features.npy
```

## 🔒 Security Considerations

✅ **Implemented:**
- Password hashing (Werkzeug)
- Session-based authentication
- User data isolation
- Anti-replay attack detection
- Voice biometric verification

⚠️ **Production Recommendations:**
- Use HTTPS in production
- Implement rate limiting
- Add CAPTCHA for signup/login
- Use stronger secret keys
- Consider encryption at rest for documents
- Add audit logging

## 📊 Performance

- **Template Recording**: 3-5 seconds
- **Feature Extraction**: ~0.5 seconds per audio file
- **Authentication**: ~1 second total
- **Supported Audio**: 0.5-10 seconds, 16kHz, mono

## 🐛 Troubleshooting

**Issue**: Verification shows 0.0% scores
- Ensure FFmpeg is installed
- Check audio files are properly converted to WAV
- Verify template was saved correctly

**Issue**: Microphone not working
- Grant browser microphone permissions
- Use HTTPS (required for some browsers)
- Check browser compatibility

**Issue**: Import errors
- Verify all dependencies installed: `pip install -r requirements.txt`
- Check Python version (3.8+)

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Deep learning models for better accuracy
- Real-time streaming authentication
- Multi-language support
- Mobile app integration
- Cloud storage integration

## 📄 License

MIT License - see LICENSE file for details

## 👨‍💻 Author

Your Name - [GitHub](https://github.com/aditinagendra05)

## 🙏 Acknowledgments

- MFCC implementation: `python_speech_features`
- Audio processing: `scipy` signal processing
- Web framework: Flask
```

## Alternative Short Descriptions:

**Academic/Technical:**
```
Voice biometric authentication system implementing MFCC feature extraction, 
cosine similarity matching, and multi-factor anti-spoofing detection for 
secure document access control.
```

**Casual/Engaging:**
```
🔐 Your voice is your password! Lock documents with voice biometrics and 
unlock them only with live speech. Includes anti-spoofing to prevent replay 
attacks. Built with Python, Flask, and audio ML.
```

**Professional:**
```
Enterprise-grade voice authentication platform for document security. 
Features real-time biometric verification, replay attack prevention, 
and MFCC-based speaker recognition with 70%+ accuracy threshold.

## 🙏 Acknowledgments

- MFCC implementation: `python_speech_features`
- Audio processing: `scipy` signal processing
- Web framework: Flask
```

## Alternative Short Descriptions:

**Academic/Technical:**
```
Voice biometric authentication system implementing MFCC feature extraction, 
cosine similarity matching, and multi-factor anti-spoofing detection for 
secure document access control.
```

**Casual/Engaging:**
```
🔐 Your voice is your password! Lock documents with voice biometrics and 
unlock them only with live speech. Includes anti-spoofing to prevent replay 
attacks. Built with Python, Flask, and audio ML.
```

**Professional:**
```
Enterprise-grade voice authentication platform for document security. 
Features real-time biometric verification, replay attack prevention, 
and MFCC-based speaker recognition with 70%+ accuracy threshold.

## 🙏 Acknowledgments

- MFCC implementation: `python_speech_features`
- Audio processing: `scipy` signal processing
- Web framework: Flask
```

## Alternative Short Descriptions:

**Academic/Technical:**
```
Voice biometric authentication system implementing MFCC feature extraction, 
cosine similarity matching, and multi-factor anti-spoofing detection for 
secure document access control.
```

**Casual/Engaging:**
```
🔐 Your voice is your password! Lock documents with voice biometrics and 
unlock them only with live speech. Includes anti-spoofing to prevent replay 
attacks. Built with Python, Flask, and audio ML.
```

**Professional:**
```
Enterprise-grade voice authentication platform for document security. 
Features real-time biometric verification, replay attack prevention, 
and MFCC-based speaker recognition with 70%+ accuracy threshold.


