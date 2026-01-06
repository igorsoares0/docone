from datetime import datetime
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class ShareableLink(db.Model):
    """Shareable link model with access control settings"""

    __tablename__ = 'shareable_links'

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False, index=True)

    # Link details
    link_code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100))  # Internal name for organization

    # Security settings
    password_hash = db.Column(db.String(255))  # Optional password protection
    require_email = db.Column(db.Boolean, default=True, nullable=False)

    # Access control
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    expires_at = db.Column(db.DateTime)  # Optional expiration
    max_views = db.Column(db.Integer)  # Optional view limit
    view_count = db.Column(db.Integer, default=0, nullable=False)

    # Customization
    custom_message = db.Column(db.Text)  # Message shown before viewing
    allow_download = db.Column(db.Boolean, default=False, nullable=False)

    # Tracking
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_viewed_at = db.Column(db.DateTime)

    # Relationships
    document_views = db.relationship('DocumentView', backref='link', lazy='dynamic', cascade='all, delete-orphan')
    captured_emails = db.relationship('CapturedEmail', backref='link', lazy='dynamic', cascade='all, delete-orphan')

    @staticmethod
    def generate_link_code():
        """Generate a secure random link code"""
        return secrets.token_urlsafe(16)

    def set_password(self, password):
        """Hash and set password for link protection"""
        if password:
            self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify link password"""
        if not self.password_hash:
            return True  # No password set
        return check_password_hash(self.password_hash, password)

    @property
    def is_valid(self):
        """Check if link is currently valid and accessible"""
        if not self.is_active:
            return False

        # Check expiration
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False

        # Check view limit
        if self.max_views and self.view_count >= self.max_views:
            return False

        return True

    @property
    def requires_password(self):
        """Check if link requires password"""
        return self.password_hash is not None

    def __repr__(self):
        return f'<ShareableLink {self.link_code}>'
