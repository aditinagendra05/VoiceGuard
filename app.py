from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from models import db, User, Document
from record import save_audio
from extraction import extract_features
from testing import authenticate_voice
import numpy as np

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'data'

db.init_app(app)

# Ensure data directory exists
os.makedirs('data', exist_ok=True)
os.makedirs('instance', exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_path(user_id, subdir=''):
    """Get path for user's data directory"""
    path = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id), subdir)
    os.makedirs(path, exist_ok=True)
    return path

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create user directories
        get_user_path(new_user.id, 'template')
        get_user_path(new_user.id, 'features')
        get_user_path(new_user.id, 'live')
        get_user_path(new_user.id, 'documents')
        
        return jsonify({'success': True, 'message': 'Account created successfully'})
    
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            
            # Check if user has voice template
            template_path = os.path.join(get_user_path(user.id, 'template'), 'template.wav')
            
            if not os.path.exists(template_path):
                return jsonify({'success': True, 'redirect': url_for('record_template')})
            else:
                return jsonify({'success': True, 'redirect': url_for('dashboard')})
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/record-template')
def record_template():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if template already exists
    template_path = os.path.join(get_user_path(session['user_id'], 'template'), 'template.wav')
    if os.path.exists(template_path):
        return redirect(url_for('dashboard'))
    
    return render_template('record_template.html')

@app.route('/save-template', methods=['POST'])
def save_template():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    audio_data = request.files.get('audio')
    if not audio_data:
        return jsonify({'error': 'No audio data received'}), 400
    
    user_id = session['user_id']
    
    # Save uploaded file temporarily with original extension
    temp_input = os.path.join(get_user_path(user_id, 'template'), 'temp_upload.webm')
    audio_data.save(temp_input)
    
    template_path = os.path.join(get_user_path(user_id, 'template'), 'template.wav')
    
    try:
        # Use FFmpeg to convert to WAV (most reliable method)
        import subprocess
        
        # Check if ffmpeg is available
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # FFmpeg not available, try direct save
            raise Exception("FFmpeg not found")
        
        # Convert using FFmpeg
        cmd = [
            'ffmpeg',
            '-i', temp_input,
            '-acodec', 'pcm_s16le',  # 16-bit PCM
            '-ar', '16000',           # 16kHz sample rate
            '-ac', '1',               # Mono
            '-y',                     # Overwrite output
            template_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg error: {result.stderr}")
        
        print(f"✅ Converted audio using FFmpeg")
        
    except Exception as e:
        print(f"⚠️ FFmpeg failed: {e}, trying alternative method...")
        
        # Fallback: Try using soundfile directly (works for some formats)
        try:
            import soundfile as sf
            data, samplerate = sf.read(temp_input)
            
            # Convert to mono if stereo
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            
            # Simple resampling if needed
            if samplerate != 16000:
                from scipy.signal import resample
                num_samples = int(len(data) * 16000 / samplerate)
                data = resample(data, num_samples)
                samplerate = 16000
            
            # Save as WAV
            sf.write(template_path, data, samplerate, subtype='PCM_16')
            print(f"✅ Converted audio using soundfile")
            
        except Exception as e2:
            # Last resort: save as-is and hope it works
            print(f"⚠️ Direct conversion failed: {e2}")
            
            # Just copy the file and rename to .wav
            import shutil
            shutil.copy(temp_input, template_path)
            print(f"⚠️ Saved audio as-is (may need manual conversion)")
    
    # Clean up temp file
    if os.path.exists(temp_input):
        os.remove(temp_input)
    
    # Verify the file exists and has content
    if not os.path.exists(template_path) or os.path.getsize(template_path) < 1000:
        return jsonify({'error': 'Failed to save audio file'}), 400
    
    # Extract and save features
    try:
        features = extract_features(template_path)
        features_path = os.path.join(get_user_path(user_id, 'features'), 'features.npy')
        np.save(features_path, features)
        print(f"✅ Extracted and saved features")
    except Exception as e:
        print(f"❌ Feature extraction error: {e}")
        return jsonify({'error': f'Failed to extract features: {str(e)}'}), 400
    
    # Update user record
    user = User.query.get(user_id)
    user.has_template = True
    db.session.commit()
    
    print(f"✅ Template saved successfully for user {user_id}")
    return jsonify({'success': True, 'message': 'Voice template saved successfully'})


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    documents = Document.query.filter_by(user_id=session['user_id']).all()
    
    return render_template('dashboard.html', user=user, documents=documents)

@app.route('/upload-document', methods=['POST'])
def upload_document():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    filename = secure_filename(file.filename)
    user_id = session['user_id']
    
    # Save file with locked_ prefix
    locked_filename = f"locked_{filename}"
    filepath = os.path.join(get_user_path(user_id, 'documents'), locked_filename)
    file.save(filepath)
    
    # Create database record
    document = Document(
        filename=filename,
        locked_filename=locked_filename,
        user_id=user_id,
        is_locked=True
    )
    db.session.add(document)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Document uploaded and locked successfully'})

@app.route('/unlock/<int:doc_id>')
def unlock_page(doc_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    document = Document.query.filter_by(id=doc_id, user_id=session['user_id']).first()
    
    if not document:
        return "Document not found", 404
    
    return render_template('unlock.html', document=document)

@app.route('/verify-voice/<int:doc_id>', methods=['POST'])
def verify_voice(doc_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    audio_data = request.files.get('audio')
    if not audio_data:
        return jsonify({'error': 'No audio data received'}), 400
    
    user_id = session['user_id']
    document = Document.query.filter_by(id=doc_id, user_id=user_id).first()
    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Save live audio with conversion
    temp_live = os.path.join(get_user_path(user_id, 'live'), 'temp_live.webm')
    live_path = os.path.join(get_user_path(user_id, 'live'), 'live.wav')
    
    audio_data.save(temp_live)
    
    # Convert to WAV (same as template recording)
    try:
        import subprocess
        cmd = [
            'ffmpeg',
            '-i', temp_live,
            '-acodec', 'pcm_s16le',
            '-ar', '16000',
            '-ac', '1',
            '-y',
            live_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            # Fallback to soundfile
            import soundfile as sf
            data, sr = sf.read(temp_live)
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            if sr != 16000:
                from scipy.signal import resample
                data = resample(data, int(len(data) * 16000 / sr))
            sf.write(live_path, data, 16000, subtype='PCM_16')
    except Exception as e:
        print(f"❌ Audio conversion error: {e}")
        import shutil
        shutil.copy(temp_live, live_path)
    
    finally:
        if os.path.exists(temp_live):
            os.remove(temp_live)
    
    # Get template features path
    features_path = os.path.join(get_user_path(user_id, 'features'), 'features.npy')
    
    print(f"\n🔐 Authenticating user {user_id} for document {doc_id}")
    print(f"  Live audio: {live_path} (exists: {os.path.exists(live_path)})")
    print(f"  Template: {features_path} (exists: {os.path.exists(features_path)})")
    
    # Authenticate voice
    result = authenticate_voice(live_path, features_path)
    
    if result['authenticated']:
        # Unlock document
        document.is_locked = False
        document.unlocked_at = datetime.utcnow()
        document.unlock_count += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Voice authenticated successfully',
            'spoof_score': result['spoof_score'],
            'match_score': result['match_score']
        })
    else:
        return jsonify({
            'success': False,
            'message': result['reason'],
            'spoof_score': result.get('spoof_score', 0.0),
            'match_score': result.get('match_score', 0.0)
        }), 403
'''

**To test if it's working now:**

1. Check your Flask console output - you should see detailed logs like:
```
   🔍 Extracting features from: data/1/template/template.wav
     ✅ Loaded audio: 48000 samples at 16000Hz
     ✅ Extracted MFCC: (189, 13)'''

@app.route('/download/<int:doc_id>')
def download_document(doc_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    document = Document.query.filter_by(id=doc_id, user_id=session['user_id']).first()
    
    if not document:
        return "Document not found", 404
    
    if document.is_locked:
        return "Document is locked. Please authenticate with your voice first.", 403
    
    filepath = os.path.join(get_user_path(session['user_id'], 'documents'), document.locked_filename)
    
    return send_file(filepath, as_attachment=True, download_name=document.filename)

@app.route('/delete/<int:doc_id>', methods=['POST'])
def delete_document(doc_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    document = Document.query.filter_by(id=doc_id, user_id=session['user_id']).first()
    
    if not document:
        return jsonify({'error': 'Document not found'}), 404
    
    # Delete file
    filepath = os.path.join(get_user_path(session['user_id'], 'documents'), document.locked_filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    
    # Delete database record
    db.session.delete(document)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Document deleted successfully'})

@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Simple admin check (you can enhance this)
    if session.get('username') != 'admin':
        return "Access denied", 403
    
    users = User.query.all()
    all_documents = Document.query.all()
    
    return render_template('admin.html', users=users, documents=all_documents)

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)