import random

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
        
        # Фильтрация по запрошенным навыкам
        if skills.lower() not in ' '.join(tech_skills).lower():
            continue
            
        candidate = {
            "name": f"{name} ({level} {main_skill} Developer)",
            "skills": ", ".join(tech_skills),
            "experience": f"{random.randint(1, 8)} лет",
            "salary": f"{random.randint(80000, 300000)} руб."
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
