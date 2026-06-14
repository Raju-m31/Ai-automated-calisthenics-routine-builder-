from flask import Flask, render_template, request, jsonify, redirect
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import numpy as np
import json
import os
from datetime import datetime, timedelta
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db, Client, Routine, Session
from routine_builder import build_level_routines

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
        print("   Run reset_database.py to initialize")

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

# Build routines from Excel file
print("\nBuilding routines from Excel sheets...")
try:
    level_routines = build_level_routines()
    print("[OK] Routines loaded successfully!")
except Exception as e:
    print(f"[WARN] Error loading routines: {e}")
    level_routines = {}

# Goal routines and other configs...
goal_routines = {'strength': {'focus_days': [1, 2, 3], 'key_exercises': ['Push-ups', 'Pull-ups', 'Dips', 'Pistol Squats'], 'progression': ['Week 1-2: Build base strength', 'Week 3-4: Increase volume', 'Week 5-6: Add variations', 'Week 7-8: Progressive overload']}}

medical_alternatives = {'shoulder_injury': {'modifications': 'Avoid overhead pressing', 'alternatives': ['Wall push-ups only', 'Floor press variations']}}

def analyze_medical_reason(text):
    text_lower = text.lower()
    if 'shoulder' in text_lower:
        return {'issue': 'shoulder_injury', 'summary': 'Shoulder limitation: use lower-load variations'}
    return {'issue': '', 'summary': 'Medical note received'}

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
        try:
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
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to create client: {str(e)}'}), 500

@app.route('/api/client/<int:client_id>', methods=['PUT'])
def api_update_client(client_id):
    """Update client"""
    data = request.get_json()
    with app.app_context():
        try:
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
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to update client: {str(e)}'}), 500

@app.route('/api/client/<int:client_id>', methods=['DELETE'])
def api_delete_client(client_id):
    """Delete client"""
    with app.app_context():
        try:
            client = Client.query.get(client_id)
            if not client:
                return jsonify({'error': 'Client not found'}), 404
            
            db.session.delete(client)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to delete client: {str(e)}'}), 500

# ============ ROUTINE API ENDPOINTS ============

@app.route('/api/routines', methods=['GET'])
def api_get_routines():
    """Get all routines or filter by client_id"""
    client_id = request.args.get('client_id', type=int)
    with app.app_context():
        if client_id:
            routines = Routine.query.filter_by(client_id=client_id).all()
        else:
            routines = Routine.query.all()
        return jsonify([routine.to_dict() for routine in routines])

@app.route('/api/routine', methods=['POST'])
def api_create_routine():
    """Create new routine"""
    data = request.get_json()
    with app.app_context():
        try:
            routine = Routine(
                client_id=data.get('client_id'),
                week=data.get('week', 1),
                day=data.get('day'),
                exercise=data.get('exercise'),
                sets=data.get('sets', 3),
                reps=data.get('reps'),
                notes=data.get('notes')
            )
            db.session.add(routine)
            db.session.commit()
            return jsonify(routine.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to create routine: {str(e)}'}), 500

@app.route('/api/routine/<int:routine_id>', methods=['PUT'])
def api_update_routine(routine_id):
    """Update routine"""
    data = request.get_json()
    with app.app_context():
        try:
            routine = Routine.query.get(routine_id)
            if not routine:
                return jsonify({'error': 'Routine not found'}), 404
            
            routine.week = data.get('week', routine.week)
            routine.day = data.get('day', routine.day)
            routine.exercise = data.get('exercise', routine.exercise)
            routine.sets = data.get('sets', routine.sets)
            routine.reps = data.get('reps', routine.reps)
            routine.notes = data.get('notes', routine.notes)
            
            db.session.commit()
            return jsonify(routine.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to update routine: {str(e)}'}), 500

@app.route('/api/routine/<int:routine_id>', methods=['DELETE'])
def api_delete_routine(routine_id):
    """Delete routine"""
    with app.app_context():
        try:
            routine = Routine.query.get(routine_id)
            if not routine:
                return jsonify({'error': 'Routine not found'}), 404
            
            db.session.delete(routine)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to delete routine: {str(e)}'}), 500

@app.route('/database/schema')
def database_schema():
    """Display database schema in graphical format"""
    with app.app_context():
        schema_info = {}
        
        # Get all models
        models = {
            'clients': Client,
            'routines': Routine,
            'sessions': Session
        }
        
        for name, model in models.items():
            columns = []
            for column in model.__table__.columns:
                col_info = {
                    'name': column.name,
                    'type': str(column.type),
                    'nullable': column.nullable,
                    'primary_key': column.primary_key,
                    'foreign_key': False
                }
                # Check for foreign key
                for fk in model.__table__.foreign_keys:
                    if fk.parent.name == column.name:
                        col_info['foreign_key'] = True
                        col_info['references'] = str(fk.column)
                columns.append(col_info)
            
            # Get record count
            record_count = model.query.count()
            
            schema_info[name] = {
                'columns': columns,
                'record_count': record_count,
                'relationships': []
            }
        
        # Add relationship info
        schema_info['clients']['relationships'] = [
            {'type': 'one-to-many', 'target': 'routines', 'via': 'client_id'},
            {'type': 'one-to-many', 'target': 'sessions', 'via': 'client_id'}
        ]
        
        return render_template('database_schema.html', schema=schema_info)

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

    # Get routine for this level
    routines = level_routines.get(level, [])
    if routines:
        selected_routine = routines[0]  # Use first routine for this level
        seven_day_routine = selected_routine['seven_day']
        four_week_plan = selected_routine['four_week']
    else:
        # Fallback to default structure
        seven_day_routine = {f'day{i}': {'name': f'Day {i}', 'exercises': []} for i in range(1, 8)}
        four_week_plan = [[{'name': f'Day {i}', 'exercises': []} for i in range(1, 8)]]
    
    weekly_plan = seven_day_routine
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
        try:
            session = Session(client_id=1, session_data=goal_data)
            db.session.add(session)
            db.session.commit()
        except Exception as e:
            print(f"[WARN] Could not save session to database: {e}")
            db.session.rollback()

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
        try:
            db.create_all()
            print("[OK] Database tables created/verified successfully!")
        except Exception as e:
            print(f"[WARN] Could not initialize database tables: {e}")
            print("  Make sure MySQL server is running and reset_database.py has been executed")
    app.run(debug=True, host='0.0.0.0', port=5000)
