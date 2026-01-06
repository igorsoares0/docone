from datetime import datetime
from app import db

class DocumentView(db.Model):
    """Track individual document viewing sessions"""

    __tablename__ = 'document_views'

    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('shareable_links.id'), nullable=False, index=True)

    # Viewer information
    viewer_email = db.Column(db.String(120), index=True)  # Captured email
    viewer_ip = db.Column(db.String(45))  # IPv4 or IPv6
    viewer_user_agent = db.Column(db.String(500))

    # Session tracking
    session_id = db.Column(db.String(64), unique=True, nullable=False, index=True)  # Unique session identifier

    # Timing data
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    ended_at = db.Column(db.DateTime)
    duration_seconds = db.Column(db.Integer, default=0)  # Total viewing time

    # Engagement metrics
    pages_viewed = db.Column(db.JSON)  # Array of page numbers viewed
    max_page_reached = db.Column(db.Integer, default=1)
    total_page_views = db.Column(db.Integer, default=0)
    current_page = db.Column(db.Integer, default=1)

    # Geographic data (optional, for future)
    country = db.Column(db.String(2))
    city = db.Column(db.String(100))

    def __repr__(self):
        return f'<DocumentView {self.session_id}>'
