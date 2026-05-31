# Calibaf Studio Routine Generator

This is a web application for generating personalized calisthenics routines based on client assessments with MySQL database integration.

## Quick Start

### Prerequisites
- Python 3.8+
- MySQL Server installed and running
- Excel file with client data (Sample Routine .xlsx)

### Setup Steps

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Database:**
   - Edit `config.py` with your MySQL credentials
   - Set MYSQL_USER and MYSQL_PASSWORD

3. **Initialize Database:**
   ```bash
   python setup_database.py
   ```
   This will create the database and import your Excel data.

4. **Run the app:**
   ```bash
   python app.py
   ```

5. **Access:**
   - **Home**: http://127.0.0.1:5000
   - **Database View**: http://127.0.0.1:5000/database

## Features

- **Client Database** with professional web interface
- **Add/Edit/Delete** clients
- **Search and Filter** by name, goal, or skill level
- **Export Data** to CSV
- **Client assessment form**
- **ML-based level prediction**
- **Medical condition alternatives**
- **4-week progression plan**
- **Statistics Dashboard** (total clients, averages, skill levels)

## Database

The application uses MySQL with three main tables:
- **clients**: Client information and fitness metrics
- **routines**: Personalized exercise routines
- **sessions**: Training session data

See [SETUP_DATABASE.md](SETUP_DATABASE.md) for detailed database setup and maintenance.

## API Endpoints

```
GET  /api/clients              - Get all clients
GET  /api/client/<id>          - Get single client
POST /api/client               - Create new client
PUT  /api/client/<id>          - Update client
DELETE /api/client/<id>        - Delete client
```

## File Structure

```
calibaf-project/
├── app.py                      # Main Flask application
├── config.py                   # Database configuration
├── models.py                   # SQLAlchemy models
├── setup_database.py           # Database initialization script
├── requirements.txt            # Python dependencies
├── SETUP_DATABASE.md          # Database setup guide
├── templates/
│   ├── index.html             # Home page
│   ├── result.html            # Routine results
│   ├── database.html          # Database interface
│   └── goal-review.html       # Goal review page
├── static/
│   ├── style.css              # Styles
│   └── routine-tracker.js     # JavaScript
└── data/
    ├── clients.json           # Backed up client data
    └── sessions/              # Session data
```

## Database Setup Troubleshooting

See [SETUP_DATABASE.md](SETUP_DATABASE.md) for:
- MySQL installation instructions
- Connection troubleshooting
- Backup and restore procedures
- Database maintenance

## Workflow

1. **Import Data**: Run `setup_database.py` to import Excel data
2. **View Clients**: Visit `/database` to see all clients
3. **Manage Data**: Add, edit, or delete clients via web interface
4. **Generate Routines**: Use home page for routine generation
5. **Export Results**: Export client data to CSV

Replace the dummy dataset with actual client data for authenticity.