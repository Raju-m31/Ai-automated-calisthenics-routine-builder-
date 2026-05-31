"""
Database Models for Client Database
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Client(db.Model):
    """Client model for storing client information"""
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    goal = db.Column(db.String(255), nullable=True)
    push_ups = db.Column(db.Integer, nullable=True)
    pull_ups = db.Column(db.Integer, nullable=True)
    skill_level = db.Column(db.String(50), default='beginner')
    medical_conditions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    routines = db.relationship('Routine', backref='client', lazy=True, cascade='all, delete-orphan')
    sessions = db.relationship('Session', backref='client', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'goal': self.goal,
            'push_ups': self.push_ups,
            'pull_ups': self.pull_ups,
            'skill_level': self.skill_level,
            'medical_conditions': self.medical_conditions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Routine(db.Model):
    """Routine model for storing client routines"""
    __tablename__ = 'routines'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    week = db.Column(db.Integer, nullable=False)
    day = db.Column(db.String(50), nullable=False)
    exercise = db.Column(db.String(255), nullable=False)
    sets = db.Column(db.Integer, nullable=True)
    reps = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'week': self.week,
            'day': self.day,
            'exercise': self.exercise,
            'sets': self.sets,
            'reps': self.reps,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Session(db.Model):
    """Session model for storing client session data"""
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    session_data = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'session_data': self.session_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
