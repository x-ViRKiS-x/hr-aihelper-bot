import sqlite3
from datetime import datetime
import json

class InterviewSystem:
    def __init__(self):
        self.db_path = 'hr_bot.db'
    
    def get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)
    
    def get_questions_for_vacancy(self, vacancy_type):
        """Генерирует вопросы для конкретной вакансии"""
        questions_map = {
            "python": [
                "Расскажите о вашем опыте работы с Python",
                "Какие фреймворки Django/Flask вы использовали?",
                "Как вы работаете с базами данных?",
                "Опишите опыт асинхронного программирования",
                "Какие инструменты тестирования используете?"
            ],
            "javascript": [
                "Опыт работы с JavaScript/TypeScript",
                "Какие фреймворки React/Vue/Angular использовали?",
                "Расскажите о работе с состоянием приложения",
                "Опыт работы с Node.js",
                "Как вы обеспечиваете производительность фронтенда?"
            ],
            "devops": [
                "Опыт работы с облачными платформами",
                "Настройка CI/CD пайплайнов",
                "Работа с контейнеризацией (Docker, Kubernetes)",
                "Мониторинг и логирование",
                "Обеспечение безопасности инфраструктуры"
            ]
        }
        return questions_map.get(vacancy_type, [
            "Расскажите о вашем профессиональном опыте",
            "Какие технологии и инструменты вы используете?",
            "Опишите самый сложный проект в карьере"
        ])
    
    def start_interview(self, user_id, vacancy_type, candidate_name):
        """Начинает новое собеседование"""
        questions = self.get_questions_for_vacancy(vacancy_type)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO interviews 
                (user_id, vacancy_type, candidate_name, questions, start_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, vacancy_type, candidate_name, 
                  json.dumps(questions, ensure_ascii=False), datetime.now()))
            
            interview_id = cursor.lastrowid
            conn.commit()
        
        return interview_id, questions
    
    def save_answer(self, interview_id, question_index, answer):
        """Сохраняет ответ кандидата"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Получаем текущие ответы
            cursor.execute('SELECT answers FROM interviews WHERE id = ?', (interview_id,))
            result = cursor.fetchone()
            
            answers = {}
            if result[0]:
                answers = json.loads(result[0])
            
            # Сохраняем новый ответ
            answers[str(question_index)] = answer
            
            cursor.execute('''
                UPDATE interviews SET answers = ? WHERE id = ?
            ''', (json.dumps(answers, ensure_ascii=False), interview_id))
            conn.commit()
    
    def complete_interview(self, interview_id):
        """Завершает собеседование"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE interviews SET end_time = ? WHERE id = ?
            ''', (datetime.now(), interview_id))
            conn.commit()
    
    def get_interview_history(self, user_id):
        """Возвращает историю собеседований пользователя"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, candidate_name, vacancy_type, start_time, end_time
                FROM interviews 
                WHERE user_id = ? 
                ORDER BY start_time DESC
                LIMIT 10
            ''', (user_id,))
            return cursor.fetchall()