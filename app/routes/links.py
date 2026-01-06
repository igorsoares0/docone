from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models.document import Document
from app.models.link import ShareableLink
from app.services.link_generator import LinkGeneratorService

bp = Blueprint('links', __name__)

@bp.route('/documents/<int:document_id>/links')
@login_required
def manage_links(document_id):
    """Manage links for a document"""
    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
    ).first()

    if not document:
        flash('Document not found.', 'danger')
        return redirect(url_for('documents.dashboard'))

    links = document.shareable_links.order_by(ShareableLink.created_at.desc()).all()

    return render_template('links/manage.html', document=document, links=links)

@bp.route('/documents/<int:document_id>/links/create', methods=['GET', 'POST'])
@login_required
def create_link(document_id):
    """Create a new shareable link"""
    document = Document.query.filter_by(
        id=document_id,
        user_id=current_user.id
    ).first()

    if not document:
        flash('Document not found.', 'danger')
        return redirect(url_for('documents.dashboard'))

    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip() or None
            password = request.form.get('password', '').strip() or None
            require_email = request.form.get('require_email') == 'on'
            allow_download = request.form.get('allow_download') == 'on'
            custom_message = request.form.get('custom_message', '').strip() or None

            # Handle expiration
            expires_at = None
            expires_str = request.form.get('expires_at', '').strip()
            if expires_str:
                try:
                    expires_at = datetime.strptime(expires_str, '%Y-%m-%d')
                except ValueError:
                    flash('Invalid expiration date format.', 'warning')

            # Handle max views
            max_views = None
            max_views_str = request.form.get('max_views', '').strip()
            if max_views_str:
                try:
                    max_views = int(max_views_str)
                except ValueError:
                    flash('Invalid max views value.', 'warning')

            # Create link
            link = LinkGeneratorService.create_link(
                document_id=document.id,
                name=name,
                password=password,
                require_email=require_email,
                expires_at=expires_at,
                max_views=max_views,
                allow_download=allow_download,
                custom_message=custom_message
            )

            flash('Shareable link created successfully!', 'success')
            return redirect(url_for('links.manage_links', document_id=document.id))

        except Exception as e:
            flash(f'Error creating link: {str(e)}', 'danger')
            return redirect(request.url)

    return render_template('links/create.html', document=document)

@bp.route('/links/<int:link_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_link(link_id):
    """Edit an existing link"""
    link = ShareableLink.query.get(link_id)

    if not link:
        flash('Link not found.', 'danger')
        return redirect(url_for('documents.dashboard'))

    # Verify ownership
    if link.document.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('documents.dashboard'))

    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip() or None
            password = request.form.get('password', '').strip() or None
            require_email = request.form.get('require_email') == 'on'
            allow_download = request.form.get('allow_download') == 'on'
            is_active = request.form.get('is_active') == 'on'
            custom_message = request.form.get('custom_message', '').strip() or None

            # Handle expiration
            expires_at = None
            expires_str = request.form.get('expires_at', '').strip()
            if expires_str:
                try:
                    expires_at = datetime.strptime(expires_str, '%Y-%m-%d')
                except ValueError:
                    pass

            # Handle max views
            max_views = None
            max_views_str = request.form.get('max_views', '').strip()
            if max_views_str:
                try:
                    max_views = int(max_views_str)
                except ValueError:
                    pass

            # Update link
            LinkGeneratorService.update_link(
                link_id=link.id,
                name=name,
                password=password,
                require_email=require_email,
                is_active=is_active,
                expires_at=expires_at,
                max_views=max_views,
                allow_download=allow_download,
                custom_message=custom_message
            )

            flash('Link updated successfully!', 'success')
            return redirect(url_for('links.manage_links', document_id=link.document_id))

        except Exception as e:
            flash(f'Error updating link: {str(e)}', 'danger')
            return redirect(request.url)

    return render_template('links/edit.html', link=link)

@bp.route('/links/<int:link_id>/delete', methods=['POST'])
@login_required
def delete_link(link_id):
    """Delete a link"""
    link = ShareableLink.query.get(link_id)

    if not link:
        flash('Link not found.', 'danger')
        return redirect(url_for('documents.dashboard'))

    # Verify ownership
    if link.document.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('documents.dashboard'))

    document_id = link.document_id

    try:
        LinkGeneratorService.delete_link(link_id)
        flash('Link deleted successfully.', 'success')
    except Exception as e:
        flash(f'Error deleting link: {str(e)}', 'danger')

    return redirect(url_for('links.manage_links', document_id=document_id))
