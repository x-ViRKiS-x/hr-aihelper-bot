import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import config
from database import init_db, add_candidate, get_candidates
from hr_parser import generate_sample_candidates
from interview_manager import create_interview_questions

# States for conversation
CHOOSING, SEARCHING, INTERVIEW = range(3)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🔍 Найти кандидатов", "💼 Провести собеседование"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🤖 Добро пожаловать в HR AI Helper!\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )
    return CHOOSING

async def find_candidates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите навыки для поиска (например: Python JavaScript):")
    return SEARCHING

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    skills = update.message.text
    candidates = generate_sample_candidates(skills)
    
    response = "🎯 Найденные кандидаты:\n\n"
    for i, candidate in enumerate(candidates, 1):
        response += f"{i}. {candidate['name']}\n"
        response += f"   Навыки: {candidate['skills']}\n"
        response += f"   Опыт: {candidate['experience']}\n"
        response += f"   Зарплата: {candidate['salary']}\n\n"
    
    await update.message.reply_text(response)
    return CHOOSING

async def start_interview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    questions = create_interview_questions("Python Developer")
    context.user_data['interview_questions'] = questions
    context.user_data['current_question'] = 0
    
    await update.message.reply_text(
        "💼 Начинаем собеседование!\n"
        f"Первый вопрос:\n\n{questions[0]}"
    )
    return INTERVIEW

async def handle_interview_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Здесь можно добавить анализ ответа
    questions = context.user_data['interview_questions']
    current = context.user_data['current_question'] + 1
    
    if current < len(questions):
        context.user_data['current_question'] = current
        await update.message.reply_text(f"Следующий вопрос:\n\n{questions[current]}")
        return INTERVIEW
    else:
        await update.message.reply_text("✅ Собеседование завершено!")
        return CHOOSING

def main():
    init_db()
    
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^🔍 Найти кандидатов$"), find_candidates),
                MessageHandler(filters.Regex("^💼 Провести собеседование$"), start_interview),
            ],
            SEARCHING: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search)
            ],
            INTERVIEW: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_interview_answer)
            ]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
