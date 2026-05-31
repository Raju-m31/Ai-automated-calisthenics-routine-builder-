"""Generate new app.py with MySQL database integration"""

new_app_content = '''from flask import Flask, render_template, request, jsonify, redirect
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import numpy as np
import json
import os
from datetime import datetime, timedelta
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db, Client, Routine, Session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
db.init_app(app)

# Initialize model training data
with app.app_context():
    try:
        client_count = Client.query.count()
        print(f"[OK] Database connected: {client_count} clients found")
    except Exception as e:
        print(f"[WARN] Database not ready: {e}")
        print("   Run setup_database.py to initialize")

# Training data for ML model
synthetic_data = {
    'push_ups': [10, 20, 30, 40, 50, 5, 15, 25, 35, 45],
    'pull_ups': [5, 10, 15, 20, 25, 2, 7, 12, 17, 22],
    'level': ['beginner', 'intermediate', 'advanced', 'advanced', 'expert', 'beginner', 'beginner', 'intermediate', 'advanced', 'expert']
}

data = synthetic_data
df = pd.DataFrame(data)

X = df[['push_ups', 'pull_ups']]
y = df['level']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X_train, y_train)

train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)
print(f"Model: Training={train_score:.2%}, Test={test_score:.2%}")

# Goal routines and other configs...
goal_routines = {'strength': {'focus_days': [1, 2, 3], 'key_exercises': ['Push-ups', 'Pull-ups', 'Dips', 'Pistol Squats'], 'progression': ['Week 1-2: Build base strength', 'Week 3-4: Increase volume', 'Week 5-6: Add variations', 'Week 7-8: Progressive overload']}}

weekly_routines = {'beginner': {'day1': {'name': 'Upper Body Push Focus', 'exercises': [{'name': 'Wall Push-ups', 'sets': 3, 'reps': '8-12', 'rest': '60s'}, {'name': 'Knee Push-ups', 'sets': 3, 'reps': '6-10', 'rest': '60s'}, {'name': 'Plank', 'sets': 3, 'reps': '20-30s', 'rest': '45s'}, {'name': 'Wall Sit', 'sets': 3, 'reps': '15-25s', 'rest': '45s'}]}}, 'intermediate': {'day1': {'name': 'Push Day', 'exercises': [{'name': 'Standard Push-ups', 'sets': 4, 'reps': '8-12', 'rest': '90s'}]}}, 'advanced': {'day1': {'name': 'Push Power Day', 'exercises': [{'name': 'One-Arm Push-ups', 'sets': 4, 'reps': '3-5 each arm', 'rest': '120s'}]}}, 'expert': {'day1': {'name': 'Elite Push Mastery', 'exercises': [{'name': 'One-Arm Planche Push-ups', 'sets': 4, 'reps': '2-4 each arm', 'rest': '180s'}]}}}

medical_alternatives = {'shoulder_injury': {'modifications': 'Avoid overhead pressing', 'alternatives': ['Wall push-ups only', 'Floor press variations']}}

def analyze_medical_reason(text):
    text_lower = text.lower()
    if 'shoulder' in text_lower:
        return {'issue': 'shoulder_injury', 'summary': 'Shoulder limitation: use lower-load variations'}
    return {'issue': '', 'summary': 'Medical note received'}

def create_4week_progression(routine, level):
    import copy
    four_weeks = []
    for week in range(1, 5):
        week_routine = []
        for day in range(1, 8):
            day_key = f'day{day}'
            if day_key in routine:
                day_data = copy.deepcopy(routine[day_key])
                day_data['week'] = week
                week_routine.append(day_data)
        four_weeks.append(week_routine)
    return four_weeks

# ============ ROUTES ============

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/database')
def database_view():
    """View all clients in database with nice table"""
    with app.app_context():
        clients = Client.query.all()
        return render_template('database.html', clients=clients)

@app.route('/api/clients', methods=['GET'])
def api_clients():
    """API to get all clients as JSON"""
    with app.app_context():
        clients = Client.query.all()
        return jsonify([client.to_dict() for client in clients])

@app.route('/api/client/<int:client_id>', methods=['GET'])
def api_get_client(client_id):
    """Get single client"""
    with app.app_context():
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        return jsonify(client.to_dict())

@app.route('/api/client', methods=['POST'])
def api_create_client():
    """Create new client"""
    data = request.get_json()
    with app.app_context():
        client = Client(
            name=data.get('name'),
            goal=data.get('goal'),
            push_ups=data.get('push_ups', 0),
            pull_ups=data.get('pull_ups', 0),
            skill_level=data.get('skill_level', 'beginner'),
            medical_conditions=data.get('medical_conditions')
        )
        db.session.add(client)
        db.session.commit()
        return jsonify(client.to_dict()), 201

@app.route('/api/client/<int:client_id>', methods=['PUT'])
def api_update_client(client_id):
    """Update client"""
    data = request.get_json()
    with app.app_context():
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        client.name = data.get('name', client.name)
        client.goal = data.get('goal', client.goal)
        client.push_ups = data.get('push_ups', client.push_ups)
        client.pull_ups = data.get('pull_ups', client.pull_ups)
        client.skill_level = data.get('skill_level', client.skill_level)
        client.medical_conditions = data.get('medical_conditions', client.medical_conditions)
        
        db.session.commit()
        return jsonify(client.to_dict())

@app.route('/api/client/<int:client_id>', methods=['DELETE'])
def api_delete_client(client_id):
    """Delete client"""
    with app.app_context():
        client = Client.query.get(client_id)
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        db.session.delete(client)
        db.session.commit()
        return jsonify({'success': True})

@app.route('/generate', methods=['POST'])
def generate():
    push_ups = int(request.form['push_ups'])
    pull_ups = int(request.form['pull_ups'])
    goal = request.form.get('goal', 'general').lower()
    goal_details = request.form.get('goal_details', '').strip()
    medical = request.form.get('medical', '')
    manual_reason = request.form.get('manual_reason', '').strip()

    level = model.predict([[push_ups, pull_ups]])[0]
    medical_summary = ''
    chosen_issue = medical

    if manual_reason:
        analysis = analyze_medical_reason(manual_reason)
        chosen_issue = analysis.get('issue', '') or chosen_issue
        medical_summary = analysis.get('summary', '')

    routine = weekly_routines.get(level, weekly_routines['beginner'])
    four_week_plan = create_4week_progression(routine, level)
    weekly_plan = four_week_plan[0]

    progression_tips = goal_routines.get(goal, {}).get('progression', ["Week 1-2: Focus on form", "Week 3-4: Increase reps", "Week 5-6: Add variations", "Week 7-8: Increase intensity"])

    import uuid
    goal_session_id = str(uuid.uuid4())
    goal_data = {
        'id': goal_session_id,
        'goal': goal,
        'goal_details': goal_details,
        'push_ups': push_ups,
        'pull_ups': pull_ups,
        'level': level,
        'start_date': datetime.now().isoformat(),
        'week_4_review_date': (datetime.now() + timedelta(days=28)).isoformat(),
        'completed_weeks': 0,
        'four_week_routine': four_week_plan
    }
    
    with app.app_context():
        session = Session(client_id=1, session_data=goal_data)
        db.session.add(session)
        db.session.commit()

    return render_template('result.html',
                         weekly_plan=weekly_plan,
                         four_week_plan=four_week_plan,
                         level=level,
                         medical_summary=medical_summary,
                         manual_reason=manual_reason,
                         progression_tips=progression_tips,
                         push_ups=push_ups,
                         pull_ups=pull_ups,
                         goal=goal,
                         goal_details=goal_details,
                         goal_session_id=goal_session_id)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
'''

# Write the new app.py
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_app_content)

print("[DONE] app.py updated with MySQL database integration!")
