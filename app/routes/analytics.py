from flask import Blueprint, request, jsonify
from app.services.analytics_tracker import AnalyticsTracker

bp = Blueprint('analytics', __name__, url_prefix='/api')

@bp.route('/track/view', methods=['POST'])
def track_view():
    """AJAX endpoint for viewer heartbeats"""

    # Handle both JSON and FormData
    if request.is_json:
        data = request.json
    else:
        # FormData from sendBeacon
        import json
        data = json.loads(request.form.get('data', '{}'))

    session_id = data.get('session_id')
    current_page = data.get('current_page')
    pages_viewed = data.get('pages_viewed', [])
    duration_seconds = data.get('duration_seconds', 0)
    is_final = data.get('is_final', False)

    if not session_id:
        return jsonify({'error': 'Session ID required'}), 400

    # Update viewing session
    success = AnalyticsTracker.update_viewing_session(
        session_id=session_id,
        current_page=current_page,
        pages_viewed=pages_viewed,
        duration_seconds=duration_seconds
    )

    if is_final:
        AnalyticsTracker.end_viewing_session(session_id)

    if success:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'error': 'Session not found'}), 404

@bp.route('/track/start', methods=['POST'])
def track_start():
    """Start a new viewing session"""

    data = request.json
    link_id = data.get('link_id')
    viewer_email = data.get('viewer_email')
    viewer_ip = request.remote_addr
    user_agent = request.user_agent.string

    if not link_id:
        return jsonify({'error': 'Link ID required'}), 400

    session_id = AnalyticsTracker.start_viewing_session(
        link_id=link_id,
        viewer_email=viewer_email,
        viewer_ip=viewer_ip,
        user_agent=user_agent
    )

    return jsonify({'session_id': session_id}), 200
