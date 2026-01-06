import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

class FileStorageService:
    """Service for handling file uploads and storage"""

    @staticmethod
    def save_uploaded_file(file, user_id):
        """
        Save uploaded file with organized structure
        Returns: (relative_path, file_size, original_filename)
        """
        # Get file extension
        original_filename = secure_filename(file.filename)
        file_ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}.{file_ext}"

        # Create directory structure: uploads/{user_id}/{year}/{month}
        now = datetime.now()
        relative_path = os.path.join(
            str(user_id),
            str(now.year),
            str(now.month).zfill(2)
        )

        # Full path
        upload_folder = current_app.config['UPLOAD_FOLDER']
        full_dir_path = os.path.join(upload_folder, relative_path)
        os.makedirs(full_dir_path, exist_ok=True)

        # Save file
        file_path = os.path.join(full_dir_path, unique_filename)
        file.save(file_path)

        # Get file size
        file_size = os.path.getsize(file_path)

        # Return relative path from uploads folder
        relative_file_path = os.path.join(relative_path, unique_filename)

        return relative_file_path, file_size, original_filename

    @staticmethod
    def get_full_path(relative_path):
        """Get full filesystem path from relative path"""
        upload_folder = current_app.config['UPLOAD_FOLDER']
        return os.path.join(upload_folder, relative_path)

    @staticmethod
    def delete_file(relative_path):
        """Delete file from storage"""
        try:
            full_path = FileStorageService.get_full_path(relative_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
        except Exception as e:
            current_app.logger.error(f"Error deleting file {relative_path}: {str(e)}")
        return False

    @staticmethod
    def is_allowed_file(filename):
        """Check if file extension is allowed"""
        allowed_extensions = current_app.config['ALLOWED_EXTENSIONS']
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @staticmethod
    def get_file_type(filename):
        """Extract file type from filename"""
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return None
