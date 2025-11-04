import logging
import sqlite3
import random
import telebot
from telebot import types
import time
import requests
from premium_manager import check_daily_limit, get_user_stats
from interview_system import InterviewSystem
import config

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

# Инициализация систем
interview_system = InterviewSystem()

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
    """Начинает процесс поиска кандидатов с выбором города"""
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        
        # Создаем кнопки городов
        buttons = []
        for i in range(0, len(config.CITIES), 3):
            row = config.CITIES[i:i+3]
            buttons.extend([types.KeyboardButton(city) for city in row])
        
        markup.add(*buttons)
        markup.add(types.KeyboardButton("❌ Отмена"))
        
        bot.send_message(
            message.chat.id,
            "🏙 Выберите город для поиска кандидатов:",
            reply_markup=markup
        )
        user_states[message.chat.id] = "SELECTING_CITY"
        
    except Exception as e:
        logger.error(f"Error in find_candidates_handler: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при начале поиска.")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "SELECTING_CITY")
def handle_city_selection(message):
    """Обработчик выбора города для поиска"""
    try:
        if message.text == "❌ Отмена":
            show_main_menu(message)
            return
            
        if message.text not in config.CITIES:
            bot.send_message(message.chat.id, "❌ Пожалуйста, выберите город из списка.")
            return
            
        # Сохраняем выбранный город и запрашиваем навыки
        user_states[f"{message.chat.id}_search_city"] = message.text
        user_states[message.chat.id] = "SEARCHING"
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("❌ Отмена"))
        
        bot.send_message(
            message.chat.id,
            f"🏙 Поиск в городе: {message.text}\n\n"
            "Введите навыки для поиска (например: Python JavaScript):",
            reply_markup=markup
        )
        
    except Exception as e:
        logger.error(f"Error in handle_city_selection: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при выборе города.")
        show_main_menu(message)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "SEARCHING")
def handle_search(message):
    """Обработчик ввода навыков для поиска"""
    try:
        if message.text == "❌ Отмена":
            show_main_menu(message)
            return
            
        skills = message.text
        city = user_states.get(f"{message.chat.id}_search_city", "Все города")
        
        # Проверяем лимиты
        user_id = message.chat.id
        user_stats = get_user_stats(user_id)
        
        if not user_stats['is_premium'] and user_stats['searches_left'] <= 0:
            show_premium_offer(message, user_stats)
            return
        
        if not check_daily_limit(user_id, 'searches'):
            bot.send_message(message.chat.id, "❌ Ошибка системы лимитов")
            return
        
        # Выполняем поиск
        candidates = generate_sample_candidates(skills, city)
        
        response = f"🎯 Найденные кандидаты в {city}:\n\n"
        for i, candidate in enumerate(candidates, 1):
            response += f"{i}. **{candidate['name']}**\n"
            response += f"   🏙 Город: {candidate['city']}\n"
            response += f"   💼 Навыки: {candidate['skills']}\n"
            response += f"   📅 Опыт: {candidate['experience']}\n"
            response += f"   💰 Зарплата: {candidate['salary']}\n\n"
        
        bot.send_message(message.chat.id, response, parse_mode='Markdown')
        user_states[message.chat.id] = "CHOOSING"
        
        # Очищаем временные данные
        if f"{message.chat.id}_search_city" in user_states:
            del user_states[f"{message.chat.id}_search_city"]
            
    except Exception as e:
        logger.error(f"Error in handle_search: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при поиске кандидатов.")
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
    """Начало нового собеседования - выбор типа вакансии"""
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        
        # Создаем кнопки для выбора типа вакансии
        buttons = []
        for key, value in config.VACANCY_TYPES.items():
            buttons.append(types.KeyboardButton(value))
        
        # Добавляем кнопку отмены
        buttons.append(types.KeyboardButton("❌ Отмена"))
        markup.add(*buttons)
        
        bot.send_message(
            message.chat.id,
            "🎯 Выберите тип вакансии для собеседования:",
            reply_markup=markup
        )
        user_states[message.chat.id] = "SELECTING_VACANCY"
        
    except Exception as e:
        logger.error(f"Error in start_interview_handler: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при запуске собеседования.")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "SELECTING_VACANCY")
def handle_vacancy_selection(message):
    """Обработчик выбора типа вакансии"""
    try:
        if message.text == "❌ Отмена":
            show_main_menu(message)
            return
            
        # Находим ключ вакансии по названию
        vacancy_type = None
        for key, value in config.VACANCY_TYPES.items():
            if value == message.text:
                vacancy_type = key
                break
                
        if not vacancy_type:
            bot.send_message(message.chat.id, "❌ Пожалуйста, выберите вакансию из списка.")
            return
            
        # Сохраняем тип вакансии и запрашиваем имя кандидата
        user_states[message.chat.id] = "ENTERING_CANDIDATE_NAME"
        user_states[f"{message.chat.id}_vacancy_type"] = vacancy_type
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("❌ Отмена"))
        
        bot.send_message(
            message.chat.id,
            f"📝 Выбрана вакансия: {message.text}\n\n"
            "Введите имя кандидата:",
            reply_markup=markup
        )
        
    except Exception as e:
        logger.error(f"Error in handle_vacancy_selection: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при выборе вакансии.")
        show_main_menu(message)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "ENTERING_CANDIDATE_NAME")
def handle_candidate_name(message):
    """Обработчик ввода имени кандидата"""
    try:
        if message.text == "❌ Отмена":
            show_main_menu(message)
            return
            
        candidate_name = message.text
        vacancy_type = user_states.get(f"{message.chat.id}_vacancy_type")
        
        # Начинаем собеседование
        interview_id, questions = interview_system.start_interview(
            message.chat.id, vacancy_type, candidate_name
        )
        
        # Сохраняем данные собеседования
        user_states[message.chat.id] = "IN_INTERVIEW"
        user_states[f"{message.chat.id}_interview_id"] = interview_id
        user_states[f"{message.chat.id}_interview_questions"] = questions
        user_states[f"{message.chat.id}_current_question"] = 0
        
        # Показываем первый вопрос
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("⏩ Пропустить вопрос"))
        markup.add(types.KeyboardButton("❌ Завершить собеседование"))
        
        bot.send_message(
            message.chat.id,
            f"💼 Начинаем собеседование с {candidate_name}\n"
            f"Вакансия: {config.VACANCY_TYPES[vacancy_type]}\n\n"
            f"Вопрос 1/{len(questions)}:\n"
            f"**{questions[0]}**\n\n"
            "Записывайте ответ кандидата:",
            reply_markup=markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Error in handle_candidate_name: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при начале собеседования.")
        show_main_menu(message)

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "IN_INTERVIEW")
def handle_interview_answer(message):
    """Обработчик ответов во время собеседования"""
    try:
        interview_id = user_states.get(f"{message.chat.id}_interview_id")
        questions = user_states.get(f"{message.chat.id}_interview_questions")
        current_index = user_states.get(f"{message.chat.id}_current_question")
        
        if message.text == "❌ Завершить собеседование":
            complete_interview(message, interview_id)
            return
            
        if message.text == "⏩ Пропустить вопрос":
            # Просто переходим к следующему вопросу без сохранения
            pass
        else:
            # Сохраняем ответ кандидата
            interview_system.save_answer(interview_id, current_index, message.text)
        
        # Переходим к следующему вопросу
        next_index = current_index + 1
        
        if next_index < len(questions):
            user_states[f"{message.chat.id}_current_question"] = next_index
            
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("⏩ Пропустить вопрос"))
            markup.add(types.KeyboardButton("❌ Завершить собеседование"))
            
            bot.send_message(
                message.chat.id,
                f"Вопрос {next_index + 1}/{len(questions)}:\n"
                f"**{questions[next_index]}**\n\n"
                "Записывайте ответ кандидата:",
                reply_markup=markup,
                parse_mode='Markdown'
            )
        else:
            # Все вопросы заданы - завершаем собеседование
            complete_interview(message, interview_id)
            
    except Exception as e:
        logger.error(f"Error in handle_interview_answer: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при сохранении ответа.")
        show_main_menu(message)

def complete_interview(message, interview_id):
    """Завершает собеседование и показывает меню"""
    try:
        interview_system.complete_interview(interview_id)
        
        # Очищаем состояние
        user_states[message.chat.id] = "CHOOSING"
        for key in [f"{message.chat.id}_interview_id", 
                   f"{message.chat.id}_interview_questions",
                   f"{message.chat.id}_current_question",
                   f"{message.chat.id}_vacancy_type"]:
            if key in user_states:
                del user_states[key]
        
        bot.send_message(
            message.chat.id,
            "✅ Собеседование завершено!\n"
            "Все ответы сохранены в истории.",
            reply_markup=get_main_menu()
        )
        
    except Exception as e:
        logger.error(f"Error in complete_interview: {e}")
        show_main_menu(message)
        
@bot.message_handler(commands=['history'])
def interview_history_handler(message):
    """Показывает историю собеседований"""
    try:
        interviews = interview_system.get_interview_history(message.chat.id)
        
        if not interviews:
            bot.send_message(message.chat.id, "📝 У вас еще нет завершенных собеседований.")
            return
        
        response = "📋 История ваших собеседований:\n\n"
        
        for interview in interviews:
            interview_id, candidate_name, vacancy_type, start_time, end_time = interview
            vacancy_name = config.VACANCY_TYPES.get(vacancy_type, vacancy_type)
            
            response += f"👤 **{candidate_name}**\n"
            response += f"💼 {vacancy_name}\n"
            response += f"📅 {start_time[:10]}\n"
            response += f"🔗 ID: {interview_id}\n\n"
        
        bot.send_message(message.chat.id, response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in interview_history_handler: {e}")
        bot.send_message(message.chat.id, "❌ Ошибка при получении истории.")

def show_main_menu(message):
    """Показывает главное меню"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔍 Найти кандидатов")
    btn2 = types.KeyboardButton("💼 Провести собеседование")
    btn3 = types.KeyboardButton("📊 Мой статус")
    btn4 = types.KeyboardButton("📋 История собеседований")
    markup.add(btn1, btn2, btn3, btn4)
    
    user_states[message.chat.id] = "CHOOSING"
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

def get_main_menu():
    """Возвращает главное меню"""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🔍 Найти кандидатов")
    btn2 = types.KeyboardButton("💼 Провести собеседование")
    btn3 = types.KeyboardButton("📊 Мой статус")
    btn4 = types.KeyboardButton("📋 История собеседований")
    markup.add(btn1, btn2, btn3, btn4)
    return markup

@bot.message_handler(func=lambda message: message.text == "📋 История собеседований")
def history_button_handler(message):
    """Обработчик кнопки истории собеседований"""
    interview_history_handler(message)

@bot.message_handler(func=lambda message: True)
def default_handler(message):
    """Обработчик всех остальных сообщений"""
    try:
        current_state = user_states.get(message.chat.id)
        if current_state not in ["SEARCHING", "INTERVIEW"]:
            bot.send_message(message.chat.id, "Выберите действие из меню ниже 👇")
        # Если состояние INTERVIEW или SEARCHING - сообщение обрабатывается другими хендлерами
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
