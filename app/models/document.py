from datetime import datetime
from app import db

class Document(db.Model):
    """Document model for uploaded files"""

    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # File information
    title = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # pdf, docx, pptx
    file_path = db.Column(db.String(500), nullable=False)  # Path to stored file
    pdf_path = db.Column(db.String(500))  # Path to converted PDF (if different from file_path)
    file_size = db.Column(db.BigInteger)  # Size in bytes
    page_count = db.Column(db.Integer)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    deleted_at = db.Column(db.DateTime)

    # Relationships
    shareable_links = db.relationship('ShareableLink', backref='document', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def total_views(self):
        """Calculate total views across all links"""
        return sum(link.view_count for link in self.shareable_links)

    @property
    def unique_viewers(self):
        """Count unique viewers by email across all links"""
        from app.models.analytics import DocumentView
        from app.models.link import ShareableLink

        unique_count = db.session.query(db.func.count(db.distinct(DocumentView.viewer_email))).join(
            ShareableLink
        ).filter(
            ShareableLink.document_id == self.id,
            DocumentView.viewer_email.isnot(None)
        ).scalar()

        return unique_count or 0

    def __repr__(self):
        return f'<Document {self.title}>'
