import sqlite3

def init():
    conn = sqlite3.connect('../database.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mac_address TEXT UNIQUE NOT NULL,
        time_remaining INTEGER DEFAULT 0,
        last_connected DATETIME DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT 0,
        FOREIGN KEY (plan_id) REFERENCES plans (id),
    );
    ''')
    cursor.execute('''
    CREATE TABLE coin_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mac_address TEXT NOT NULL,
        coin_value INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (mac_address) REFERENCES devices (mac_address)
    );
    ''')
    cursor.execute('''
    CREATE TABLE plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price INTEGER NOT NULL,
        duration INTEGER NOT NULL
    );
    ''')
    cursor.execute('''
    
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("Initializing database...")
    init()
    print("Database initialized")