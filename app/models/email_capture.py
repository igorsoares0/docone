from datetime import datetime
from app import db

class CapturedEmail(db.Model):
    """Store emails captured from viewers before document access"""

    __tablename__ = 'captured_emails'

    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('shareable_links.id'), nullable=False, index=True)

    email = db.Column(db.String(120), nullable=False, index=True)
    captured_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Additional optional fields
    full_name = db.Column(db.String(100))
    company = db.Column(db.String(100))

    # Tracking
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))

    # Whether they actually viewed the document after capturing email
    viewed_document = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'<CapturedEmail {self.email}>'
