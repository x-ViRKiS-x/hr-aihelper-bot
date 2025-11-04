import sqlite3
import logging

logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect('hr_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            skills TEXT NOT NULL,
            experience TEXT NOT NULL,
            salary TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            vacancy_type TEXT NOT NULL,
            candidate_name TEXT NOT NULL,
            questions TEXT NOT NULL,
            answers TEXT,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def add_candidate(name, skills, experience, salary):
    conn = sqlite3.connect('hr_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO candidates (name, skills, experience, salary)
        VALUES (?, ?, ?, ?)
    ''', (name, skills, experience, salary))
    
    conn.commit()
    conn.close()

def get_candidates(skills_filter=None):
    conn = sqlite3.connect('hr_bot.db')
    cursor = conn.cursor()
    
    if skills_filter:
        cursor.execute('''
            SELECT * FROM candidates WHERE skills LIKE ?
        ''', (f'%{skills_filter}%',))
    else:
        cursor.execute('SELECT * FROM candidates')
    
    candidates = cursor.fetchall()
    conn.close()
    
    return candidates
