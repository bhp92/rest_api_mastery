"""routes/files.py — File upload/download"""
from flask import Blueprint, request, send_from_directory, current_app
from utils.auth import require_auth
from utils.responses import success, error
import os, uuid

files_bp = Blueprint('files', __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'txt', 'csv', 'json'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@files_bp.route('/upload', methods=['POST'])
@require_auth
def upload():
    if 'file' not in request.files:
        return error("No file part in request. Use multipart/form-data with key 'file'")
    f = request.files['file']
    if f.filename == '':
        return error("No file selected")
    if not allowed_file(f.filename):
        return error(f"File type not allowed. Allowed: {ALLOWED_EXTENSIONS}")

    ext = f.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_name)
    f.save(save_path)
    size = os.path.getsize(save_path)
    return success({
        'filename': unique_name,
        'original_name': f.filename,
        'size_bytes': size,
        'url': f"/api/v1/files/{unique_name}"
    }, "File uploaded", 201)


@files_bp.route('/<filename>', methods=['GET'])
def download(filename):
    folder = current_app.config['UPLOAD_FOLDER']
    path = os.path.join(folder, filename)
    if not os.path.exists(path):
        return error("File not found", 404)
    return send_from_directory(folder, filename)


@files_bp.route('', methods=['GET'])
@require_auth
def list_files():
    folder = current_app.config['UPLOAD_FOLDER']
    files = []
    for fname in os.listdir(folder):
        fpath = os.path.join(folder, fname)
        files.append({'filename': fname, 'size_bytes': os.path.getsize(fpath), 'url': f"/api/v1/files/{fname}"})
    return success(files)
