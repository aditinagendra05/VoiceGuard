"""
Voice Feature Extraction
Extracts MFCC and pitch features from audio files
"""

import numpy as np
import soundfile as sf
from python_speech_features import mfcc
from scipy.signal import correlate
from scipy.fft import rfft, rfftfreq
import warnings
warnings.filterwarnings('ignore')

def extract_pitch(audio, sample_rate):
    """
    Extract pitch (fundamental frequency) using autocorrelation
    """
    try:
        # Normalize audio
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
        else:
            return 0
        
        # Apply autocorrelation
        correlation = correlate(audio, audio, mode='full')
        correlation = correlation[len(correlation)//2:]
        
        # Find peaks in autocorrelation
        # Look for pitch in human voice range: 80-400 Hz
        min_lag = int(sample_rate / 400)  # Max pitch
        max_lag = int(sample_rate / 80)   # Min pitch
        
        if max_lag < len(correlation) and min_lag < max_lag:
            peak_lag = np.argmax(correlation[min_lag:max_lag]) + min_lag
            pitch = sample_rate / peak_lag if peak_lag > 0 else 0
        else:
            pitch = 0
        
        return pitch
    except Exception as e:
        print(f"⚠️ Pitch extraction warning: {e}")
        return 0

def extract_features(audio_path):
    """
    Extract voice features from audio file
    
    Args:
        audio_path: Path to WAV file
    
    Returns:
        numpy array of features
    """
    try:
        print(f"\n🔍 Extracting features from: {audio_path}")
        
        # Load audio file
        audio, sample_rate = sf.read(audio_path)
        print(f"  ✅ Loaded audio: {len(audio)} samples at {sample_rate}Hz")
        
        # Convert stereo to mono if needed
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)
            print(f"  ✅ Converted to mono")
        
        # Check if audio is valid
        if len(audio) == 0:
            raise ValueError("Audio file is empty")
        
        if np.all(audio == 0):
            raise ValueError("Audio contains only silence")
        
        # Normalize audio
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
        
        # Resample to 16kHz if needed
        if sample_rate != 16000:
            print(f"  ⚠️ Resampling from {sample_rate}Hz to 16000Hz")
            from scipy.signal import resample
            duration = len(audio) / sample_rate
            num_samples = int(duration * 16000)
            audio = resample(audio, num_samples)
            sample_rate = 16000
        
        # Check minimum duration (at least 0.5 seconds)
        min_samples = int(0.5 * sample_rate)
        if len(audio) < min_samples:
            raise ValueError(f"Audio too short: {len(audio)/sample_rate:.2f}s (need at least 0.5s)")
        
        print(f"  ✅ Audio duration: {len(audio)/sample_rate:.2f}s")
        
        # Extract MFCC features (13 coefficients)
        try:
            mfcc_features = mfcc(
                audio,
                samplerate=sample_rate,
                numcep=13,
                nfilt=26,
                nfft=512,
                lowfreq=0,
                highfreq=None,
                preemph=0.97,
                ceplifter=22,
                appendEnergy=True,
                winfunc=np.hamming
            )
            
            print(f"  ✅ Extracted MFCC: {mfcc_features.shape}")
            
            if mfcc_features.shape[0] == 0:
                raise ValueError("No MFCC frames extracted")
            
        except Exception as e:
            print(f"  ❌ MFCC extraction failed: {e}")
            raise
        
        # Calculate statistics for MFCCs
        mfcc_mean = np.mean(mfcc_features, axis=0)
        mfcc_std = np.std(mfcc_features, axis=0)
        mfcc_min = np.min(mfcc_features, axis=0)
        mfcc_max = np.max(mfcc_features, axis=0)
        
        # Extract pitch features
        frame_length = int(0.025 * sample_rate)  # 25ms frames
        hop_length = int(0.010 * sample_rate)    # 10ms hop
        
        pitches = []
        for i in range(0, len(audio) - frame_length, hop_length):
            frame = audio[i:i + frame_length]
            pitch = extract_pitch(frame, sample_rate)
            if pitch > 0:  # Only keep valid pitches
                pitches.append(pitch)
        
        if len(pitches) > 0:
            pitch_mean = np.mean(pitches)
            pitch_std = np.std(pitches)
            print(f"  ✅ Pitch: mean={pitch_mean:.1f}Hz, std={pitch_std:.1f}Hz")
        else:
            pitch_mean = 150.0  # Default human voice pitch
            pitch_std = 20.0
            print(f"  ⚠️ No pitch detected, using defaults")
        
        # Additional spectral features
        # Energy
        energy = np.sum(audio ** 2) / len(audio)
        
        # Zero crossing rate
        zero_crossings = np.sum(np.abs(np.diff(np.sign(audio)))) / (2 * len(audio))
        
        # Spectral centroid (using FFT)
        fft = np.abs(rfft(audio))
        freqs = rfftfreq(len(audio), 1/sample_rate)
        spectral_centroid = np.sum(freqs * fft) / np.sum(fft) if np.sum(fft) > 0 else 0
        
        print(f"  ✅ Energy={energy:.6f}, ZCR={zero_crossings:.4f}, SC={spectral_centroid:.1f}Hz")
        
        # Combine all features
        features = np.concatenate([
            mfcc_mean,      # 13 features
            mfcc_std,       # 13 features
            mfcc_min,       # 13 features
            mfcc_max,       # 13 features
            [pitch_mean, pitch_std],  # 2 features
            [energy, zero_crossings, spectral_centroid]  # 3 features
        ])
        
        # Check for NaN or Inf
        if np.any(np.isnan(features)) or np.any(np.isinf(features)):
            print(f"  ⚠️ Warning: Invalid values in features, replacing with zeros")
            features = np.nan_to_num(features, nan=0.0, posinf=0.0, neginf=0.0)
        
        print(f"✅ Successfully extracted {len(features)} features")
        print(f"   Feature range: [{np.min(features):.3f}, {np.max(features):.3f}]")
        print(f"   Feature mean: {np.mean(features):.3f}, std: {np.std(features):.3f}")
        
        return features
        
    except Exception as e:
        print(f"❌ Error extracting features from {audio_path}: {e}")
        import traceback
        traceback.print_exc()
        # Return zero features if extraction fails
        return np.zeros(57)  # 13*4 + 2 + 3 = 57 features

def compare_features(features1, features2):
    """
    Compare two feature vectors using cosine similarity
    
    Args:
        features1: First feature vector
        features2: Second feature vector
    
    Returns:
        Similarity score (0-1, higher is more similar)
    """
    try:
        # Check if features are valid
        if len(features1) == 0 or len(features2) == 0:
            print("⚠️ Empty feature vectors")
            return 0.0
        
        if np.all(features1 == 0) or np.all(features2 == 0):
            print("⚠️ Zero feature vectors")
            return 0.0
        
        # Normalize features
        norm1 = np.linalg.norm(features1)
        norm2 = np.linalg.norm(features2)
        
        if norm1 == 0 or norm2 == 0:
            print("⚠️ Zero norm features")
            return 0.0
        
        # Cosine similarity
        similarity = np.dot(features1, features2) / (norm1 * norm2)
        
        # Convert to 0-1 range
        similarity = (similarity + 1) / 2
        
        # Clip to valid range
        similarity = np.clip(similarity, 0.0, 1.0)
        
        print(f"  Cosine similarity: {similarity:.3f}")
        
        return float(similarity)
        
    except Exception as e:
        print(f"❌ Error comparing features: {e}")
        return 0.0

if __name__ == "__main__":
    # Test the feature extraction
    import sys
    
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        features = extract_features(audio_file)
        print(f"\nFeature vector shape: {features.shape}")
        print(f"Feature vector (first 10): {features[:10]}")
        print(f"Non-zero features: {np.count_nonzero(features)}/{len(features)}")
    else:
        print("Usage: python extraction.py <audio_file.wav>")