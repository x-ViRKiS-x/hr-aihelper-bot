import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, ConversationHandler
import config
from database import init_db
from hr_parser import generate_sample_candidates
from interview_manager import create_interview_questions

# States for conversation
CHOOSING, SEARCHING, INTERVIEW = range(3)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    keyboard = [["🔍 Найти кандидатов", "💼 Провести собеседование"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        "🤖 Добро пожаловать в HR AI Helper!\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )
    return CHOOSING

def find_candidates(update: Update, context: CallbackContext):
    update.message.reply_text("Введите навыки для поиска (например: Python JavaScript):")
    return SEARCHING

def handle_search(update: Update, context: CallbackContext):
    skills = update.message.text
    candidates = generate_sample_candidates(skills)
    
    response = "🎯 Найденные кандидаты:\n\n"
    for i, candidate in enumerate(candidates, 1):
        response += f"{i}. {candidate['name']}\n"
        response += f"   Навыки: {candidate['skills']}\n"
        response += f"   Опыт: {candidate['experience']}\n"
        response += f"   Зарплата: {candidate['salary']}\n\n"
    
    update.message.reply_text(response)
    return CHOOSING

def start_interview(update: Update, context: CallbackContext):
    questions = create_interview_questions("Python Developer")
    context.user_data['interview_questions'] = questions
    context.user_data['current_question'] = 0
    
    update.message.reply_text(
        "💼 Начинаем собеседование!\n"
        f"Первый вопрос:\n\n{questions[0]}"
    )
    return INTERVIEW

def handle_interview_answer(update: Update, context: CallbackContext):
    questions = context.user_data['interview_questions']
    current = context.user_data['current_question'] + 1
    
    if current < len(questions):
        context.user_data['current_question'] = current
        update.message.reply_text(f"Следующий вопрос:\n\n{questions[current]}")
        return INTERVIEW
    else:
        update.message.reply_text("✅ Собеседование завершено!")
        return CHOOSING

def error(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    init_db()
    
    updater = Updater(config.BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(Filters.regex('^🔍 Найти кандидатов$'), find_candidates),
                MessageHandler(Filters.regex('^💼 Провести собеседование$'), start_interview),
            ],
            SEARCHING: [
                MessageHandler(Filters.text & ~Filters.command, handle_search)
            ],
            INTERVIEW: [
                MessageHandler(Filters.text & ~Filters.command, handle_interview_answer)
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    
    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    
    updater.start_polling()
    print("🤖 Бот запущен! Остановите сочетанием Ctrl+C")
    updater.idle()

if __name__ == '__main__':
    main()
