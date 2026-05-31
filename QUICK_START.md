# Quick Start Guide - Client Database

## 60-Second Setup

### 1. Ensure MySQL is Running
- **Windows**: Start MySQL from Services
- **Mac**: `brew services start mysql`
- **Linux**: `sudo systemctl start mysql`

### 2. Update Credentials (if needed)
Edit `config.py`:
```python
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'your_password'  # Set your MySQL password
```

### 3. Create Database
```bash
python setup_database.py
```

Output should show:
```
✓ Database 'client_database' created
✓ Tables created successfully
✓ Excel data imported
```

### 4. Start Application
```bash
python app.py
```

### 5. Access the Database
Open browser: **http://localhost:5000/database**

---

## What You Get

A professional web interface with:
- ✓ All clients displayed in a table with proper formatting
- ✓ Column headers: ID | Name | Goal | Push-ups | Pull-ups | Level | Medical | Joined | Actions
- ✓ Color-coded skill levels (Beginner, Intermediate, Advanced, Expert)
- ✓ Search and filter functionality
- ✓ Add new clients with modal form
- ✓ Edit and delete existing clients
- ✓ Export data to CSV
- ✓ Statistics dashboard

---

## Common Commands

```bash
# Setup database
python setup_database.py

# Start application
python app.py

# View app
http://localhost:5000

# View database
http://localhost:5000/database

# Backup database
mysqldump -u root -p client_database > backup.sql

# Reset database
mysql -u root -p -e "DROP DATABASE client_database;"
python setup_database.py
```

---

## File Structure

```
calibaf project/
├── config.py              ← Database credentials
├── models.py              ← Data structure
├── setup_database.py      ← Run this first
├── app.py                 ← Main application
├── requirements.txt       ← Dependencies
├── templates/
│   └── database.html      ← Beautiful data UI
└── data/
    └── clients.json       ← Backup
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" | Start MySQL server |
| "Access denied" | Check MySQL password in config.py |
| "Database doesn't exist" | Run setup_database.py |
| "No data showing" | Ensure Excel file exists & setup ran |

---

## Next Steps

1. ✓ Database is set up
2. View data at `/database`
3. Add/edit clients via web interface
4. Generate routines from home page
5. Export data when needed

---

See [SETUP_DATABASE.md](SETUP_DATABASE.md) for detailed information.
