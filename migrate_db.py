import sqlite3

def migrate_db():
    conn = sqlite3.connect('civic_sense.db')
    c = conn.cursor()
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN email TEXT")
        print("Successfully added 'email' column to 'users' table.")
    except sqlite3.OperationalError as e:
        print(f"Migration might have already run: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    migrate_db()
