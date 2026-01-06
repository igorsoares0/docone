from datetime import datetime
from app import db
from app.models.link import ShareableLink

class LinkGeneratorService:
    """Service for creating and managing shareable links"""

    @staticmethod
    def create_link(document_id, name=None, password=None, require_email=True,
                   expires_at=None, max_views=None, allow_download=False, custom_message=None):
        """
        Create a new shareable link for a document
        Returns: ShareableLink object
        """
        # Generate unique link code
        link_code = ShareableLink.generate_link_code()

        # Ensure uniqueness (very unlikely to collide, but check anyway)
        while ShareableLink.query.filter_by(link_code=link_code).first():
            link_code = ShareableLink.generate_link_code()

        # Create link
        link = ShareableLink(
            document_id=document_id,
            link_code=link_code,
            name=name,
            require_email=require_email,
            expires_at=expires_at,
            max_views=max_views,
            allow_download=allow_download,
            custom_message=custom_message
        )

        # Set password if provided
        if password:
            link.set_password(password)

        db.session.add(link)
        db.session.commit()

        return link

    @staticmethod
    def validate_link_access(link_code, password=None):
        """
        Validate if a link can be accessed
        Returns: (is_valid, error_message, link_object)
        """
        link = ShareableLink.query.filter_by(link_code=link_code).first()

        if not link:
            return False, "Link not found", None

        if not link.is_valid:
            if not link.is_active:
                return False, "This link has been deactivated", link
            elif link.expires_at and link.expires_at < datetime.utcnow():
                return False, "This link has expired", link
            elif link.max_views and link.view_count >= link.max_views:
                return False, "This link has reached its view limit", link

        if link.requires_password:
            if not password:
                return False, "Password required", link
            if not link.check_password(password):
                return False, "Incorrect password", link

        return True, None, link

    @staticmethod
    def increment_view_count(link_id):
        """Increment the view count for a link"""
        link = ShareableLink.query.get(link_id)
        if link:
            link.view_count += 1
            link.last_viewed_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    @staticmethod
    def update_link(link_id, **kwargs):
        """Update link settings"""
        link = ShareableLink.query.get(link_id)
        if not link:
            return None

        # Update allowed fields
        allowed_fields = ['name', 'require_email', 'is_active', 'expires_at',
                         'max_views', 'allow_download', 'custom_message']

        for field in allowed_fields:
            if field in kwargs:
                setattr(link, field, kwargs[field])

        # Handle password separately
        if 'password' in kwargs:
            if kwargs['password']:
                link.set_password(kwargs['password'])
            else:
                link.password_hash = None

        db.session.commit()
        return link

    @staticmethod
    def delete_link(link_id):
        """Delete a link"""
        link = ShareableLink.query.get(link_id)
        if link:
            db.session.delete(link)
            db.session.commit()
            return True
        return False

    @staticmethod
    def deactivate_link(link_id):
        """Deactivate a link (soft delete)"""
        link = ShareableLink.query.get(link_id)
        if link:
            link.is_active = False
            db.session.commit()
            return True
        return False
