from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db, socketio
from app.models import Task

tasks = Blueprint('tasks', __name__)


def emit_task_event(event_name, task_data):
    socketio.emit(event_name, task_data, namespace='/tasks')


@tasks.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    status_filter   = request.args.get('status')
    priority_filter = request.args.get('priority')
    sort_by         = request.args.get('sort', 'created_at')
    order           = request.args.get('order', 'desc')
    query = Task.query.filter_by(user_id=current_user.id)
    if status_filter and status_filter in Task.STATUS_CHOICES:
        query = query.filter_by(status=status_filter)
    if priority_filter and priority_filter in Task.PRIORITY_CHOICES:
        query = query.filter_by(priority=priority_filter)
    sort_col = getattr(Task, sort_by, Task.created_at)
    query = query.order_by(sort_col.asc() if order == 'asc' else sort_col.desc())
    all_tasks = query.all()
    return jsonify({'success': True, 'count': len(all_tasks),
                    'tasks': [t.to_dict() for t in all_tasks]}), 200


@tasks.route('/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'success': False, 'message': 'Task not found.'}), 404
    return jsonify({'success': True, 'task': task.to_dict()}), 200


@tasks.route('/tasks', methods=['POST'])
@login_required
def create_task():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Request body must be JSON.'}), 400
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'success': False, 'message': 'Title is required.'}), 400
    priority = data.get('priority', Task.PRIORITY_MEDIUM)
    status   = data.get('status',   Task.STATUS_PENDING)
    if priority not in Task.PRIORITY_CHOICES:
        return jsonify({'success': False, 'message': f'Invalid priority. Choose from: {Task.PRIORITY_CHOICES}'}), 400
    if status not in Task.STATUS_CHOICES:
        return jsonify({'success': False, 'message': f'Invalid status. Choose from: {Task.STATUS_CHOICES}'}), 400
    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.fromisoformat(data['due_date'])
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid due_date format.'}), 400
    task = Task(title=title, description=data.get('description', '').strip(),
                priority=priority, status=status, due_date=due_date,
                user_id=current_user.id)
    db.session.add(task)
    db.session.commit()
    task_dict = task.to_dict()
    emit_task_event('task_created', {'message': f'New task created: {task.title}',
                                     'task': task_dict, 'user_id': current_user.id})
    return jsonify({'success': True, 'message': 'Task created.', 'task': task_dict}), 201


@tasks.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'success': False, 'message': 'Task not found.'}), 404
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Request body must be JSON.'}), 400
    if 'title' in data:
        t = data['title'].strip()
        if not t:
            return jsonify({'success': False, 'message': 'Title cannot be empty.'}), 400
        task.title = t
    if 'description' in data:
        task.description = data['description'].strip()
    if 'priority' in data:
        if data['priority'] not in Task.PRIORITY_CHOICES:
            return jsonify({'success': False, 'message': f'Invalid priority. Choose from: {Task.PRIORITY_CHOICES}'}), 400
        task.priority = data['priority']
    if 'status' in data:
        if data['status'] not in Task.STATUS_CHOICES:
            return jsonify({'success': False, 'message': f'Invalid status. Choose from: {Task.STATUS_CHOICES}'}), 400
        task.status = data['status']
    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.fromisoformat(data['due_date'])
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid due_date format.'}), 400
        else:
            task.due_date = None
    task.updated_at = datetime.utcnow()
    db.session.commit()
    task_dict = task.to_dict()
    emit_task_event('task_updated', {'message': f'Task updated: {task.title}',
                                     'task': task_dict, 'user_id': current_user.id})
    return jsonify({'success': True, 'message': 'Task updated.', 'task': task_dict}), 200


@tasks.route('/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({'success': False, 'message': 'Task not found.'}), 404
    task_info = {'id': task.id, 'title': task.title}
    db.session.delete(task)
    db.session.commit()
    emit_task_event('task_deleted', {'message': f'Task deleted: {task_info["title"]}',
                                     'task': task_info, 'user_id': current_user.id})
    return jsonify({'success': True, 'message': 'Task deleted.'}), 200


@tasks.route('/tasks/bulk-status', methods=['PATCH'])
@login_required
def bulk_update_status():
    data       = request.get_json()
    task_ids   = data.get('task_ids', [])
    new_status = data.get('status')
    if not task_ids or not new_status:
        return jsonify({'success': False, 'message': 'task_ids and status are required.'}), 400
    if new_status not in Task.STATUS_CHOICES:
        return jsonify({'success': False, 'message': f'Invalid status. Choose from: {Task.STATUS_CHOICES}'}), 400
    updated = Task.query.filter(Task.id.in_(task_ids),
                                Task.user_id == current_user.id).update(
        {'status': new_status, 'updated_at': datetime.utcnow()}, synchronize_session='fetch')
    db.session.commit()
    emit_task_event('bulk_updated', {'message': f'{updated} tasks marked as {new_status}',
                                     'count': updated, 'user_id': current_user.id})
    return jsonify({'success': True, 'message': f'{updated} tasks updated to {new_status}.'}), 200
