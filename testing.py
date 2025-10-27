"""
Voice Authentication and Spoof Detection
Authenticates users based on voice features and detects replay attacks
"""

import numpy as np
import soundfile as sf
from scipy.signal import stft
from extraction import extract_features, compare_features
import os
# Authentication thresholds
SPOOF_THRESHOLD = 0.5   # Confidence that audio is live (0-1)
MATCH_THRESHOLD = 0.7   # Similarity threshold for voice matching (0-1)

def detect_spoof(audio_path):
    """
    Detect if audio is a replay/spoof attack
    
    Checks for:
    - Spectral characteristics typical of recordings
    - Audio quality artifacts
    - Frequency distribution anomalies
    
    Args:
        audio_path: Path to audio file to check
    
    Returns:
        dict: {
            'is_live': bool,
            'confidence': float (0-1)
        }
    """
    try:
        # Load audio
        audio, sample_rate = sf.read(audio_path)
        
        # Convert stereo to mono if needed
        if len(audio.shape) > 1:
            audio = np.mean(audio, axis=1)
        
        # Normalize
        audio = audio / np.max(np.abs(audio)) if np.max(np.abs(audio)) > 0 else audio
        
        # Feature 1: Zero crossing rate (recordings tend to have lower ZCR)
        zero_crossings = np.sum(np.abs(np.diff(np.sign(audio)))) / (2 * len(audio))
        zcr_score = min(zero_crossings * 100, 1.0)  # Higher is better
        
        # Feature 2: High frequency energy ratio
        # Live recordings have more high-frequency content
        f, t, Zxx = stft(audio, fs=sample_rate, nperseg=256)
        power_spectrum = np.abs(Zxx) ** 2
        
        # Split spectrum into low and high frequency bands
        freq_split = len(f) // 2
        low_freq_energy = np.sum(power_spectrum[:freq_split, :])
        high_freq_energy = np.sum(power_spectrum[freq_split:, :])
        
        if low_freq_energy + high_freq_energy > 0:
            hf_ratio = high_freq_energy / (low_freq_energy + high_freq_energy)
        else:
            hf_ratio = 0
        
        hf_score = min(hf_ratio * 3, 1.0)  # Higher is better
        
        # Feature 3: Spectral flux (variation in spectrum over time)
        # Live audio has more variation
        spectral_flux = []
        for i in range(1, Zxx.shape[1]):
            flux = np.sum((np.abs(Zxx[:, i]) - np.abs(Zxx[:, i-1])) ** 2)
            spectral_flux.append(flux)
        
        if len(spectral_flux) > 0:
            avg_flux = np.mean(spectral_flux)
            flux_score = min(avg_flux * 0.01, 1.0)  # Normalize
        else:
            flux_score = 0.5
        
        # Feature 4: Dynamic range
        # Recordings often have compressed dynamic range
        dynamic_range = np.max(audio) - np.min(audio)
        dr_score = min(dynamic_range * 2, 1.0)
        
        # Feature 5: Signal-to-noise ratio estimate
        # Calculate using high-frequency content
        signal_power = np.mean(audio ** 2)
        if signal_power > 0:
            snr_estimate = 10 * np.log10(signal_power / (1e-10 + np.std(audio[-100:])**2))
            snr_score = min(max(snr_estimate / 40, 0), 1.0)
        else:
            snr_score = 0.5
        
        # Combine scores with weights
        weights = {
            'zcr': 0.15,
            'hf': 0.25,
            'flux': 0.30,
            'dr': 0.15,
            'snr': 0.15
        }
        
        confidence = (
            weights['zcr'] * zcr_score +
            weights['hf'] * hf_score +
            weights['flux'] * flux_score +
            weights['dr'] * dr_score +
            weights['snr'] * snr_score
        )
        
        is_live = confidence >= SPOOF_THRESHOLD
        
        print(f"🔍 Spoof Detection Scores:")
        print(f"  - Zero Crossing Rate: {zcr_score:.3f}")
        print(f"  - High Freq Ratio: {hf_score:.3f}")
        print(f"  - Spectral Flux: {flux_score:.3f}")
        print(f"  - Dynamic Range: {dr_score:.3f}")
        print(f"  - SNR Estimate: {snr_score:.3f}")
        print(f"  → Overall Confidence: {confidence:.3f} ({'LIVE' if is_live else 'SPOOF'})")
        
        return {
            'is_live': is_live,
            'confidence': float(confidence)
        }
        
    except Exception as e:
        print(f"❌ Error in spoof detection: {e}")
        return {
            'is_live': False,
            'confidence': 0.0
        }

def match_voice(live_audio_path, template_features_path):
    """
    Match live audio against stored template features
    
    Args:
        live_audio_path: Path to live recording
        template_features_path: Path to stored template features (.npy)
    
    Returns:
        dict: {
            'match': bool,
            'similarity': float (0-1)
        }
    """
    try:
        # Extract features from live audio
        live_features = extract_features(live_audio_path)
        
        # Load template features
        template_features = np.load(template_features_path)
        
        # Compare features
        similarity = compare_features(live_features, template_features)
        
        match = similarity >= MATCH_THRESHOLD
        
        print(f"🎯 Voice Match:")
        print(f"  - Similarity: {similarity:.3f}")
        print(f"  - Threshold: {MATCH_THRESHOLD}")
        print(f"  → Result: {'MATCH' if match else 'NO MATCH'}")
        
        return {
            'match': match,
            'similarity': float(similarity)
        }
        
    except Exception as e:
        print(f"❌ Error in voice matching: {e}")
        return {
            'match': False,
            'similarity': 0.0
        }

def authenticate_voice(live_audio_path, template_features_path):
    """
    Complete voice authentication pipeline
    
    Args:
        live_audio_path: Path to live recording
        template_features_path: Path to stored template features
    
    Returns:
        dict: {
            'authenticated': bool,
            'spoof_score': float,
            'match_score': float,
            'reason': str (if failed)
        }
    """
    print("\n" + "="*60)
    print("🎙️  VOICE AUTHENTICATION")
    print("="*60)
    
    # Step 1: Spoof detection
    print("\n[1/2] Checking for replay attacks...")
    spoof_result = detect_spoof(live_audio_path)
    
    if not spoof_result['is_live']:
        print("\n❌ AUTHENTICATION FAILED: Possible spoof detected")
        return {
            'authenticated': False,
            'spoof_score': spoof_result['confidence'],
            'match_score': 0.0,
            'reason': 'Possible spoof detected - please speak live, not a recording'
        }
    
    # Step 2: Voice matching
    print("\n[2/2] Matching voice against template...")
    match_result = match_voice(live_audio_path, template_features_path)
    
    if not match_result['match']:
        print("\n❌ AUTHENTICATION FAILED: Voice does not match")
        return {
            'authenticated': False,
            'spoof_score': spoof_result['confidence'],
            'match_score': match_result['similarity'],
            'reason': 'Voice does not match template'
        }
    
    # Both checks passed
    print("\n✅ AUTHENTICATION SUCCESSFUL")
    print("="*60)
    return {
        'authenticated': True,
        'spoof_score': spoof_result['confidence'],
        'match_score': match_result['similarity'],
        'reason': None
    }

if __name__ == "__main__":
    # Test the authentication
    import sys
    
    if len(sys.argv) >= 3:
        live_audio = sys.argv[1]
        template_features = sys.argv[2]
        
        result = authenticate_voice(live_audio, template_features)
        print(f"\nFinal Result: {result}")
    else:
        print("Usage: python testing.py <live_audio.wav> <template_features.npy>")
        print("\nExample:")
        print("  python testing.py data/1/live/live.wav data/1/features/features.npy")