import sqlite3
import threading
from datetime import datetime, timedelta
from contextlib import contextmanager

class PremiumManager:
    def __init__(self):
        self.db_path = 'hr_bot.db'
        self._local = threading.local()
        self.create_tables()
    
    def get_connection(self):
        """Получает соединение с БД для текущего потока"""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self._local.conn
    
    @contextmanager
    def get_cursor(self):
        """Контекстный менеджер для работы с курсором"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def create_tables(self):
        """Создает таблицы если их нет"""
        with self.get_cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    is_premium BOOLEAN DEFAULT FALSE,
                    premium_until DATE,
                    searches_today INTEGER DEFAULT 0,
                    last_reset_date DATE
                )
            ''')
    
    def check_daily_limit(self, user_id, action_type):
        """Проверяет дневной лимит для пользователя"""
        with self.get_cursor() as cursor:
            # Получаем данные пользователя
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            
            # Если пользователя нет - создаем
            if not user:
                cursor.execute(
                    'INSERT INTO users (user_id, last_reset_date) VALUES (?, ?)',
                    (user_id, datetime.now().date().isoformat())
                )
                return True
            
            user_id, is_premium, premium_until, searches_today, last_reset_date = user
            
            # Премиум пользователи без лимитов
            if is_premium and premium_until:
                premium_until_date = datetime.strptime(premium_until, '%Y-%m-%d').date()
                if datetime.now().date() <= premium_until_date:
                    return True
            
            # Сбрасываем счетчик если новый день
            if last_reset_date != datetime.now().date().isoformat():
                cursor.execute(
                    'UPDATE users SET searches_today = 0, last_reset_date = ? WHERE user_id = ?',
                    (datetime.now().date().isoformat(), user_id)
                )
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
            
            return True
    
    def get_user_stats(self, user_id):
        """Возвращает статистику пользователя"""
        with self.get_cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return {"searches_used": 0, "searches_left": 3, "is_premium": False}
            
            user_id, is_premium, premium_until, searches_today, last_reset_date = user
            
            # Сбрасываем если новый день
            if last_reset_date != datetime.now().date().isoformat():
                searches_today = 0
            
            return {
                "searches_used": searches_today,
                "searches_left": 3 - searches_today,
                "is_premium": bool(is_premium)
            }
    
    def close_connections(self):
        """Закрывает все соединения (для завершения работы)"""
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            del self._local.conn

# Глобальный экземпляр менеджера
premium_manager = PremiumManager()

# Функции для импорта в bot.py
def check_daily_limit(user_id, action_type):
    return premium_manager.check_daily_limit(user_id, action_type)

def get_user_stats(user_id):
    return premium_manager.get_user_stats(user_id)
