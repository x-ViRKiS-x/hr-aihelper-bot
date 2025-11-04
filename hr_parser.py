import random

def generate_sample_candidates(skills, city="Все города"):
    """Генерирует синтетические данные кандидатов с учетом города"""
    
    names = ["Алексей Петров", "Мария Сидорова", "Иван Козлов", "Елена Новикова", 
             "Дмитрий Волков", "Анна Зайцева", "Сергей Орлов", "Ольга Лебедева"]
    
    positions = ["Junior", "Middle", "Senior"]
    technologies = ["Python", "JavaScript", "Java", "C++", "React", "Vue", "Django", "Flask"]
    
    # Зарплаты в зависимости от города
    salary_ranges = {
        "Москва": (120000, 400000),
        "Санкт-Петербург": (100000, 350000),
        "Все города": (80000, 300000),
        "default": (70000, 250000)
    }
    
    salary_range = salary_ranges.get(city, salary_ranges["default"])
    
    candidates = []
    
    for i in range(3):
        name = random.choice(names)
        level = random.choice(positions)
        tech_skills = random.sample(technologies, 2)
        main_skill = random.choice(tech_skills)
        
        candidate = {
            "name": f"{name} ({level} {main_skill} Developer)",
            "skills": ", ".join(tech_skills),
            "experience": f"{random.randint(1, 8)} лет",
            "salary": f"{random.randint(salary_range[0], salary_range[1])} руб.",
            "city": city if city != "Все города" else random.choice(["Москва", "СПб", "Новосибирск", "Екатеринбург", "Нижний Тагил"])
        }
        candidates.append(candidate)
    
    if not candidates:
        # Если нет кандидатов по фильтру, показываем случайных
        for i in range(3):
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
