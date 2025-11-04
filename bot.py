import logging
import sqlite3
import random
import telebot
from telebot import types
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = "8568267520:AAG10Ff-f9562PwrgNFGboVZP-E3ulSi8DY"
DATABASE_NAME = "hr_bot.db"

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

# Состояния пользователей
user_states = {}

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect(DATABASE_NAME)
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
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def generate_sample_candidates(skills):
    """Генерирует синтетические данные кандидатов"""
    names = ["Алексей Петров", "Мария Сидорова", "Иван Козлов", "Елена Новикова", 
             "Дмитрий Волков", "Анна Зайцева", "Сергей Орлов", "Ольга Лебедева"]
    
    positions = ["Junior", "Middle", "Senior"]
    technologies = ["Python", "JavaScript", "Java", "C++", "React", "Vue", "Django", "Flask"]
    
    candidates = []
    
    for i in range(5):
        name = random.choice(names)
        level = random.choice(positions)
        tech_skills = random.sample(technologies, 3)
        main_skill = random.choice(tech_skills)
        
        candidate = {
            "name": f"{name} ({level} {main_skill} Developer)",
            "skills": ", ".join(tech_skills),
            "experience": f"{random.randint(1, 8)} лет",
            "salary": f"{random.randint(80000, 300000)} руб."
        }
        candidates.append(candidate)
    
    return candidates

def create_interview_questions(position):
    """Генерирует вопросы для собеседования"""
    base_questions = [
        "Расскажите о вашем опыте работы и наиболее интересных проектах",
        "Какие технологии и инструменты вы используете в работе?",
        "Как вы организуете свой рабочий процесс?",
        "Расскажите о сложной задаче и как вы её решили",
        "Какие у вас планы по профессиональному развитию?"
    ]
    return base_questions[:3]  # Возвращаем первые 3 вопроса

@bot.message_handler(commands=['start'])
def start_handler(message):
    """Обработчик команды /start"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔍 Найти кандидатов")
    btn2 = types.KeyboardButton("💼 Провести собеседование")
    markup.add(btn1, btn2)
    
    bot.send_message(
        message.chat.id,
        "🤖 Добро пожаловать в HR AI Helper!\n"
        "Выберите действие:",
        reply_markup=markup
    )
    user_states[message.chat.id] = "CHOOSING"

@bot.message_handler(func=lambda message: message.text == "🔍 Найти кандидатов")
def find_candidates_handler(message):
    """Обработчик поиска кандидатов"""
    bot.send_message(message.chat.id, "Введите навыки для поиска (например: Python JavaScript):")
    user_states[message.chat.id] = "SEARCHING"

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "SEARCHING")
def handle_search(message):
    """Обработчик ввода навыков для поиска"""
    skills = message.text
    candidates = generate_sample_candidates(skills)
    
    response = "🎯 Найденные кандидаты:\n\n"
    for i, candidate in enumerate(candidates, 1):
        response += f"{i}. {candidate['name']}\n"
        response += f"   Навыки: {candidate['skills']}\n"
        response += f"   Опыт: {candidate['experience']}\n"
        response += f"   Зарплата: {candidate['salary']}\n\n"
    
    bot.send_message(message.chat.id, response)
    user_states[message.chat.id] = "CHOOSING"

@bot.message_handler(func=lambda message: message.text == "💼 Провести собеседование")
def start_interview_handler(message):
    """Обработчик начала собеседования"""
    questions = create_interview_questions("Python Developer")
    user_states[message.chat.id] = "INTERVIEW"
    user_states[f"{message.chat.id}_questions"] = questions
    user_states[f"{message.chat.id}_current_question"] = 0
    
    bot.send_message(
        message.chat.id,
        "💼 Начинаем собеседование!\n"
        f"Первый вопрос:\n\n{questions[0]}"
    )

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "INTERVIEW")
def handle_interview_answer(message):
    """Обработчик ответов на собеседовании"""
    questions = user_states.get(f"{message.chat.id}_questions", [])
    current = user_states.get(f"{message.chat.id}_current_question", 0) + 1
    
    if current < len(questions):
        user_states[f"{message.chat.id}_current_question"] = current
        bot.send_message(message.chat.id, f"Следующий вопрос:\n\n{questions[current]}")
    else:
        bot.send_message(message.chat.id, "✅ Собеседование завершено!")
        user_states[message.chat.id] = "CHOOSING"

@bot.message_handler(func=lambda message: True)
def default_handler(message):
    """Обработчик всех остальных сообщений"""
    if user_states.get(message.chat.id) != "SEARCHING" and user_states.get(message.chat.id) != "INTERVIEW":
        bot.send_message(message.chat.id, "Выберите действие из меню ниже 👇")

if __name__ == '__main__':
    init_db()
    print("🤖 Бот запущен! Остановите сочетанием Ctrl+C")
    bot.infinity_polling()
