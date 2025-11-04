BOT_TOKEN = "8568267520:AAG10Ff-f9562PwrgNFGboVZP-E3ulSi8DY"
DATABASE_NAME = "hr_bot.db"
ADMIN_IDS = [356816394]

# Настройки безопасности
MAX_REQUESTS_PER_DAY = 50
REQUEST_TIMEOUT = 30

# Система лимитов
FREE_DAILY_LIMITS = {
    'searches': 3,
    'interviews': 2,
    'exports': 1
}

PREMIUM_PRICE = 490  # руб/месяц
PREMIUM_FEATURES = [
    "Неограниченный поиск кандидатов",
    "Расширенная аналитика",
    "Экспорт в Excel/PDF", 
    "Шаблоны писем кандидатам",
    "Приоритетная поддержка"
]

# Добавляем настройки вакансий и городов
VACANCY_TYPES = {
    "python": "Python разработчик",
    "javascript": "JavaScript разработчик", 
    "java": "Java разработчик",
    "devops": "DevOps инженер",
    "qa": "QA инженер",
    "frontend": "Frontend разработчик",
    "backend": "Backend разработчик"
}

CITIES = [
    "Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Нижний Тагил", "Казань",
    "Нижний Новгород", "Челябинск", "Самара", "Омск", "Ростов-на-Дону",
    "Уфа", "Красноярск", "Воронеж", "Пермь", "Волгоград", "Все города"
]