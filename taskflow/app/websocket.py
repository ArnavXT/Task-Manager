from flask_login import current_user
from flask_socketio import emit, join_room, leave_room, disconnect
from app import socketio


@socketio.on('connect', namespace='/tasks')
def handle_connect():
    if current_user.is_authenticated:
        room = f'user_{current_user.id}'
        join_room(room)
        emit('connected', {
            'message': 'Connected to real-time task updates.',
            'user': current_user.username,
            'room': room
        })
    else:
        emit('error', {'message': 'Authentication required.'})
        disconnect()


@socketio.on('disconnect', namespace='/tasks')
def handle_disconnect():
    if current_user.is_authenticated:
        leave_room(f'user_{current_user.id}')


@socketio.on('ping', namespace='/tasks')
def handle_ping(data):
    emit('pong', {'message': 'pong', 'timestamp': data.get('timestamp')})


@socketio.on('request_notification', namespace='/tasks')
def handle_notification_request(data):
    if current_user.is_authenticated:
        emit('notification', {
            'type': 'info',
            'message': data.get('message', 'WebSocket is working!'),
            'user': current_user.username
        })
