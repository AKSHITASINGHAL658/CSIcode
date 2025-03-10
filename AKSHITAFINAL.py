import os
import sqlite3
import sys
from pathlib import Path

DB_PATH = Path.home() / ".smartnav.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS dirs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        path TEXT UNIQUE,
                        score INTEGER DEFAULT 1,
                        last_accessed INTEGER
                    )''')
    conn.commit()
    return conn

def add_directory(path):
    conn = get_db_connection()
    conn.execute('''INSERT INTO dirs (path, score, last_accessed)
                    VALUES (?, 1, strftime('%s','now'))
                    ON CONFLICT(path) DO UPDATE SET
                    score = score + 1, last_accessed = strftime('%s','now')''', (path,))
    conn.commit()
    conn.close()

def find_best_match(query, current_dir):
    conn = get_db_connection()
    cursor = conn.execute('''SELECT path FROM dirs 
                             WHERE path LIKE ? 
                             ORDER BY 
                                CASE WHEN path LIKE ? THEN 1 ELSE 2 END, 
                                score DESC, 
                                last_accessed DESC 
                             LIMIT 1''',
                          (f'%{query}%', f'{current_dir}%'))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def main():
    if len(sys.argv) < 2:
        print("Usage: smartnav <command> [args]")
        return
    
    command = sys.argv[1]
    if command == "add":
        dir_path = os.getcwd()
        add_directory(dir_path)
    elif command == "jump":
        if len(sys.argv) < 3:
            print("Usage: smartnav jump <query>")
            return
        current_dir = os.getcwd()
        target = find_best_match(sys.argv[2], current_dir)
        if target:
            print(target)
    else:
        print("Unknown command")

if __name__ == "__main__":
    main()
