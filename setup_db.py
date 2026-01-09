import sqlite3

def init_db():
    conn = sqlite3.connect('civic_sense.db')
    c = conn.cursor()
    
    # Create Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT, -- Added for password recovery
            role TEXT NOT NULL, -- 'student' or 'admin'
            domain TEXT -- NULL for students, Location/Category for admins
        )
    ''')
    
    # Create Reports Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            type TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            status TEXT DEFAULT 'Pending',
            date TEXT NOT NULL,
            resolved_date TEXT,
            FOREIGN KEY (student_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    init_db()
