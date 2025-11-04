import sqlite3
from datetime import datetime, timedelta

class PremiumManager:
    def __init__(self):
        self.conn = sqlite3.connect('hr_bot.db')
        self.create_tables()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                is_premium BOOLEAN DEFAULT FALSE,
                premium_until DATE,
                searches_today INTEGER DEFAULT 0,
                last_reset_date DATE
            )
        ''')
        self.conn.commit()
