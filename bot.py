import logging
import sqlite3
import random
import telebot
from telebot import types
import time
import requests
from premium_manager import check_daily_limit, get_user_stats

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = "8568267520:AAG10Ff-f9562PwrgNFGboVZP-E3ulSi8DY"
DATABASE_NAME = "hr_bot.db"

# Настройка для обхода прокси PythonAnywhere
session = requests.Session()
session.trust_env = False  # Отключаем использование системных прокси

# Инициализация бота с кастомной сессией
bot = telebot.TeleBot(BOT_TOKEN)
bot.session = session

# Состояния пользователей
user_states = {}

# Настройки премиума
PREMIUM_PRICE = 490
PREMIUM_FEATURES = [
    "Неограниченный поиск кандидатов",
    "Расширенная аналитика",
    "Экспорт в Excel/PDF", 
    "Шаблоны писем кандидатам",
    "Приоритетная поддержка"
]

def generate_sample_candidates(skills):
    """Генерирует синтетические данные кандидатов"""
    names = ["Алексей Петров", "Мария Сидорова", "Иван Козлов", "Елена Новикова", 
             "Дмитрий Волков", "Анна Зайцева", "Сергей Орлов", "Ольга Лебедева"]
    
    positions = ["Junior", "Middle", "Senior"]
    technologies = ["Python", "JavaScript", "Java", "C++", "React", "Vue", "Django", "Flask"]
    
    candidates = []
    
    for i in range(3):  # Уменьшаем до 3 кандидатов для скорости
        name = random.choice(names)
        level = random.choice(positions)
        tech_skills = random.sample(technologies, 2)  # Уменьшаем количество навыков
        main_skill = random.choice(tech_skills)
        
        candidate = {
            "name": f"{name} ({level} {main_skill} Developer)",
            "skills": ", ".join(tech_skills),
            "experience": f"{random.randint(1, 5)} лет",
            "salary": f"{random.randint(80000, 200000)} руб."
        }
        candidates.append(candidate)
    
    return candidates

@bot.message_handler(commands=['start'])
def start_handler(message):
    """Обработчик команды /start"""
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🔍 Найти кандидатов")
        btn2 = types.KeyboardButton("💼 Провести собеседование")
        btn3 = types.KeyboardButton("📊 Мой статус")
        markup.add(btn1, btn2, btn3)
        
        bot.send_message(
            message.chat.id,
            "🤖 Добро пожаловать в HR AI Helper!\n"
            "Выберите действие:",
            reply_markup=markup
        )
        user_states[message.chat.id] = "CHOOSING"
    except Exception as e:
        logger.error(f"Error in start_handler: {e}")
        # Упрощенное сообщение об ошибке
        try:
            bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте /start")
        except:
            pass

@bot.message_handler(func=lambda message: message.text == "🔍 Найти кандидатов")
def find_candidates_handler(message):
    """Проверяем лимиты перед поиском"""
    try:
        user_id = message.chat.id
        user_stats = get_user_stats(user_id)
        
        if not user_stats['is_premium'] and user_stats['searches_left'] <= 0:
            markup = types.InlineKeyboardMarkup()
            btn_premium = types.InlineKeyboardButton("💳 Купить премиум", callback_data="buy_premium")
            markup.add(btn_premium)
            
            bot.send_message(message.chat.id,
                f"❌ Лимит исчерпан! Использовано: {user_stats['searches_used']}/3\n"
                "🎁 Премиум - неограниченный доступ",
                reply_markup=markup)
            return
        
        if not check_daily_limit(user_id, 'searches'):
            bot.send_message(message.chat.id, "❌ Ошибка лимитов")
            return
            
        bot.send_message(message.chat.id, 
            f"🔍 Поиск... (осталось {user_stats['searches_left']-1}/3)\n"
            "Введите навыки (Python JavaScript):")
        user_states[message.chat.id] = "SEARCHING"
    except Exception as e:
        logger.error(f"Error in find_candidates_handler: {e}")
        try:
            bot.send_message(message.chat.id, "❌ Ошибка. Попробуйте снова.")
        except:
            pass

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "SEARCHING")
def handle_search(message):
    """Обработчик ввода навыков для поиска"""
    try:
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
    except Exception as e:
        logger.error(f"Error in handle_search: {e}")
        try:
            bot.send_message(message.chat.id, "❌ Ошибка поиска.")
        except:
            pass
        user_states[message.chat.id] = "CHOOSING"

@bot.message_handler(func=lambda message: message.text == "📊 Мой статус")
def status_handler(message):
    """Показывает текущий статус пользователя"""
    try:
        user_stats = get_user_stats(message.chat.id)
        
        if user_stats['is_premium']:
            status_text = "🎁 ПРЕМИУМ АКТИВЕН"
        else:
            status_text = f"🆓 БЕСПЛАТНЫЙ ({user_stats['searches_left']}/3)"
        
        bot.send_message(message.chat.id,
            f"📊 Ваш статус:\n{status_text}\n"
            f"Использовано: {user_stats['searches_used']}/3")
    except Exception as e:
        logger.error(f"Error in status_handler: {e}")
        try:
            bot.send_message(message.chat.id, "❌ Ошибка статуса.")
        except:
            pass

@bot.message_handler(func=lambda message: message.text == "💼 Провести собеседование")
def start_interview_handler(message):
    """Обработчик начала собеседования"""
    try:
        questions = [
            "Расскажите о вашем опыте работы",
            "Какие технологии используете?",
            "Опишите сложный проект"
        ]
        user_states[message.chat.id] = "INTERVIEW"
        user_states[f"{message.chat.id}_questions"] = questions
        user_states[f"{message.chat.id}_current_question"] = 0
        
        bot.send_message(message.chat.id, "💼 Собеседование:\n\n" + questions[0])
    except Exception as e:
        logger.error(f"Error in start_interview_handler: {e}")
        try:
            bot.send_message(message.chat.id, "❌ Ошибка собеседования.")
        except:
            pass

@bot.message_handler(func=lambda message: True)
def default_handler(message):
    """Обработчик всех остальных сообщений"""
    try:
        if user_states.get(message.chat.id) not in ["SEARCHING", "INTERVIEW"]:
            bot.send_message(message.chat.id, "Выберите действие из меню 👇")
    except Exception as e:
        logger.error(f"Error in default_handler: {e}")

if __name__ == '__main__':
    print("🤖 Бот запущен! Остановите Ctrl+C")
    try:
        # Пробуем разные методы запуска
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except KeyboardInterrupt:
        print("Бот остановлен")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        print(f"Критическая ошибка: {e}")
