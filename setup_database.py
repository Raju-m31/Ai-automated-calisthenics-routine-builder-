"""
Database setup and Excel import script
Run this script to initialize the database and import data from Excel
"""
import os
import sys
import pandas as pd
from config import SQLALCHEMY_DATABASE_URI, MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
from models import db, Client, Routine, Session
import mysql.connector
from mysql.connector import Error

def create_database():
    """Create MySQL database if it doesn't exist"""
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        print(f"✓ Database '{MYSQL_DATABASE}' created/verified successfully!")
        cursor.close()
        connection.close()
    except Error as e:
        print(f"✗ Error creating database: {e}")
        print("\nPlease ensure MySQL is running and update config.py with correct credentials:")
        print("  - MYSQL_HOST: localhost")
        print("  - MYSQL_USER: your_username")
        print("  - MYSQL_PASSWORD: your_password")
        sys.exit(1)


def init_tables(app):
    """Initialize database tables"""
    try:
        with app.app_context():
            db.create_all()
            print("✓ Database tables created successfully!")
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        sys.exit(1)


def import_excel_data(app, excel_file='Sample Routine .xlsx'):
    """Import client data from Excel file"""
    if not os.path.exists(excel_file):
        print(f"✗ Excel file '{excel_file}' not found!")
        return
    
    try:
        with app.app_context():
            xls = pd.ExcelFile(excel_file)
            
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Check if client already exists
                existing_client = Client.query.filter_by(name=sheet_name.strip()).first()
                if existing_client:
                    print(f"  ⊘ Client '{sheet_name}' already exists, skipping...")
                    continue
                
                # Extract client data from the sheet
                client_name = sheet_name.strip()
                goal = None
                push_ups = None
                pull_ups = None
                skill_level = 'beginner'
                
                # Parse sheet to extract data
                for idx, row in df.iterrows():
                    row_str = str(row.iloc[0]).lower().strip() if pd.notna(row.iloc[0]) else ''
                    
                    # Look for goal
                    if 'goal' in row_str and len(row) > 1 and pd.notna(row.iloc[1]):
                        goal = str(row.iloc[1]).strip()
                    
                    # Extract numeric values
                    if len(row) > 1 and pd.notna(row.iloc[1]) and isinstance(row.iloc[1], (int, float)):
                        if push_ups is None and row.iloc[1] > 0:
                            push_ups = int(row.iloc[1])
                        elif pull_ups is None and row.iloc[1] > 0 and push_ups is not None:
                            pull_ups = int(row.iloc[1])
                
                # Set defaults
                if push_ups is None:
                    push_ups = 0
                if pull_ups is None:
                    pull_ups = 0
                
                # Create and save client
                client = Client(
                    name=client_name,
                    goal=goal or 'General Fitness',
                    push_ups=push_ups,
                    pull_ups=pull_ups,
                    skill_level=skill_level
                )
                db.session.add(client)
                print(f"  ✓ Added client: {client_name}")
            
            db.session.commit()
            print(f"\n✓ Excel data imported successfully!")
            
    except Exception as e:
        print(f"✗ Error importing Excel data: {e}")
        db.session.rollback()


def main():
    """Main setup function"""
    print("=" * 50)
    print("CLIENT DATABASE SETUP")
    print("=" * 50)
    
    # Step 1: Create database
    print("\n[1/3] Creating database...")
    create_database()
    
    # Step 2: Initialize Flask app and create tables
    print("\n[2/3] Creating database tables...")
    from flask import Flask
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    init_tables(app)
    
    # Step 3: Import Excel data
    print("\n[3/3] Importing Excel data...")
    import_excel_data(app)
    
    print("\n" + "=" * 50)
    print("✓ SETUP COMPLETE!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Update config.py with your MySQL credentials if needed")
    print("2. Run: python app.py")
    print("3. Open http://localhost:5000 in your browser")
    print("\nTo view the database tables, visit /database in your browser")


if __name__ == '__main__':
    main()
