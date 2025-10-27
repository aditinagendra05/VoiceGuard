"""
Audio Recording Module
Handles saving audio data from web browser
"""

import os
import soundfile as sf
import numpy as np

def save_audio(audio_data, output_path, sample_rate=16000):
    """
    Save audio data to WAV file
    
    Args:
        audio_data: Audio data (bytes, numpy array, or file-like object)
        output_path: Path where to save the WAV file
        sample_rate: Sample rate in Hz (default: 16000)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # If audio_data is bytes or file-like, save directly
        if isinstance(audio_data, bytes):
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            print(f"✅ Audio saved to: {output_path}")
            return True
        
        # If it's a numpy array, use soundfile
        elif isinstance(audio_data, np.ndarray):
            sf.write(output_path, audio_data, sample_rate)
            print(f"✅ Audio saved to: {output_path}")
            return True
        
        # If it has a read method (file-like object), copy it
        elif hasattr(audio_data, 'read'):
            with open(output_path, 'wb') as f:
                f.write(audio_data.read())
            print(f"✅ Audio saved to: {output_path}")
            return True
        
        else:
            print(f"❌ Unsupported audio data type: {type(audio_data)}")
            return False
            
    except Exception as e:
        print(f"❌ Error saving audio: {e}")
        return False

def validate_audio(audio_path, min_duration=1.0, max_duration=15.0):
    """
    Validate audio file
    
    Args:
        audio_path: Path to audio file
        min_duration: Minimum duration in seconds
        max_duration: Maximum duration in seconds
    
    Returns:
        dict: {
            'valid': bool,
            'duration': float,
            'sample_rate': int,
            'reason': str (if invalid)
        }
    """
    try:
        # Read audio file
        audio, sample_rate = sf.read(audio_path)
        
        # Calculate duration
        if len(audio.shape) > 1:
            duration = len(audio) / sample_rate
        else:
            duration = len(audio) / sample_rate
        
        # Check duration
        if duration < min_duration:
            return {
                'valid': False,
                'duration': duration,
                'sample_rate': sample_rate,
                'reason': f'Audio too short ({duration:.1f}s < {min_duration}s)'
            }
        
        if duration > max_duration:
            return {
                'valid': False,
                'duration': duration,
                'sample_rate': sample_rate,
                'reason': f'Audio too long ({duration:.1f}s > {max_duration}s)'
            }
        
        # Check if audio is silent
        if len(audio.shape) > 1:
            audio_mono = np.mean(audio, axis=1)
        else:
            audio_mono = audio
        
        energy = np.sum(audio_mono ** 2) / len(audio_mono)
        if energy < 1e-6:
            return {
                'valid': False,
                'duration': duration,
                'sample_rate': sample_rate,
                'reason': 'Audio is too quiet or silent'
            }
        
        return {
            'valid': True,
            'duration': duration,
            'sample_rate': sample_rate,
            'reason': None
        }
        
    except Exception as e:
        return {
            'valid': False,
            'duration': 0,
            'sample_rate': 0,
            'reason': f'Error reading audio: {str(e)}'
        }

def get_audio_info(audio_path):
    """
    Get information about an audio file
    
    Args:
        audio_path: Path to audio file
    
    Returns:
        dict: Audio information
    """
    try:
        info = sf.info(audio_path)
        return {
            'duration': info.duration,
            'sample_rate': info.samplerate,
            'channels': info.channels,
            'format': info.format,
            'subtype': info.subtype
        }
    except Exception as e:
        return {
            'error': str(e)
        }

if __name__ == "__main__":
    # Test recording functionality
    import sys
    
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
        
        # Validate audio
        validation = validate_audio(audio_file)
        print(f"\nValidation: {validation}")
        
        # Get info
        info = get_audio_info(audio_file)
        print(f"\nAudio Info: {info}")
    else:
        print("Usage: python record.py <audio_file.wav>")