from flask import Flask, render_template, request, jsonify, redirect
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import numpy as np
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Parse all Excel sheets and extract client data
def parse_all_client_sheets():
    excel_file = 'Sample Routine .xlsx'
    clients = []
    training_data = {'push_ups': [], 'pull_ups': [], 'level': []}
    
    if os.path.exists(excel_file):
        xls = pd.ExcelFile(excel_file)
        
        for client_idx, sheet_name in enumerate(xls.sheet_names, 1):
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            # Extract client info from sheet
            client_name = sheet_name.strip()
            
            # Try to extract from first column data
            goal = None
            push_ups = None
            pull_ups = None
            skill_level = 'beginner'
            routines = []
            
            # Parse sheet to find: Goal, fitness metrics, and exercises
            for idx, row in df.iterrows():
                row_str = str(row.iloc[0]).lower().strip() if pd.notna(row.iloc[0]) else ''
                
                # Look for goal
                if 'goal' in row_str and pd.notna(row.iloc[1]):
                    goal = str(row.iloc[1]).strip()
                
                # Estimate metrics from sheet data
                if pd.notna(row.iloc[1]) and isinstance(row.iloc[1], (int, float)):
                    if push_ups is None:
                        push_ups = int(row.iloc[1])
                    elif pull_ups is None:
                        pull_ups = int(row.iloc[1])
            
            # Default values if not found
            if push_ups is None:
                push_ups = 10 + (client_idx * 5)
            if pull_ups is None:
                pull_ups = 5 + (client_idx * 2)
            
            # Determine skill level based on reps
            if push_ups >= 40:
                skill_level = 'expert'
            elif push_ups >= 25:
                skill_level = 'advanced'
            elif push_ups >= 15:
                skill_level = 'intermediate'
            else:
                skill_level = 'beginner'
            
            # Create client record
            client = {
                'id': f'client_{str(client_idx).zfill(3)}',
                'name': client_name,
                'goal': goal or 'General Fitness',
                'skill_level': skill_level,
                'push_ups': push_ups,
                'pull_ups': pull_ups,
                'join_date': '2026-01-01',
                'routines': []
            }
            
            clients.append(client)
            training_data['push_ups'].append(push_ups)
            training_data['pull_ups'].append(pull_ups)
            training_data['level'].append(skill_level)
            
            print(f"Parsed {client_name}: {push_ups} push-ups, {pull_ups} pull-ups, {skill_level}")
    
    return clients, training_data

# Parse clients from Excel
print("\n=== Loading Client Data ===")
clients_list, client_training_data = parse_all_client_sheets()
print(f"Total clients loaded: {len(clients_list)}\n")

# Save all clients to JSON
data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)
client_data_file = {'clients': clients_list}
with open(os.path.join(data_dir, 'clients.json'), 'w') as f:
    json.dump(client_data_file, f, indent=2)
print(f"Saved {len(clients_list)} clients to data/clients.json\n")

# Add synthetic data for better model generalization
synthetic_data = {
    'push_ups': [10, 20, 30, 40, 50, 5, 15, 25, 35, 45],
    'pull_ups': [5, 10, 15, 20, 25, 2, 7, 12, 17, 22],
    'level': ['beginner', 'intermediate', 'advanced', 'advanced', 'expert', 'beginner', 'beginner', 'intermediate', 'advanced', 'expert']
}

# Combine client data with synthetic data
for key in ['push_ups', 'pull_ups', 'level']:
    client_training_data[key].extend(synthetic_data[key])

data = client_training_data
df = pd.DataFrame(data)

# Train model with 80/20 split
print("=== Training Model ===")
X = df[['push_ups', 'pull_ups']]
y = df['level']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training set size: {len(X_train)}")
print(f"Test set size: {len(X_test)}")

model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X_train, y_train)

# Evaluate model
train_score = model.score(X_train, y_train)
test_score = model.score(X_test, y_test)

print(f"Training accuracy: {train_score:.2%}")
print(f"Test accuracy: {test_score:.2%}\n")

# Load client data for routes
client_data_file = {'clients': clients_list}

# Goal-specific routine modifications
goal_routines = {
    'handstand': {
        'focus_days': [1, 4],  # Days focusing on handstand
        'key_exercises': ['Handstand Practice', 'Wall Handstand', 'Handstand Push-ups', 'Shoulder Taps'],
        'progression': ['Week 1-2: Wall holds, shoulder taps', 'Week 3-4: Wall handstand 15-20s', 'Week 5-6: Free handstand attempts', 'Week 7-8: Balance hold 30+ seconds']
    },
    'muscle_up': {
        'focus_days': [2, 5],
        'key_exercises': ['Muscle-ups', 'Pull-ups', 'Dips', 'Transition Drills'],
        'progression': ['Week 1-2: Assisted muscle-ups', 'Week 3-4: Transition practice', 'Week 5-6: Explosive pull-ups', 'Week 7-8: Clean muscle-ups']
    },
    'planche': {
        'focus_days': [1, 4],
        'key_exercises': ['Planche Practice', 'Planche Push-ups', 'Hollow Body Hold', 'Tuck Planche'],
        'progression': ['Week 1-2: Tuck hold 10-15s', 'Week 3-4: Straddle hold 10-20s', 'Week 5-6: Full planche attempts', 'Week 7-8: Planche hold 5-10s']
    },
    'front_lever': {
        'focus_days': [2, 4],
        'key_exercises': ['Front Lever Practice', 'Chin-ups', 'Scapular Pull-ups', 'Lever Holds'],
        'progression': ['Week 1-2: Tuck front lever', 'Week 3-4: One-leg front lever', 'Week 5-6: Straddle lever', 'Week 7-8: Full front lever']
    },
    'strength': {
        'focus_days': [1, 2, 3],
        'key_exercises': ['Push-ups', 'Pull-ups', 'Dips', 'Pistol Squats'],
        'progression': ['Week 1-2: Build base strength', 'Week 3-4: Increase volume', 'Week 5-6: Add variations', 'Week 7-8: Progressive overload']
    }
}

# Comprehensive Weekly Calisthenics Routines
weekly_routines = {
    'beginner': {
        'day1': {
            'name': 'Upper Body Push Focus',
            'exercises': [
                {'name': 'Wall Push-ups', 'sets': 3, 'reps': '8-12', 'rest': '60s'},
                {'name': 'Knee Push-ups', 'sets': 3, 'reps': '6-10', 'rest': '60s'},
                {'name': 'Plank', 'sets': 3, 'reps': '20-30s', 'rest': '45s'},
                {'name': 'Wall Sit', 'sets': 3, 'reps': '15-25s', 'rest': '45s'}
            ]
        },
        'day2': {
            'name': 'Lower Body & Core',
            'exercises': [
                {'name': 'Bodyweight Squats', 'sets': 3, 'reps': '10-15', 'rest': '60s'},
                {'name': 'Lunges (each leg)', 'sets': 3, 'reps': '6-8', 'rest': '60s'},
                {'name': 'Glute Bridges', 'sets': 3, 'reps': '10-15', 'rest': '45s'},
                {'name': 'Bicycle Crunches', 'sets': 3, 'reps': '10-15', 'rest': '45s'}
            ]
        },
        'day3': {
            'name': 'Upper Body Pull Focus',
            'exercises': [
                {'name': 'Assisted Pull-ups (or Inverted Rows)', 'sets': 3, 'reps': '5-8', 'rest': '60s'},
                {'name': 'Negative Pull-ups', 'sets': 3, 'reps': '3-5', 'rest': '60s'},
                {'name': 'Superman Holds', 'sets': 3, 'reps': '15-20s', 'rest': '45s'},
                {'name': 'Door Frame Rows', 'sets': 3, 'reps': '8-12', 'rest': '45s'}
            ]
        },
        'day4': {
            'name': 'Full Body Circuit',
            'exercises': [
                {'name': 'Push-ups (knee or wall)', 'sets': 3, 'reps': '6-10', 'rest': '45s'},
                {'name': 'Bodyweight Squats', 'sets': 3, 'reps': '8-12', 'rest': '45s'},
                {'name': 'Plank', 'sets': 3, 'reps': '20-30s', 'rest': '45s'},
                {'name': 'Mountain Climbers', 'sets': 3, 'reps': '10-15', 'rest': '45s'}
            ]
        },
        'day5': {
            'name': 'Active Recovery',
            'exercises': [
                {'name': 'Walking Lunges', 'sets': 3, 'reps': '8-10 each leg', 'rest': '60s'},
                {'name': 'Arm Circles', 'sets': 3, 'reps': '10 each direction', 'rest': '30s'},
                {'name': 'Cat-Cow Stretch', 'sets': 3, 'reps': '8-10', 'rest': '30s'},
                {'name': 'Child\'s Pose', 'sets': 2, 'reps': '30s hold', 'rest': '30s'}
            ]
        },
        'day6': {
            'name': 'Core & Mobility',
            'exercises': [
                {'name': 'Russian Twists', 'sets': 3, 'reps': '10-15 each side', 'rest': '45s'},
                {'name': 'Leg Raises', 'sets': 3, 'reps': '6-10', 'rest': '45s'},
                {'name': 'Bird-Dog', 'sets': 3, 'reps': '8-10 each side', 'rest': '30s'},
                {'name': 'Cobra Stretch', 'sets': 3, 'reps': '20-30s hold', 'rest': '30s'}
            ]
        },
        'day7': {
            'name': 'Rest Day',
            'exercises': [
                {'name': 'Light Walking', 'sets': 1, 'reps': '20-30 minutes', 'rest': 'N/A'},
                {'name': 'Full Body Stretching', 'sets': 1, 'reps': '10-15 minutes', 'rest': 'N/A'}
            ]
        }
    },
    'intermediate': {
        'day1': {
            'name': 'Push Day - Chest & Triceps',
            'exercises': [
                {'name': 'Standard Push-ups', 'sets': 4, 'reps': '8-12', 'rest': '90s'},
                {'name': 'Diamond Push-ups', 'sets': 3, 'reps': '6-10', 'rest': '90s'},
                {'name': 'Archer Push-ups', 'sets': 3, 'reps': '4-6 each side', 'rest': '90s'},
                {'name': 'Tricep Dips (using chair)', 'sets': 3, 'reps': '8-12', 'rest': '75s'}
            ]
        },
        'day2': {
            'name': 'Pull Day - Back & Biceps',
            'exercises': [
                {'name': 'Pull-ups', 'sets': 4, 'reps': '6-10', 'rest': '90s'},
                {'name': 'Wide Grip Pull-ups', 'sets': 3, 'reps': '5-8', 'rest': '90s'},
                {'name': 'Inverted Rows', 'sets': 3, 'reps': '8-12', 'rest': '75s'},
                {'name': 'Chin-ups', 'sets': 3, 'reps': '4-8', 'rest': '90s'}
            ]
        },
        'day3': {
            'name': 'Legs & Core',
            'exercises': [
                {'name': 'Pistol Squats', 'sets': 3, 'reps': '3-5 each leg', 'rest': '120s'},
                {'name': 'Bulgarian Split Squats', 'sets': 3, 'reps': '6-8 each leg', 'rest': '90s'},
                {'name': 'Calf Raises', 'sets': 4, 'reps': '15-20', 'rest': '60s'},
                {'name': 'Hanging Leg Raises', 'sets': 3, 'reps': '8-12', 'rest': '75s'}
            ]
        },
        'day4': {
            'name': 'Upper Body Mixed',
            'exercises': [
                {'name': 'Push-ups', 'sets': 3, 'reps': '10-15', 'rest': '75s'},
                {'name': 'Pull-ups', 'sets': 3, 'reps': '6-10', 'rest': '90s'},
                {'name': 'Dips', 'sets': 3, 'reps': '8-12', 'rest': '75s'},
                {'name': 'Plank', 'sets': 3, 'reps': '45-60s', 'rest': '60s'}
            ]
        },
        'day5': {
            'name': 'Full Body Circuit',
            'exercises': [
                {'name': 'Burpees', 'sets': 3, 'reps': '6-10', 'rest': '90s'},
                {'name': 'Mountain Climbers', 'sets': 3, 'reps': '20-30 each leg', 'rest': '60s'},
                {'name': 'Jump Squats', 'sets': 3, 'reps': '8-12', 'rest': '75s'},
                {'name': 'Superman to Push-up', 'sets': 3, 'reps': '6-8', 'rest': '90s'}
            ]
        },
        'day6': {
            'name': 'Core & Conditioning',
            'exercises': [
                {'name': 'Dragon Flags', 'sets': 3, 'reps': '3-5', 'rest': '120s'},
                {'name': 'L-Sit', 'sets': 3, 'reps': '10-20s', 'rest': '90s'},
                {'name': 'Russian Twists', 'sets': 3, 'reps': '15-20 each side', 'rest': '60s'},
                {'name': 'Flutter Kicks', 'sets': 3, 'reps': '20-30', 'rest': '45s'}
            ]
        },
        'day7': {
            'name': 'Active Recovery',
            'exercises': [
                {'name': 'Yoga Flow', 'sets': 1, 'reps': '20 minutes', 'rest': 'N/A'},
                {'name': 'Mobility Work', 'sets': 1, 'reps': '15 minutes', 'rest': 'N/A'},
                {'name': 'Light Cardio', 'sets': 1, 'reps': '20 minutes', 'rest': 'N/A'}
            ]
        }
    },
    'advanced': {
        'day1': {
            'name': 'Push Power Day',
            'exercises': [
                {'name': 'One-Arm Push-ups', 'sets': 4, 'reps': '3-5 each arm', 'rest': '120s'},
                {'name': 'Planche Push-ups', 'sets': 3, 'reps': '3-6', 'rest': '120s'},
                {'name': 'Archer Push-ups', 'sets': 3, 'reps': '6-8 each side', 'rest': '90s'},
                {'name': 'Handstand Push-ups', 'sets': 3, 'reps': '3-5', 'rest': '120s'}
            ]
        },
        'day2': {
            'name': 'Pull Power Day',
            'exercises': [
                {'name': 'Muscle-ups', 'sets': 4, 'reps': '3-6', 'rest': '120s'},
                {'name': 'Front Lever Pull-ups', 'sets': 3, 'reps': '3-5', 'rest': '120s'},
                {'name': 'One-Arm Pull-ups', 'sets': 3, 'reps': '1-3 each arm', 'rest': '150s'},
                {'name': 'Typewriter Pull-ups', 'sets': 3, 'reps': '2-4 each side', 'rest': '120s'}
            ]
        },
        'day3': {
            'name': 'Legs & Core Power',
            'exercises': [
                {'name': 'Pistol Squats', 'sets': 4, 'reps': '6-8 each leg', 'rest': '90s'},
                {'name': 'Shrimp Squats', 'sets': 3, 'reps': '4-6 each leg', 'rest': '120s'},
                {'name': 'Dragon Flags', 'sets': 4, 'reps': '6-8', 'rest': '90s'},
                {'name': 'V-Ups', 'sets': 3, 'reps': '8-12', 'rest': '75s'}
            ]
        },
        'day4': {
            'name': 'Skill Work',
            'exercises': [
                {'name': 'Planche Practice', 'sets': 4, 'reps': '20-45s holds', 'rest': '90s'},
                {'name': 'Front Lever Practice', 'sets': 4, 'reps': '15-30s holds', 'rest': '90s'},
                {'name': 'Handstand Practice', 'sets': 3, 'reps': '30-60s', 'rest': '60s'},
                {'name': 'L-Sit', 'sets': 3, 'reps': '20-45s', 'rest': '75s'}
            ]
        },
        'day5': {
            'name': 'Strength Circuit',
            'exercises': [
                {'name': 'Push-ups to Muscle-up', 'sets': 3, 'reps': '3-5', 'rest': '150s'},
                {'name': 'Pistol to One-Legged Push-up', 'sets': 3, 'reps': '2-4 each side', 'rest': '120s'},
                {'name': 'Human Flag Attempts', 'sets': 3, 'reps': '5-10s holds', 'rest': '90s'},
                {'name': 'Manna (Planche to Handstand)', 'sets': 3, 'reps': '2-4', 'rest': '150s'}
            ]
        },
        'day6': {
            'name': 'Conditioning & Core',
            'exercises': [
                {'name': 'Burpee Muscle-ups', 'sets': 3, 'reps': '3-5', 'rest': '120s'},
                {'name': 'Running Man', 'sets': 3, 'reps': '10-15 each leg', 'rest': '90s'},
                {'name': 'Hollow Body Rock', 'sets': 4, 'reps': '15-25s', 'rest': '60s'},
                {'name': 'Superman to Plank', 'sets': 3, 'reps': '8-12', 'rest': '75s'}
            ]
        },
        'day7': {
            'name': 'Recovery & Mobility',
            'exercises': [
                {'name': 'Deep Tissue Massage', 'sets': 1, 'reps': '20 minutes', 'rest': 'N/A'},
                {'name': 'Yoga & Stretching', 'sets': 1, 'reps': '30 minutes', 'rest': 'N/A'},
                {'name': 'Foam Rolling', 'sets': 1, 'reps': '15 minutes', 'rest': 'N/A'},
                {'name': 'Meditation', 'sets': 1, 'reps': '10 minutes', 'rest': 'N/A'}
            ]
        }
    },
    'expert': {
        'day1': {
            'name': 'Elite Push Mastery',
            'exercises': [
                {'name': 'One-Arm Planche Push-ups', 'sets': 4, 'reps': '2-4 each arm', 'rest': '180s'},
                {'name': 'Manna to Handstand Push-up', 'sets': 3, 'reps': '1-3', 'rest': '180s'},
                {'name': 'One-Arm Handstand Push-ups', 'sets': 3, 'reps': '1-2 each arm', 'rest': '180s'},
                {'name': 'Planche Levers', 'sets': 4, 'reps': '10-20s', 'rest': '120s'}
            ]
        },
        'day2': {
            'name': 'Elite Pull Mastery',
            'exercises': [
                {'name': 'One-Arm Muscle-ups', 'sets': 4, 'reps': '1-3 each arm', 'rest': '180s'},
                {'name': 'Hesse (One-arm Front Lever)', 'sets': 3, 'reps': '5-10s each arm', 'rest': '150s'},
                {'name': 'Barspin to Muscle-up', 'sets': 3, 'reps': '1-2', 'rest': '180s'},
                {'name': 'Victorian Cross', 'sets': 3, 'reps': '3-5s hold', 'rest': '120s'}
            ]
        },
        'day3': {
            'name': 'Elite Legs & Core',
            'exercises': [
                {'name': 'One-Legged Pistol Squats', 'sets': 4, 'reps': '8-12 each leg', 'rest': '90s'},
                {'name': 'Triple Clap Push-ups', 'sets': 3, 'reps': '3-5', 'rest': '120s'},
                {'name': 'Full Dragon Flag', 'sets': 4, 'reps': '8-12', 'rest': '90s'},
                {'name': 'Inverted Cross (Human Flag)', 'sets': 3, 'reps': '10-20s', 'rest': '150s'}
            ]
        },
        'day4': {
            'name': 'Skill Mastery',
            'exercises': [
                {'name': 'Full Planche', 'sets': 5, 'reps': '15-30s holds', 'rest': '120s'},
                {'name': 'Straddle Planche', 'sets': 4, 'reps': '10-20s holds', 'rest': '120s'},
                {'name': 'Full Front Lever', 'sets': 4, 'reps': '15-25s holds', 'rest': '120s'},
                {'name': 'One-Arm Handstand', 'sets': 3, 'reps': '5-15s each arm', 'rest': '150s'}
            ]
        },
        'day5': {
            'name': 'Power & Explosion',
            'exercises': [
                {'name': 'Clap Muscle-ups', 'sets': 4, 'reps': '2-4', 'rest': '150s'},
                {'name': '360 Muscle-ups', 'sets': 3, 'reps': '1-2', 'rest': '180s'},
                {'name': 'Kong to Inverted Cross', 'sets': 3, 'reps': '2-4', 'rest': '150s'},
                {'name': 'Triple Clap Planche Push-ups', 'sets': 3, 'reps': '1-3', 'rest': '180s'}
            ]
        },
        'day6': {
            'name': 'Conditioning Elite',
            'exercises': [
                {'name': 'Muscle-up Burpees', 'sets': 4, 'reps': '5-8', 'rest': '120s'},
                {'name': 'Planche to Handstand Walk', 'sets': 3, 'reps': '3-5 steps', 'rest': '150s'},
                {'name': 'Hollow Body to Superman', 'sets': 4, 'reps': '15-25', 'rest': '75s'},
                {'name': 'Running Man to One-Arm Push-up', 'sets': 3, 'reps': '3-5 each arm', 'rest': '150s'}
            ]
        },
        'day7': {
            'name': 'Elite Recovery',
            'exercises': [
                {'name': 'Sports Massage', 'sets': 1, 'reps': '45 minutes', 'rest': 'N/A'},
                {'name': 'Advanced Yoga', 'sets': 1, 'reps': '45 minutes', 'rest': 'N/A'},
                {'name': 'Cryotherapy/Ice Bath', 'sets': 1, 'reps': '3-5 minutes', 'rest': 'N/A'},
                {'name': 'Nutrition & Supplementation', 'sets': 1, 'reps': 'Review daily intake', 'rest': 'N/A'}
            ]
        }
    }
}

# Medical alternatives
medical_alternatives = {
    'shoulder_injury': {
        'modifications': 'Avoid overhead pressing, focus on horizontal pushes',
        'alternatives': ['Wall push-ups only', 'Floor press variations', 'Avoid pull-ups, use rows']
    },
    'back_injury': {
        'modifications': 'No spinal loading, focus on controlled movements',
        'alternatives': ['Knee push-ups', 'Assisted variations only', 'Avoid hollow body positions']
    },
    'wrist_injury': {
        'modifications': 'Minimize wrist pressure, use fist or palm support',
        'alternatives': ['Wall push-ups', 'Lat pulldown alternatives', 'Avoid plank positions']
    },
    'knee_injury': {
        'modifications': 'No deep knee flexion, focus on upper body',
        'alternatives': ['Wall sits only', 'Avoid squats and lunges', 'Focus on core and upper body']
    },
    'elbow_injury': {
        'modifications': 'Avoid elbow extension, focus on pulling movements',
        'alternatives': ['Avoid dips and push-ups', 'Pull-up variations', 'Focus on core work']
    },
    'neck_injury': {
        'modifications': 'Avoid head positioning stress, maintain neutral spine',
        'alternatives': ['Avoid handstands', 'Controlled movements only', 'Focus on horizontal work']
    }
}

# Optional Hugging Face LLM analysis
import os
import requests
HF_MODEL_URL = 'https://api-inference.huggingface.co/models/google/flan-t5-small'
HF_API_TOKEN = os.getenv('HF_API_TOKEN', '').strip()

def llm_medical_analysis(reason):
    if not HF_API_TOKEN:
        return None
    headers = {
        'Authorization': f'Bearer {HF_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    prompt = (
        "Read this client medical note and classify the primary issue category (shoulder_injury, back_injury, wrist_injury, core_issue, none). "
        "Then write a short safety summary.\nNote: return format exactly: issue: <category>; summary: <text>.\n"
        f"Client note: {reason}"
    )
    try:
        response = requests.post(HF_MODEL_URL, headers=headers, json={"inputs": prompt, "parameters": {"max_new_tokens": 120}} , timeout=20)
        if response.status_code != 200:
            return None
        output = response.json()
        if isinstance(output, dict) and 'error' in output:
            return None
        text = ''
        if isinstance(output, list):
            text = output[0].get('generated_text', '')
        elif isinstance(output, dict):
            text = output.get('generated_text', '')
        text = text.lower()
        issue = 'none'
        if 'shoulder_injury' in text or 'shoulder' in text:
            issue = 'shoulder_injury'
        elif 'back_injury' in text or 'back' in text:
            issue = 'back_injury'
        elif 'wrist_injury' in text or 'wrist' in text:
            issue = 'wrist_injury'
        elif 'core_issue' in text or 'core' in text or 'abdomen' in text:
            issue = 'core_issue'
        summary = ''
        if 'summary:' in text:
            summary = text.split('summary:')[-1].strip()
        else:
            summary = 'Medical note analyzed by LLM. Please verify.'
        return {'issue': issue if issue != 'none' else '', 'summary': summary}
    except Exception:
        return None

# Local fallback analysis

def analyze_medical_reason(text):
    text_lower = text.lower()
    if 'shoulder' in text_lower:
        return {
            'issue': 'shoulder_injury',
            'summary': 'Shoulder-related limitation detected. Use lower-load push variations and avoid overhead pull motions.'
        }
    if 'back' in text_lower:
        return {
            'issue': 'back_injury',
            'summary': 'Back-related limitation detected. Favor knee push and assisted pull motions.'
        }
    if 'wrist' in text_lower:
        return {
            'issue': 'wrist_injury',
            'summary': 'Wrist-related limitation detected. Use wall push-ups and avoid heavy wrist loading.'
        }
    if 'abdomen' in text_lower or 'core' in text_lower:
        return {
            'issue': 'core_issue',
            'summary': 'Core/abdomen concerns detected. Keep load low and focus on controlled core stability.'
        }
    return {
        'issue': '',
        'summary': 'Custom reason received. Use conservative progression and trainer review.'
    }

@app.route('/')
def home():
    llm_status = 'ON' if HF_API_TOKEN else 'OFF (optional token missing)'
    return render_template('index.html', llm_status=llm_status)

@app.route('/client/<client_id>')
def get_client_routine(client_id):
    """Get routine for a specific client"""
    for client in client_data_file.get('clients', []):
        if client.get('id') == client_id:
            return jsonify(client)
    return jsonify({'error': 'Client not found'}), 404

@app.route('/clients')
def list_clients():
    """List all available clients"""
    clients_list = []
    for client in client_data_file.get('clients', []):
        clients_list.append({
            'id': client.get('id'),
            'name': client.get('name'),
            'goal': client.get('goal'),
            'skill_level': client.get('skill_level')
        })
    return jsonify(clients_list)

@app.route('/generate', methods=['POST'])
def generate():
    push_ups = int(request.form['push_ups'])
    pull_ups = int(request.form['pull_ups'])
    goal = request.form.get('goal', 'general').lower()
    goal_details = request.form.get('goal_details', '').strip()
    medical = request.form.get('medical', '')
    manual_reason = request.form.get('manual_reason', '').strip()

    # Predict level
    level = model.predict([[push_ups, pull_ups]])[0]

    medical_summary = ''
    chosen_issue = medical
    modifications = []

    # If trainer enters manual medical reason, call LLM analysis first (if available), else local
    if manual_reason:
        analysis = None
        if HF_API_TOKEN:
            analysis = llm_medical_analysis(manual_reason)
        if not analysis:
            analysis = analyze_medical_reason(manual_reason)
        chosen_issue = analysis.get('issue', '') or chosen_issue
        medical_summary = analysis.get('summary', '')

    # If no manual reason but selected condition, use that
    if not medical_summary and medical in medical_alternatives:
        chosen_issue = medical
        alt = medical_alternatives[chosen_issue]
        medical_summary = alt.get('modifications', 'Using safe alternatives for selected condition.')
        modifications = alt.get('alternatives', [])

    # Get the weekly routine for this level
    routine = weekly_routines.get(level, weekly_routines['beginner'])

    # Apply medical modifications if needed
    if chosen_issue and chosen_issue in medical_alternatives:
        pass

    # Generate the 7-day routine
    weekly_plan = []
    for day in range(1, 8):
        day_key = f'day{day}'
        if day_key in routine:
            day_data = routine[day_key].copy()
            # Add medical warnings if applicable
            if modifications:
                day_data['medical_warnings'] = modifications
            weekly_plan.append(day_data)

    # Get goal-specific progression tips
    progression_tips = goal_routines.get(goal, {}).get('progression', [
        "Week 1-2: Focus on form and consistency",
        "Week 3-4: Increase reps or add variations",
        "Week 5-6: Add weight or resistance bands",
        "Week 7-8: Combine movements or increase intensity"
    ])

    # Create goal tracking session (store in server session)
    import uuid
    from datetime import datetime, timedelta
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
        'completed_weeks': 0
    }
    
    # Store goal session (in production, use database)
    os.makedirs('data/sessions', exist_ok=True)
    session_file = f'data/sessions/{goal_session_id}.json'
    with open(session_file, 'w') as f:
        json.dump(goal_data, f, indent=2)

    return render_template('result.html',
                         weekly_plan=weekly_plan,
                         level=level,
                         medical_summary=medical_summary,
                         manual_reason=manual_reason,
                         progression_tips=progression_tips,
                         push_ups=push_ups,
                         pull_ups=pull_ups,
                         goal=goal,
                         goal_details=goal_details,
                         goal_session_id=goal_session_id)

@app.route('/review-goal/<goal_session_id>', methods=['GET', 'POST'])
def review_goal(goal_session_id):
    """Review and adjust goal after 4 weeks"""
    session_file = f'data/sessions/{goal_session_id}.json'
    
    if not os.path.exists(session_file):
        return jsonify({'error': 'Goal session not found'}), 404
    
    with open(session_file, 'r') as f:
        goal_data = json.load(f)
    
    if request.method == 'POST':
        # User updating goal or continuing with same goal
        action = request.form.get('action')  # 'continue' or 'change'
        new_goal = request.form.get('new_goal', goal_data['goal']) if action == 'change' else goal_data['goal']
        new_details = request.form.get('new_details', goal_data['goal_details']) if action == 'change' else goal_data['goal_details']
        
        # Update goal data
        goal_data['goal'] = new_goal
        goal_data['goal_details'] = new_details
        goal_data['completed_weeks'] = (goal_data.get('completed_weeks', 0) + 4)
        goal_data['last_review'] = datetime.now().isoformat()
        
        # If continuing, generate new routine with same goal
        # If changing, redirect to home to start new routine
        with open(session_file, 'w') as f:
            json.dump(goal_data, f, indent=2)
        
        if action == 'change':
            return redirect('/')
        else:
            # Generate updated routine for continued goal
            return redirect(f'/generate-updated/{goal_session_id}')
    
    # Show review page
    from datetime import datetime, timedelta
    start_date = datetime.fromisoformat(goal_data['start_date'])
    review_date = start_date + timedelta(days=28)
    
    return render_template('goal-review.html',
                         goal_data=goal_data,
                         review_date=review_date.strftime('%B %d, %Y'),
                         weeks_completed=goal_data.get('completed_weeks', 0) + 4)

@app.route('/goal-status/<goal_session_id>')
def goal_status(goal_session_id):
    """Get goal status as JSON"""
    session_file = f'data/sessions/{goal_session_id}.json'
    
    if not os.path.exists(session_file):
        return jsonify({'error': 'Goal session not found'}), 404
    
    with open(session_file, 'r') as f:
        goal_data = json.load(f)
    
    from datetime import datetime
    start_date = datetime.fromisoformat(goal_data['start_date'])
    current_week = (datetime.now() - start_date).days // 7 + 1
    
    return jsonify({
        'goal': goal_data['goal'],
        'goal_details': goal_data['goal_details'],
        'current_week': min(current_week, 4),
        'weeks_completed': goal_data.get('completed_weeks', 0),
        'time_until_review': max(0, 28 - (datetime.now() - start_date).days)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)