"""
View database tables and relations
"""
import sqlite3

db_path = 'calibaf.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 70)
print("DATABASE RELATIONS - CALIBAF STUDIO")
print("=" * 70)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("\nTABLES IN DATABASE:")
print("-" * 70)
for table in tables:
    table_name = table[0]
    print(f"\n[{table_name.upper()}]")
    
    # Get table schema
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    
    print("  Columns:")
    for col in columns:
        col_id, name, type_, not_null, default, pk = col
        pk_mark = " [PRIMARY KEY]" if pk else ""
        nn_mark = " [NOT NULL]" if not_null else ""
        print(f"    - {name:<20} {type_:<15}{pk_mark}{nn_mark}")
    
    # Get foreign keys
    cursor.execute(f"PRAGMA foreign_key_list({table_name});")
    fks = cursor.fetchall()
    
    if fks:
        print("  Foreign Keys:")
        for fk in fks:
            id_, seq, table_ref, from_col, to_col, on_delete, on_update, match = fk
            print(f"    - {from_col} -> {table_ref}({to_col})")

print("\n" + "=" * 70)
print("RECORD COUNTS:")
print("-" * 70)
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    print(f"  {table_name:<20} {count:>6} records")

print("\n" + "=" * 70)
print("SAMPLE DATA:")
print("-" * 70)

# Show sample clients
print("\nClients (first 3):")
cursor.execute("SELECT id, name, goal, skill_level, push_ups, pull_ups FROM clients LIMIT 3;")
for row in cursor.fetchall():
    print(f"  ID {row[0]}: {row[1]} | Goal: {row[2]} | Level: {row[3]} | Push-ups: {row[4]}, Pull-ups: {row[5]}")

# Show sample routines
print("\nRoutines (first 3):")
cursor.execute("SELECT id, client_id, day, exercise, sets, reps FROM routines LIMIT 3;")
for row in cursor.fetchall():
    print(f"  ID {row[0]}: Client {row[1]} | {row[2]} - {row[3]} ({row[4]}x{row[5]})")

# Show relationships
print("\nSessions (first 2):")
cursor.execute("SELECT id, client_id FROM sessions LIMIT 2;")
for row in cursor.fetchall():
    print(f"  ID {row[0]}: Client {row[1]}")

print("\n" + "=" * 70)
conn.close()
print("Done!")
