import random

def create_interview_questions(position):
    """Генерирует вопросы для собеседования в зависимости от позиции"""
    
    base_questions = [
        "Расскажите о вашем опыте работы и наиболее интересных проектах",
        "Какие технологии и инструменты вы используете в работе?",
        "Как вы организуете свой рабочий процесс?",
        "Расскажите о сложной задаче и как вы её решили",
        "Какие у вас планы по профессиональному развитию?"
    ]
    
    technical_questions = {
        "Python": [
            "Что такое декораторы в Python и как вы их используете?",
            "В чем разница между списками и кортежами?",
            "Как работает GIL в Python?",
            "Какие вы знаете ORM и с какими работали?",
            "Как вы тестируете Python код?"
        ],
        "JavaScript": [
            "Что такое замыкания и как они работают?",
            "Объясните разницу между let, const и var",
            "Что такое Promise и как с ним работать?",
            "Расскажите о Event Loop в JavaScript",
            "Какие фреймворки вы использовали и почему?"
        ],
        "Java": [
            "В чем разница между ArrayList и LinkedList?",
            "Что такое многопоточность в Java?",
            "Объясните принципы ООП на примерах",
            "Как работает сборщик мусора в Java?",
            "Что такое Spring Framework и его преимущества?"
        ]
    }
    
    # Выбираем технические вопросы на основе позиции
    tech_questions = []
    for tech, questions in technical_questions.items():
        if tech.lower() in position.lower():
            tech_questions.extend(questions)
    
    if not tech_questions:
        # Если не нашли специфичных вопросов, берем случайные из всех
        all_tech_questions = [q for questions in technical_questions.values() for q in questions]
        tech_questions = random.sample(all_tech_questions, 3)
    
    all_questions = base_questions + tech_questions
    return random.sample(all_questions, min(5, len(all_questions)))
