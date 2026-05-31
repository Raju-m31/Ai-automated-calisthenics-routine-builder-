# Database Setup Guide - Calibaf Studio

## Prerequisites

You need MySQL Server installed on your system. Follow these steps to set up the MySQL database.

### 1. Install MySQL Server

**Windows:**
- Download MySQL from: https://dev.mysql.com/downloads/mysql/
- Run the installer and follow the setup wizard
- Remember the root password you set
- Default port is 3306

**macOS:**
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo mysql_secure_installation
```

---

## Setup Steps

### Step 1: Update Configuration

Edit `config.py` in your project root with your MySQL credentials:

```python
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'your_password_here'  # <-- Set your MySQL password
MYSQL_DATABASE = 'client_database'
MYSQL_PORT = 3306
```

### Step 2: Install Dependencies

All required packages are already in `requirements.txt`:
- Flask-SQLAlchemy
- mysql-connector-python
- pandas
- scikit-learn

They should be installed from the initial setup, but if not:

```bash
pip install -r requirements.txt
```

### Step 3: Run Database Setup Script

Execute the setup script to:
1. Create the database
2. Create all tables
3. Import data from your Excel file

```bash
python setup_database.py
```

You should see output like:
```
==================================================
CLIENT DATABASE SETUP
==================================================

[1/3] Creating database...
[OK] Database 'client_database' created/verified successfully!

[2/3] Creating database tables...
[OK] Database tables created successfully!

[3/3] Importing Excel data...
  [OK] Added client: Client Name 1
  [OK] Added client: Client Name 2
  ...

==================================================
[OK] SETUP COMPLETE!
==================================================
```

### Step 4: Start the Application

```bash
python app.py
```

The app will start at `http://localhost:5000`

### Step 5: Access the Database Interface

Open your browser and go to:
- **Home**: http://localhost:5000
- **Database View**: http://localhost:5000/database

---

## Database Structure

The system creates three main tables:

### clients
| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Auto-increment client ID |
| name | String | Client name (unique) |
| goal | String | Fitness goal |
| push_ups | Integer | Max push-ups |
| pull_ups | Integer | Max pull-ups |
| skill_level | String | beginner/intermediate/advanced/expert |
| medical_conditions | Text | Any medical limitations |
| created_at | DateTime | Account creation date |
| updated_at | DateTime | Last update date |

### routines
| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Auto-increment routine ID |
| client_id | Integer (FK) | Links to clients.id |
| week | Integer | Week number (1-4) |
| day | String | Day of week |
| exercise | String | Exercise name |
| sets | Integer | Number of sets |
| reps | String | Reps range (e.g., "8-12") |
| notes | Text | Additional notes |
| created_at | DateTime | Creation date |

### sessions
| Column | Type | Description |
|--------|------|-------------|
| id | Integer (PK) | Auto-increment session ID |
| client_id | Integer (FK) | Links to clients.id |
| session_data | JSON | Routine data in JSON format |
| created_at | DateTime | Creation date |

---

## Features

### Database Interface (`/database`)
- **View all clients** in a professional table layout
- **Add new clients** with modal form
- **Edit client information**
- **Delete clients** 
- **Search and filter** by name, goal, or skill level
- **Export data** to CSV
- **View statistics** (total clients, averages, top skill level)

### API Endpoints

**Get all clients:**
```
GET /api/clients
```

**Get single client:**
```
GET /api/client/<id>
```

**Create client:**
```
POST /api/client
Content-Type: application/json
{
  "name": "John Doe",
  "goal": "Handstand",
  "push_ups": 25,
  "pull_ups": 10,
  "skill_level": "intermediate",
  "medical_conditions": "None"
}
```

**Update client:**
```
PUT /api/client/<id>
Content-Type: application/json
{
  "push_ups": 30,
  "skill_level": "advanced"
}
```

**Delete client:**
```
DELETE /api/client/<id>
```

---

## Troubleshooting

### Error: "Connection refused"
- **Cause**: MySQL server is not running
- **Solution**: Start MySQL service
  - Windows: Services > MySQL
  - macOS: `brew services start mysql`
  - Linux: `sudo systemctl start mysql`

### Error: "Access denied for user"
- **Cause**: Wrong MySQL credentials
- **Solution**: Update `config.py` with correct username and password

### Error: "Database doesn't exist"
- **Cause**: setup_database.py hasn't been run
- **Solution**: Run `python setup_database.py`

### Error: "Table already exists"
- **Cause**: Tables were created before
- **Solution**: 
  - Option 1: Run the app (it handles existing tables)
  - Option 2: Drop and recreate: `mysql -u root -p -e "DROP DATABASE client_database;"`

### Excel data not imported
- **Cause**: File name mismatch or Excel file not found
- **Solution**: Ensure `Sample Routine .xlsx` is in the project root

---

## Backup & Maintenance

### Backup Database
```bash
mysqldump -u root -p client_database > backup.sql
```

### Restore Database
```bash
mysql -u root -p client_database < backup.sql
```

### Reset Database
```bash
mysql -u root -p
DROP DATABASE client_database;
```

Then re-run `python setup_database.py`

---

## Next Steps

1. **Import Excel Data**: Run `setup_database.py`
2. **Start Application**: Run `python app.py`
3. **View Database**: Go to http://localhost:5000/database
4. **Add/Manage Clients**: Use the web interface to manage your client data
5. **Generate Routines**: Use the home page to create personalized routines

---

## Support

For issues or questions:
- Check error messages in the terminal
- Review `config.py` settings
- Ensure MySQL is running and credentials are correct
- Check that dependencies are installed: `pip list | grep Flask`
