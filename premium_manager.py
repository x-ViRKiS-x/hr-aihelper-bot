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
    
    def check_daily_limit(self, user_id, action_type):
        """Проверяет дневной лимит для пользователя"""
        cursor = self.conn.cursor()
        
        # Получаем данные пользователя
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        # Если пользователя нет - создаем
        if not user:
            cursor.execute(
                'INSERT INTO users (user_id, last_reset_date) VALUES (?, ?)',
                (user_id, datetime.now().date())
            )
            self.conn.commit()
            return True
        
        user_id, is_premium, premium_until, searches_today, last_reset_date = user
        
        # Премиум пользователи без лимитов
        if is_premium and premium_until and datetime.now().date() <= datetime.strptime(premium_until, '%Y-%m-%d').date():
            return True
        
        # Сбрасываем счетчик если новый день
        if last_reset_date != datetime.now().date():
            cursor.execute(
                'UPDATE users SET searches_today = 0, last_reset_date = ? WHERE user_id = ?',
                (datetime.now().date(), user_id)
            )
            self.conn.commit()
            searches_today = 0
        
        # Проверяем лимиты
        if action_type == 'searches':
            if searches_today >= 3:  # 3 бесплатных поиска в день
                return False
            # Увеличиваем счетчик
            cursor.execute(
                'UPDATE users SET searches_today = searches_today + 1 WHERE user_id = ?',
                (user_id,)
            )
            self.conn.commit()
        
        return True
    
    def get_user_stats(self, user_id):
        """Возвращает статистику пользователя"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return {"searches_used": 0, "searches_left": 3, "is_premium": False}
        
        user_id, is_premium, premium_until, searches_today, last_reset_date = user
        
        # Сбрасываем если новый день
        if last_reset_date != datetime.now().date():
            searches_today = 0
        
        return {
            "searches_used": searches_today,
            "searches_left": 3 - searches_today,
            "is_premium": is_premium
        }

# Глобальный экземпляр менеджера
premium_manager = PremiumManager()

# Функции для импорта в bot.py
def check_daily_limit(user_id, action_type):
    return premium_manager.check_daily_limit(user_id, action_type)

def get_user_stats(user_id):
    return premium_manager.get_user_stats(user_id)
