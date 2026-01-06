from datetime import datetime
from app import db
from app.models.analytics import DocumentView
from app.models.link import ShareableLink

class AnalyticsTracker:
    """Service for tracking document views and analytics"""

    @staticmethod
    def start_viewing_session(link_id, viewer_email, viewer_ip, user_agent):
        """
        Create a new viewing session
        Returns: session_id
        """
        import secrets

        session_id = secrets.token_urlsafe(32)

        view = DocumentView(
            link_id=link_id,
            viewer_email=viewer_email,
            viewer_ip=viewer_ip,
            viewer_user_agent=user_agent,
            session_id=session_id
        )

        db.session.add(view)
        db.session.commit()

        return session_id

    @staticmethod
    def update_viewing_session(session_id, current_page=None, pages_viewed=None, duration_seconds=None):
        """
        Update viewing session with tracking data
        Returns: True if successful
        """
        view = DocumentView.query.filter_by(session_id=session_id).first()

        if not view:
            return False

        if current_page is not None:
            view.current_page = current_page
            view.max_page_reached = max(view.max_page_reached or 0, current_page)

        if pages_viewed is not None:
            view.pages_viewed = pages_viewed
            view.total_page_views = len(pages_viewed)

        if duration_seconds is not None:
            view.duration_seconds = duration_seconds

        db.session.commit()
        return True

    @staticmethod
    def end_viewing_session(session_id):
        """
        Finalize viewing session
        Returns: True if successful
        """
        view = DocumentView.query.filter_by(session_id=session_id).first()

        if not view:
            return False

        view.ended_at = datetime.utcnow()
        db.session.commit()
        return True

    @staticmethod
    def get_document_stats(document_id):
        """
        Get aggregate statistics for a document
        Returns: dict with stats
        """
        from sqlalchemy import func

        # Get all links for this document
        link_ids = db.session.query(ShareableLink.id).filter_by(document_id=document_id).all()
        link_ids = [lid[0] for lid in link_ids]

        # Total views
        total_views = DocumentView.query.filter(DocumentView.link_id.in_(link_ids)).count()

        # Unique viewers (by email)
        unique_viewers = db.session.query(func.count(func.distinct(DocumentView.viewer_email))).filter(
            DocumentView.link_id.in_(link_ids),
            DocumentView.viewer_email.isnot(None)
        ).scalar() or 0

        # Average duration
        avg_duration = db.session.query(func.avg(DocumentView.duration_seconds)).filter(
            DocumentView.link_id.in_(link_ids),
            DocumentView.duration_seconds.isnot(None),
            DocumentView.duration_seconds > 0
        ).scalar() or 0

        # Get all views
        views = DocumentView.query.filter(DocumentView.link_id.in_(link_ids)).order_by(
            DocumentView.started_at.desc()
        ).all()

        return {
            'total_views': total_views,
            'unique_viewers': unique_viewers,
            'avg_duration': int(avg_duration) if avg_duration else 0,
            'views': views
        }

    @staticmethod
    def get_link_stats(link_id):
        """
        Get statistics for a specific link
        Returns: dict with stats
        """
        from sqlalchemy import func

        # Total views
        total_views = DocumentView.query.filter_by(link_id=link_id).count()

        # Unique viewers
        unique_viewers = db.session.query(func.count(func.distinct(DocumentView.viewer_email))).filter_by(
            link_id=link_id
        ).filter(DocumentView.viewer_email.isnot(None)).scalar() or 0

        # Average duration
        avg_duration = db.session.query(func.avg(DocumentView.duration_seconds)).filter_by(
            link_id=link_id
        ).filter(
            DocumentView.duration_seconds.isnot(None),
            DocumentView.duration_seconds > 0
        ).scalar() or 0

        # Get all views
        views = DocumentView.query.filter_by(link_id=link_id).order_by(
            DocumentView.started_at.desc()
        ).all()

        return {
            'total_views': total_views,
            'unique_viewers': unique_viewers,
            'avg_duration': int(avg_duration) if avg_duration else 0,
            'views': views
        }
