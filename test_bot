# test_bot.py - упрощенная версия для тестирования
import telebot
from telebot import types

BOT_TOKEN = "8568267520:AAG10Ff-f9562PwrgNFGboVZP-E3ulSi8DY"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🔍 Поиск", "📊 Статус")
    bot.send_message(message.chat.id, "🤖 Бот работает!", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.send_message(message.chat.id, f"Получил: {message.text}")

if __name__ == '__main__':
    print("Тестовый бот запущен")
    bot.infinity_polling()
