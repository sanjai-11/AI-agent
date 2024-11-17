import sqlite3 as db

# Initialize the SQLite database
def init_db():
    conn = db.connect('backend_data.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE,  -- Enforce unique keys
        value TEXT,
        created_time TEXT,
        updated_time TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Fetch all records from the database
def fetch_records():
    conn = db.connect('backend_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT key, value, created_time, updated_time FROM records')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Perform database operations (insert, update, delete)
def backend(action, key, value=None):
    conn = db.connect('backend_data.db')
    cursor = conn.cursor()
    try:
        # Prevent insertion or update if both key and value are None
        if action == "insert":
            if key is None and value is None:
                print("Error: Cannot insert a record with both key and value as None.")
            else:
                cursor.execute('''
                INSERT INTO records (key, value, created_time, updated_time)
                VALUES (?, ?, datetime('now'), NULL)
                ''', (key, value))

        elif action == "update":
            if key is None and value is None:
                print("Error: Cannot update a record with both key and value as None.")
            else:
                cursor.execute('''
                UPDATE records
                SET value = ?, updated_time = datetime('now')
                WHERE key = ?
                ''', (value, key))

        elif action == "delete":
            if key is None and value is None:
                # Delete rows where both key and value are None
                cursor.execute('''
                DELETE FROM records
                WHERE key IS NULL AND value IS NULL
                ''')
            elif key and value:  # Delete a specific row with both key and value
                cursor.execute('''
                DELETE FROM records
                WHERE key = ? AND value = ?
                ''', (key, value))
            elif key:  # Only delete the key, keep the value
                cursor.execute('''
                UPDATE records
                SET key = NULL, updated_time = datetime('now')
                WHERE key = ?
                ''', (key,))
            elif value:  # Only delete the value, keep the key
                cursor.execute('''
                UPDATE records
                SET value = NULL, updated_time = datetime('now')
                WHERE value = ?
                ''', (value,))

        conn.commit()
    except db.IntegrityError as e:
        print(f"IntegrityError: {e}")
    finally:
        conn.close()