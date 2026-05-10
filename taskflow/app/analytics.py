# pyrefly: ignore [missing-import]
import numpy as np
import pandas as pd
from flask import Blueprint, jsonify, render_template
from flask_login import login_required, current_user
from app.models import Task

analytics = Blueprint('analytics', __name__)


def get_task_dataframe(user_id):
    tasks = Task.query.filter_by(user_id=user_id).all()
    if not tasks:
        return pd.DataFrame(columns=['id','title','description','priority','status',
                                      'created_at','updated_at','due_date'])
    df = pd.DataFrame([t.to_dict() for t in tasks])
    for col in ['created_at', 'updated_at', 'due_date']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    return df


@analytics.route('/')
@login_required
def analytics_page():
    return render_template('analytics.html')


@analytics.route('/summary', methods=['GET'])
@login_required
def summary():
    df = get_task_dataframe(current_user.id)
    total_tasks = len(df)

    if total_tasks == 0:
        return jsonify({'success': True, 'analytics': {
            'total_tasks': 0, 'completed_tasks': 0, 'pending_tasks': 0,
            'in_progress_tasks': 0, 'completion_percentage': 0.0,
            'priority_breakdown': {}, 'status_breakdown': {},
            'avg_tasks_per_day': 0.0, 'completion_rate_7days': 0,
            'priority_completion_rates': {}, 'std_completion': 0.0,
            'np_summary': {}, 'timeline_data': []
        }}), 200

    status_counts     = df['status'].value_counts().to_dict()
    completed_tasks   = int(status_counts.get('completed', 0))
    pending_tasks     = int(status_counts.get('pending', 0))
    in_progress_tasks = int(status_counts.get('in_progress', 0))

    completion_percentage = float(np.round((completed_tasks / total_tasks) * 100, 2))

    priority_breakdown = {k: int(v) for k, v in df['priority'].value_counts().to_dict().items()}

    status_breakdown = {}
    for status, count in status_counts.items():
        status_breakdown[status] = {
            'count': int(count),
            'percentage': float(np.round((count / total_tasks) * 100, 2))
        }

    df['created_date'] = df['created_at'].dt.date
    tasks_per_day    = df.groupby('created_date').size()
    avg_tasks_per_day = float(np.round(np.mean(tasks_per_day.values), 2))
    std_completion    = float(np.round(np.std(tasks_per_day.values), 2)) if len(tasks_per_day) > 1 else 0.0

    now = pd.Timestamp.now(tz='UTC')
    seven_days_ago = now - pd.Timedelta(days=7)
    if df['updated_at'].dt.tz is not None:
        recent_mask = (df['updated_at'] >= seven_days_ago) & (df['status'] == 'completed')
    else:
        recent_mask = (df['updated_at'] >= seven_days_ago.tz_localize(None)) & (df['status'] == 'completed')
    completion_rate_7days = int(df[recent_mask].shape[0])

    priority_completion_rates = {}
    for priority in df['priority'].unique():
        pf = df[df['priority'] == priority]
        pt = len(pf)
        pc = len(pf[pf['status'] == 'completed'])
        priority_completion_rates[priority] = {
            'total': pt, 'completed': pc,
            'rate': float(np.round((pc / pt) * 100, 2)) if pt > 0 else 0.0
        }

    task_id_array = np.array(df['id'].tolist())
    np_summary = {
        'mean_task_id': float(np.mean(task_id_array)),
        'max_task_id': int(np.max(task_id_array)),
        'min_task_id': int(np.min(task_id_array)),
        'total_count': int(np.sum(np.ones(len(task_id_array))))
    }

    timeline_data = (
        df.groupby(df['created_at'].dt.strftime('%Y-%m-%d')).size()
        .reset_index(name='count')
        .rename(columns={'created_at': 'date'})
        .to_dict(orient='records')
    )

    return jsonify({'success': True, 'analytics': {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completion_percentage': completion_percentage,
        'priority_breakdown': priority_breakdown,
        'status_breakdown': status_breakdown,
        'avg_tasks_per_day': avg_tasks_per_day,
        'completion_rate_7days': completion_rate_7days,
        'priority_completion_rates': priority_completion_rates,
        'std_completion': std_completion,
        'np_summary': np_summary,
        'timeline_data': timeline_data
    }}), 200
