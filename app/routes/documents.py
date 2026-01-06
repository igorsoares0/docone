from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.document import Document
from app.services.file_storage import FileStorageService
from app.services.document_converter import DocumentConverter
import os

bp = Blueprint('documents', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with document list"""
    # Get all documents for current user (excluding deleted)
    documents = Document.query.filter_by(
        user_id=current_user.id,
        is_deleted=False
    ).order_by(Document.created_at.desc()).all()

    return render_template('dashboard/index.html', documents=documents)

@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    """Upload new document"""
    if request.method == 'POST':
        # Check if file is present
        if 'file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)

        # Validate file type
        if not FileStorageService.is_allowed_file(file.filename):
            allowed = ', '.join(current_app.config['ALLOWED_EXTENSIONS'])
            flash(f'Invalid file type. Allowed types: {allowed}', 'danger')
            return redirect(request.url)

        try:
            # Save file
            relative_path, file_size, original_filename = FileStorageService.save_uploaded_file(
                file, current_user.id
            )

            # Get file type
            file_type = FileStorageService.get_file_type(original_filename)

            # Determine PDF path
            pdf_path = DocumentConverter.get_pdf_path_for_document(relative_path, file_type)

            # Convert to PDF if needed
            if file_type != 'pdf':
                input_full_path = FileStorageService.get_full_path(relative_path)
                output_full_path = FileStorageService.get_full_path(pdf_path)

                conversion_success = DocumentConverter.convert_to_pdf(
                    input_full_path,
                    output_full_path
                )

                if not conversion_success:
                    # Clean up uploaded file
                    FileStorageService.delete_file(relative_path)
                    flash('Failed to convert document to PDF. Please try again.', 'danger')
                    return redirect(request.url)
            else:
                # For PDF files, pdf_path is same as file_path
                pdf_path = relative_path

            # Get page count
            pdf_full_path = FileStorageService.get_full_path(pdf_path)
            page_count = DocumentConverter.get_pdf_page_count(pdf_full_path)

            # Get title from form or use filename
            title = request.form.get('title', '').strip()
            if not title:
                title = os.path.splitext(original_filename)[0]

            # Create document record
            document = Document(
                user_id=current_user.id,
                title=title,
                original_filename=original_filename,
                file_type=file_type,
                file_path=relative_path,
                pdf_path=pdf_path,
                file_size=file_size,
                page_count=page_count
            )

            db.session.add(document)
            db.session.commit()

            flash(f'Document "{title}" uploaded successfully!', 'success')
            return redirect(url_for('documents.dashboard'))

        except Exception as e:
            current_app.logger.error(f"Upload error: {str(e)}")
            flash('An error occurred during upload. Please try again.', 'danger')
            return redirect(request.url)

    return render_template('dashboard/upload.html')

@bp.route('/documents/<int:document_id>/delete', methods=['POST'])
@login_required
def delete_document(document_id):
    """Delete a document"""
    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
    ).first()

    if not document:
        flash('Document not found.', 'danger')
        return redirect(url_for('documents.dashboard'))

    try:
        # Delete files from storage
        FileStorageService.delete_file(document.file_path)
        if document.pdf_path and document.pdf_path != document.file_path:
            FileStorageService.delete_file(document.pdf_path)

        # Mark as deleted (soft delete) or hard delete
        # Using hard delete for simplicity
        db.session.delete(document)
        db.session.commit()

        flash('Document deleted successfully.', 'success')

    except Exception as e:
        current_app.logger.error(f"Delete error: {str(e)}")
        flash('An error occurred while deleting the document.', 'danger')

    return redirect(url_for('documents.dashboard'))

@bp.route('/documents/<int:document_id>')
@login_required
def view_document(document_id):
    """View document details and analytics"""
    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
    ).first()

    if not document:
        flash('Document not found.', 'danger')
        return redirect(url_for('documents.dashboard'))

    # Get analytics stats
    from app.services.analytics_tracker import AnalyticsTracker
    stats = AnalyticsTracker.get_document_stats(document.id)

    return render_template('dashboard/analytics.html', document=document, stats=stats)
