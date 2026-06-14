"""
Reset Database Script for SQLite
Creates a clean database with sample data
Run this before starting the app: python reset_database.py
"""
import os
import sys
from datetime import datetime, timedelta
import random

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, Client, Routine, Session
from config import SQLALCHEMY_DATABASE_URI

# Sample data for populating the database
SAMPLE_CLIENTS = [
    {
        'name': 'Alex Johnson',
        'goal': 'Handstand',
        'push_ups': 25,
        'pull_ups': 12,
        'skill_level': 'intermediate',
        'medical_conditions': None
    },
    {
        'name': 'Sarah Williams',
        'goal': 'Muscle Up',
        'push_ups': 35,
        'pull_ups': 18,
        'skill_level': 'advanced',
        'medical_conditions': None
    },
    {
        'name': 'Mike Brown',
        'goal': 'General Fitness',
        'push_ups': 15,
        'pull_ups': 8,
        'skill_level': 'beginner',
        'medical_conditions': 'None'
    },
    {
        'name': 'Emma Davis',
        'goal': 'Strength Building',
        'push_ups': 30,
        'pull_ups': 14,
        'skill_level': 'intermediate',
        'medical_conditions': None
    },
    {
        'name': 'John Smith',
        'goal': 'Endurance',
        'push_ups': 40,
        'pull_ups': 20,
        'skill_level': 'advanced',
        'medical_conditions': None
    },
    {
        'name': 'Lisa Martinez',
        'goal': 'Flexibility',
        'push_ups': 12,
        'pull_ups': 6,
        'skill_level': 'beginner',
        'medical_conditions': 'Shoulder flexibility issues'
    },
    {
        'name': 'David Lee',
        'goal': 'Olympic Rings',
        'push_ups': 45,
        'pull_ups': 22,
        'skill_level': 'expert',
        'medical_conditions': None
    },
    {
        'name': 'Jessica Taylor',
        'goal': 'Core Strength',
        'push_ups': 20,
        'pull_ups': 10,
        'skill_level': 'beginner',
        'medical_conditions': None
    }
]

SAMPLE_EXERCISES = [
    ('Push-ups', 3, '8-12'),
    ('Pull-ups', 3, '5-8'),
    ('Dips', 3, '6-10'),
    ('Handstand Hold', 3, '20-30s'),
    ('Pistol Squats', 3, '6-8 per leg'),
    ('Planche Hold', 3, '10-20s'),
    ('Hollow Body Hold', 3, '30-45s'),
    ('Muscle Up', 3, '3-5'),
    ('Leg Raises', 3, '8-12'),
    ('Chin-ups', 3, '5-8'),
]

def reset_database():
    """Drop and recreate the database with clean schema"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        try:
            # Get database file path if using SQLite
            db_path = None
            if 'sqlite' in SQLALCHEMY_DATABASE_URI:
                db_path = SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    print("[*] Deleting existing database...")
                    os.remove(db_path)
                    print("    Deleted successfully!")
            
            # Create all tables
            print("\n[*] Creating database tables...")
            db.create_all()
            print("    Tables created successfully!")
            
            # Insert sample clients
            print("\n[*] Inserting sample client data...")
            for client_data in SAMPLE_CLIENTS:
                client = Client(
                    name=client_data['name'],
                    goal=client_data['goal'],
                    push_ups=client_data['push_ups'],
                    pull_ups=client_data['pull_ups'],
                    skill_level=client_data['skill_level'],
                    medical_conditions=client_data['medical_conditions']
                )
                db.session.add(client)
            
            db.session.commit()
            print(f"    Inserted {len(SAMPLE_CLIENTS)} clients!")
            
            # Insert sample routines
            print("\n[*] Inserting sample routine data...")
            clients = Client.query.all()
            routine_count = 0
            
            for week in range(1, 3):  # 2 weeks
                for day_num in range(1, 6):  # Monday to Friday
                    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                    day_name = days[day_num - 1]
                    
                    for client in clients:
                        num_exercises = random.randint(2, 4)
                        exercises = random.sample(SAMPLE_EXERCISES, num_exercises)
                        
                        for exercise, sets, reps in exercises:
                            routine = Routine(
                                client_id=client.id,
                                week=week,
                                day=day_name,
                                exercise=exercise,
                                sets=sets,
                                reps=reps,
                                notes=f"Week {week} training"
                            )
                            db.session.add(routine)
                            routine_count += 1
            
            db.session.commit()
            print(f"    Inserted {routine_count} routine entries!")
            
            # Insert sample sessions
            print("\n[*] Inserting sample session data...")
            for client in clients:
                for days_ago in range(0, 10, 2):
                    session_date = datetime.utcnow() - timedelta(days=days_ago)
                    session_data = {
                        'date': session_date.isoformat(),
                        'exercises_completed': random.randint(3, 6),
                        'duration_minutes': random.randint(30, 90),
                        'intensity': random.choice(['low', 'medium', 'high']),
                        'notes': 'Great workout session!'
                    }
                    
                    session = Session(
                        client_id=client.id,
                        session_data=session_data,
                        created_at=session_date
                    )
                    db.session.add(session)
            
            db.session.commit()
            print("    Session data inserted!")
            
            print("\n" + "="*60)
            print("SUCCESS! Database has been reset and populated!")
            print("="*60)
            print(f"Clients: {len(SAMPLE_CLIENTS)}")
            print(f"Routines: {routine_count}")
            print(f"Sessions: {len(clients) * 5}")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    reset_database()
