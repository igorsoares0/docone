from flask import Blueprint, render_template, redirect, url_for, flash, request, session, send_file
import secrets
from app import db
from app.models.link import ShareableLink
from app.models.email_capture import CapturedEmail
from app.models.analytics import DocumentView
from app.services.link_generator import LinkGeneratorService
from app.services.file_storage import FileStorageService

bp = Blueprint('viewer', __name__, url_prefix='/v')

@bp.route('/<link_code>')
def view(link_code):
    """Main viewer endpoint - handles password and email gates"""

    # Validate link
    is_valid, error_message, link = LinkGeneratorService.validate_link_access(link_code)

    if not is_valid and not link:
        flash(error_message, 'danger')
        return render_template('viewer/error.html', message=error_message), 404

    # Check if password is required and not yet verified
    if link.requires_password:
        password_verified = session.get(f'link_password_verified_{link_code}', False)
        if not password_verified:
            return redirect(url_for('viewer.password_gate', link_code=link_code))

    # Check if email is required and not yet captured
    if link.require_email:
        email_captured = session.get(f'link_email_captured_{link_code}')
        if not email_captured:
            return redirect(url_for('viewer.email_capture', link_code=link_code))

    # Check if link is valid now (after password/email verification)
    if not link.is_valid:
        flash(error_message or 'This link is no longer valid.', 'warning')
        return render_template('viewer/error.html', message=error_message or 'Link expired'), 403

    # Get or create session ID for analytics tracking
    tracking_session_id = session.get(f'tracking_session_{link_code}')

    # Render document viewer
    return render_template('viewer/document.html',
                          link=link,
                          document=link.document,
                          tracking_session_id=tracking_session_id)

@bp.route('/<link_code>/password', methods=['GET', 'POST'])
def password_gate(link_code):
    """Password protection gate"""

    link = ShareableLink.query.filter_by(link_code=link_code).first()

    if not link or not link.requires_password:
        return redirect(url_for('viewer.view', link_code=link_code))

    # Check if already verified
    if session.get(f'link_password_verified_{link_code}', False):
        return redirect(url_for('viewer.view', link_code=link_code))

    if request.method == 'POST':
        password = request.form.get('password', '')

        if link.check_password(password):
            # Store verification in session
            session[f'link_password_verified_{link_code}'] = True
            return redirect(url_for('viewer.view', link_code=link_code))
        else:
            flash('Incorrect password. Please try again.', 'danger')

    return render_template('viewer/password_gate.html', link=link, document=link.document)

@bp.route('/<link_code>/email', methods=['GET', 'POST'])
def email_capture(link_code):
    """Email capture gate"""

    link = ShareableLink.query.filter_by(link_code=link_code).first()

    if not link or not link.require_email:
        return redirect(url_for('viewer.view', link_code=link_code))

    # Check if email already captured for this session
    if session.get(f'link_email_captured_{link_code}'):
        return redirect(url_for('viewer.view', link_code=link_code))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        full_name = request.form.get('full_name', '').strip() or None
        company = request.form.get('company', '').strip() or None

        if not email:
            flash('Email address is required.', 'danger')
            return render_template('viewer/email_capture.html', link=link, document=link.document)

        # Store captured email
        captured = CapturedEmail(
            link_id=link.id,
            email=email,
            full_name=full_name,
            company=company,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )

        db.session.add(captured)

        # Create analytics session
        session_id = secrets.token_urlsafe(32)

        document_view = DocumentView(
            link_id=link.id,
            viewer_email=email,
            viewer_ip=request.remote_addr,
            viewer_user_agent=request.user_agent.string,
            session_id=session_id
        )

        db.session.add(document_view)
        db.session.commit()

        # Store in session
        session[f'link_email_captured_{link_code}'] = email
        session[f'tracking_session_{link_code}'] = session_id

        # Increment view count
        LinkGeneratorService.increment_view_count(link.id)

        return redirect(url_for('viewer.view', link_code=link_code))

    return render_template('viewer/email_capture.html', link=link, document=link.document)

@bp.route('/<link_code>/document.pdf')
def serve_pdf(link_code):
    """Serve the PDF file"""

    # Validate access
    link = ShareableLink.query.filter_by(link_code=link_code).first()

    if not link:
        return "Document not found", 404

    # Check session for password verification
    if link.requires_password:
        if not session.get(f'link_password_verified_{link_code}', False):
            return "Access denied", 403

    # Check session for email capture
    if link.require_email:
        if not session.get(f'link_email_captured_{link_code}'):
            return "Access denied", 403

    # Get PDF file path
    pdf_path = link.document.pdf_path
    full_path = FileStorageService.get_full_path(pdf_path)

    # Serve file
    return send_file(
        full_path,
        mimetype='application/pdf',
        as_attachment=False,
        download_name=link.document.original_filename
    )

@bp.route('/<link_code>/download')
def download_pdf(link_code):
    """Download the PDF file"""

    link = ShareableLink.query.filter_by(link_code=link_code).first()

    if not link or not link.allow_download:
        return "Download not allowed", 403

    # Check access permissions (same as serve_pdf)
    if link.requires_password and not session.get(f'link_password_verified_{link_code}', False):
        return "Access denied", 403

    if link.require_email and not session.get(f'link_email_captured_{link_code}'):
        return "Access denied", 403

    # Get PDF file path
    pdf_path = link.document.pdf_path
    full_path = FileStorageService.get_full_path(pdf_path)

    # Serve file as download
    return send_file(
        full_path,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=link.document.original_filename
    )
