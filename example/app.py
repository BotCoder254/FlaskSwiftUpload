"""Professional FlaskSwiftUpload Demo Application."""

from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
from datetime import datetime
from pathlib import Path
from flask_swift_upload import (
    FileUploader,
    StorageManager,
    StorageConfig,
    ContentValidator
)
import os
import time

app = Flask(__name__)

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/flask_swift_upload"

# Initialize MongoDB with retry mechanism
def init_mongo():
    retries = 3
    while retries > 0:
        try:
            mongo = PyMongo(app)
            # Test the connection
            mongo.db.command('ping')
            return mongo
        except Exception as e:
            print(f"MongoDB Connection Error: {str(e)}")
            print(f"Retrying in 2 seconds... ({retries} attempts left)")
            retries -= 1
            time.sleep(2)
    raise Exception("Failed to connect to MongoDB after multiple attempts")

try:
    mongo = init_mongo()
except Exception as e:
    print(f"Fatal Error: {str(e)}")
    print("Please ensure MongoDB is running with: sudo systemctl start mongod")
    exit(1)

# FlaskSwiftUpload Configuration
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Configure storage options
storage_config = {
    'create_date_subfolders': True,
    'max_folder_size': 1024 * 1024 * 1024,  # 1GB
    'backup_old_files': True,
    'backup_folder': str(UPLOAD_DIR / "backup"),
    'path_template': '{year}/{month}/{day}'
}

# Initialize the uploader with storage configuration
uploader = FileUploader(
    upload_folder=str(UPLOAD_DIR),
    allowed_mime_types=['image/jpeg', 'image/png', 'image/gif', 'video/mp4', 'video/quicktime'],
    max_content_length=50 * 1024 * 1024,  # 50MB
    use_timestamp=True,
    hash_filenames=True,
    storage_config=storage_config
)

def get_upload_stats():
    """Get upload statistics."""
    total_uploads = mongo.db.uploads.count_documents({})
    total_size = sum(doc.get('size', 0) for doc in mongo.db.uploads.find({}, {'size': 1}))
    latest_uploads = list(mongo.db.uploads.find().sort('uploaded_at', -1).limit(5))
    
    # Convert ObjectId to string for JSON serialization
    for upload in latest_uploads:
        upload['_id'] = str(upload['_id'])
        upload['uploaded_at'] = upload['uploaded_at'].isoformat()
    
    return {
        'total_uploads': total_uploads,
        'total_size': total_size,
        'latest_uploads': latest_uploads,
        'storage_usage': uploader.get_storage_stats()
    }

@app.route('/')
def index():
    """Render the main page."""
    try:
        stats = get_upload_stats()
    except Exception as e:
        stats = {
            'total_uploads': 0,
            'total_size': 0,
            'latest_uploads': [],
            'storage_usage': {'total_size': 0, 'file_count': 0}
        }
    return render_template('index.html', stats=stats)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    if 'files' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No selected file'}), 400

    results = []
    for file in files:
        if file.filename:
            try:
                success, message, filename, details = uploader.save_file(file)
                if success:
                    # Store metadata in MongoDB
                    mongo.db.uploads.insert_one({
                        'filename': filename,
                        'original_filename': file.filename,
                        'mime_type': details.get('mime_type'),
                        'size': details.get('size'),
                        'uploaded_at': datetime.utcnow()
                    })
                    results.append({
                        'filename': filename,
                        'status': 'success'
                    })
                else:
                    results.append({
                        'filename': file.filename,
                        'status': 'error',
                        'message': message
                    })
            except Exception as e:
                results.append({
                    'filename': file.filename,
                    'status': 'error',
                    'message': str(e)
                })

    return jsonify({
        'status': 'success',
        'results': results
    })

@app.route('/files')
def list_files():
    """List uploaded files."""
    page = int(request.args.get('page', 1))
    per_page = 10
    skip = (page - 1) * per_page

    files = list(mongo.db.uploads.find()
                .sort('uploaded_at', -1)
                .skip(skip)
                .limit(per_page))
    
    # Convert ObjectId to string for JSON serialization
    for file in files:
        file['_id'] = str(file['_id'])
        file['uploaded_at'] = file['uploaded_at'].isoformat()

    return jsonify({
        'files': files,
        'page': page,
        'per_page': per_page
    })

if __name__ == '__main__':
    app.run(debug=True)
