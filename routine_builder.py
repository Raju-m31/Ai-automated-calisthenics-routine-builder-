"""
Routine Builder - Parse Excel sheets and generate proper 7-day routines
"""
import pandas as pd
import json
from collections import defaultdict

def parse_excel_routines(excel_file='Sample Routine .xlsx'):
    """Parse routine data from Excel file"""
    try:
        xls = pd.ExcelFile(excel_file)
        routines_by_level = defaultdict(list)
        all_routines = {}
        
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            # Parse routine from sheet
            routine = parse_sheet(df, sheet_name)
            if routine and routine.get('exercises'):
                all_routines[sheet_name] = routine
                level = routine.get('level', 'intermediate')
                routines_by_level[level].append(routine)
        
        return all_routines, dict(routines_by_level)
    except Exception as e:
        print(f"Error parsing Excel: {e}")
        return {}, {}

def parse_sheet(df, sheet_name):
    """Parse individual sheet into routine"""
    routine = {
        'name': sheet_name.strip(),
        'goal': '',
        'level': 'intermediate',
        'exercises': {}
    }
    
    # Parse the sheet
    df = df.fillna('')
    rows = df.values.tolist()
    
    current_day = None
    current_exercises = []
    
    for i, row in enumerate(rows):
        row_str = ' '.join([str(cell).strip() for cell in row if cell])
        row_str = row_str.lower().strip()
        
        # Look for goal
        if 'goal' in row_str and i + 1 < len(rows):
            next_row = ' '.join([str(cell).strip() for cell in rows[i+1] if cell])
            routine['goal'] = next_row.strip()
        
        # Look for day markers (Day 1, Day 2, etc.)
        if row_str.startswith('day'):
            if current_day and current_exercises:
                routine['exercises'][current_day] = current_exercises
            
            # Extract day number
            for j in range(1, 8):
                if f'day {j}' in row_str or f'day{j}' in row_str:
                    current_day = f'day{j}'
                    current_exercises = []
                    break
        elif current_day and row_str and not row_str.isspace():
            # Extract exercise (check for sets and reps pattern)
            current_exercises.append(row_str)
    
    # Add last day
    if current_day and current_exercises:
        routine['exercises'][current_day] = current_exercises
    
    # Determine skill level from exercises and goal
    routine['level'] = determine_level(routine)
    
    return routine if routine['exercises'] else None

def determine_level(routine):
    """Determine skill level based on exercises"""
    exercises_str = ' '.join([str(e) for exs in routine['exercises'].values() for e in exs]).lower()
    goal_str = routine['goal'].lower()
    
    advanced_keywords = ['handstand', 'planche', 'one-arm', 'muscle up', 'lever']
    intermediate_keywords = ['pull', 'push', 'progression', 'holds']
    
    if any(keyword in exercises_str or keyword in goal_str for keyword in advanced_keywords):
        return 'advanced'
    elif any(keyword in exercises_str or keyword in goal_str for keyword in intermediate_keywords):
        return 'intermediate'
    else:
        return 'beginner'

def generate_7day_routine(routine_template):
    """Generate a complete 7-day routine"""
    seven_day = {}
    
    # Use provided days or fill with defaults
    provided_days = routine_template.get('exercises', {})
    
    for day_num in range(1, 8):
        day_key = f'day{day_num}'
        if day_key in provided_days:
            exercises = provided_days[day_key]
        else:
            # Use rest day or similar exercises from other days
            if day_num % 2 == 0:
                exercises = ['Rest day - Recovery and stretching']
            else:
                # Cycle through available exercises
                all_exercises = []
                for exs in provided_days.values():
                    all_exercises.extend(exs)
                if all_exercises:
                    idx = (day_num - 1) % len(all_exercises)
                    exercises = [all_exercises[idx]]
                else:
                    exercises = ['General training']
        
        seven_day[day_key] = {
            'name': f"Day {day_num}",
            'exercises': parse_exercises(exercises),
            'rest': '90s'
        }
    
    return seven_day

def parse_exercises(exercise_list):
    """Parse exercise strings into structured format"""
    parsed = []
    
    for exercise in exercise_list:
        exercise = str(exercise).strip()
        if not exercise:
            continue
        
        # Try to extract sets and reps (e.g., "3×10", "3x10", "3 × 10")
        sets = 3
        reps = '10'
        
        if '×' in exercise or 'x' in exercise.lower():
            parts = exercise.replace('×', 'x').lower().split('x')
            if len(parts) >= 2:
                try:
                    sets = int(parts[0].strip())
                    reps = parts[1].strip().split()[0]
                except:
                    pass
        
        # Extract exercise name (remove set/rep info)
        name = exercise.split('×')[0].split('x')[0].strip() if '×' in exercise or 'x' in exercise.lower() else exercise
        name = ' '.join(name.split())
        
        parsed.append({
            'name': name,
            'sets': sets,
            'reps': reps,
            'rest': '60s'
        })
    
    return parsed

def create_4week_progression(seven_day_routine):
    """Create a 4-week progression from 7-day routine"""
    progression = []
    
    for week in range(1, 5):
        week_routine = []
        for day_num in range(1, 8):
            day_key = f'day{day_num}'
            if day_key in seven_day_routine:
                day_data = seven_day_routine[day_key].copy()
                day_data['week'] = week
                
                # Increase difficulty each week
                if week > 1:
                    day_data['exercises'] = increase_difficulty(day_data['exercises'], week)
                
                week_routine.append(day_data)
        
        progression.append(week_routine)
    
    return progression

def increase_difficulty(exercises, week):
    """Increase difficulty of exercises for each week"""
    increased = []
    for exercise in exercises:
        new_exercise = exercise.copy()
        
        # Increase sets or reps based on week
        if week == 2:
            new_exercise['reps'] = str(int(new_exercise['reps']) + 2) if new_exercise['reps'].isdigit() else new_exercise['reps']
        elif week == 3:
            new_exercise['sets'] = new_exercise['sets'] + 1
        elif week == 4:
            new_exercise['reps'] = str(int(new_exercise['reps']) + 5) if new_exercise['reps'].isdigit() else new_exercise['reps']
        
        increased.append(new_exercise)
    
    return increased

def build_level_routines():
    """Build comprehensive routines for each level"""
    # Parse Excel
    all_routines, by_level = parse_excel_routines()
    
    # Group by level
    level_routines = {
        'beginner': [],
        'intermediate': [],
        'advanced': [],
        'expert': []
    }
    
    for routine in all_routines.values():
        level = routine['level']
        seven_day = generate_7day_routine(routine)
        four_week = create_4week_progression(seven_day)
        
        level_routines[level].append({
            'name': routine['name'],
            'goal': routine['goal'],
            'seven_day': seven_day,
            'four_week': four_week
        })
    
    # Add backup routines if levels are empty
    for level in ['beginner', 'intermediate', 'advanced', 'expert']:
        if not level_routines[level]:
            level_routines[level] = [create_default_routine(level)]
    
    return level_routines

def create_default_routine(level):
    """Create default routine for each level"""
    defaults = {
        'beginner': {
            'name': 'Beginner Foundation',
            'goal': 'Build basic strength and endurance',
            'exercises': {
                'day1': ['Wall push-ups 3×8', 'Plank 3×20s', 'Knee pull-ups 3×5'],
                'day2': ['rest - stretching'],
                'day3': ['Incline push-ups 3×10', 'Scapular pull-ups 3×8', 'Wall sit 3×20s'],
                'day4': ['rest - mobility'],
                'day5': ['Push-ups 3×5', 'Dead hang 3×15s', 'Dips assistance 3×5'],
                'day6': ['rest - recovery'],
                'day7': ['Full body light session']
            }
        },
        'intermediate': {
            'name': 'Intermediate Push-Pull',
            'goal': 'Develop muscle endurance and control',
            'exercises': {
                'day1': ['Push-ups 4×10', 'Pull-ups 4×5', 'Dips 4×5'],
                'day2': ['rest'],
                'day3': ['Handstand hold 3×30s', 'Pistol squat practice 3×5', 'Pike push-ups 4×8'],
                'day4': ['rest'],
                'day5': ['Muscle-up progression 4×3', 'L-sit hold 3×15s', 'Clap push-ups 3×5'],
                'day6': ['rest'],
                'day7': ['Skill work and conditioning']
            }
        },
        'advanced': {
            'name': 'Advanced Skills',
            'goal': 'Master advanced calisthenics movements',
            'exercises': {
                'day1': ['Handstand push-ups 4×5', 'Front lever progression 3×20s', 'One-arm pull-up progression 4×3'],
                'day2': ['rest'],
                'day3': ['Planche progression 3×15s', 'Muscle-up practice 5×2', 'Human flag hold 3×10s'],
                'day4': ['rest'],
                'day5': ['Handstand walk practice 5×10m', 'Back lever progression 3×10s', 'Advanced L-sit 3×20s'],
                'day6': ['rest'],
                'day7': ['Skill refinement and testing']
            }
        },
        'expert': {
            'name': 'Elite Mastery',
            'goal': 'Perfect elite movements and combinations',
            'exercises': {
                'day1': ['One-arm push-ups 5×3', 'One-arm pull-ups 5×2', 'Planche lean 4×30s'],
                'day2': ['rest'],
                'day3': ['Front lever 4×20s', 'Back lever 4×15s', 'Handstand walk 5×20m'],
                'day4': ['rest'],
                'day5': ['Human flag 4×15s', 'Muscle-up combo 5×3', 'V-sit progression 4×20s'],
                'day6': ['rest'],
                'day7': ['Competition simulation']
            }
        }
    }
    
    default = defaults[level]
    seven_day = generate_7day_routine(default)
    four_week = create_4week_progression(seven_day)
    
    return {
        'name': default['name'],
        'goal': default['goal'],
        'seven_day': seven_day,
        'four_week': four_week
    }

if __name__ == '__main__':
    routines = build_level_routines()
    print("Routines built successfully!")
    for level, routs in routines.items():
        print(f"\n{level.upper()}: {len(routs)} routines")
        for r in routs:
            print(f"  - {r['name']}: {r['goal']}")
