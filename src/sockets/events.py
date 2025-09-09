"""SocketIO event handlers and utilities."""

from flask_socketio import emit
from typing import Dict, Any

def emit_parse_started(socketio, user_id: int, job_url: str):
    """Emit event when job parsing starts."""
    payload = {
        'user_id': user_id,
        'job_url': job_url,
        'status': 'started',
        'message': 'Starting to parse job posting...'
    }
    socketio.emit('parse_started', payload, room=f'user_{user_id}')

def emit_parse_finished(socketio, user_id: int, job_data: Dict[str, Any], success: bool = True, error: str = None):
    """Emit event when job parsing finishes."""
    payload = {
        'user_id': user_id,
        'success': success,
        'message': 'Job parsing completed successfully!' if success else f'Job parsing failed: {error}',
        'job_data': job_data if success else None
    }
    socketio.emit('parse_finished', payload, room=f'user_{user_id}')

def emit_match_finished(socketio, user_id: int, match_result: Dict[str, Any], success: bool = True, error: str = None):
    """Emit event when resume matching finishes."""
    payload = {
        'user_id': user_id,
        'success': success,
        'message': 'Resume matching completed successfully!' if success else f'Resume matching failed: {error}',
        'match_result': match_result if success else None
    }
    socketio.emit('match_finished', payload, room=f'user_{user_id}')

def emit_progress_update(socketio, user_id: int, step: str, progress: int, message: str):
    """Emit a general progress update."""
    payload = {
        'user_id': user_id,
        'step': step,
        'progress': progress,  # 0-100
        'message': message
    }
    socketio.emit('progress_update', payload, room=f'user_{user_id}')
