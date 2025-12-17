import os
from typing import List
from .config import config
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_keywords() -> List[str]:
    """
    Загружает список ключевых слов из файла
    Игнорирует пустые строки и комментарии (начинающиеся с #)
    """
    filepath = config.KEYWORDS_FILE
    
    if not os.path.exists(filepath):
        logger.info(f"Файл ключевых слов не найден, создается файл по умолчанию: {filepath}")
        save_keywords()
        return [
            "спасиб", "благодар", "признател", "ценю твою", "ценю вашу",
            "ты мне очень помог", "ты мне сильно помог", "ты помог",
            "ты лучший", "ты супер", "ты космос", "ты огонь", "ты говорил"
        ]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    keywords = []
    for line in lines:
        line = line.strip()
        # Пропускаем пустые строки и комментарии
        if line and not line.startswith('#'):
            keywords.append(line)
    
    logger.info(f"Загружено {len(keywords)} ключевых слов из {filepath}")
    return keywords

def save_keywords(keywords: List[str] = None):
    """
    Сохраняет список ключевых слов в файл
    Если список не передан, используется список по умолчанию
    """
    if keywords is None:
        keywords = [
            "спасиб", "благодар", "признател", "ценю твою", "ценю вашу",
            "ты мне очень помог", "ты мне сильно помог", "ты помог",
            "ты лучший", "ты супер", "ты космос", "ты огонь", "ты говорил"
        ]
    
    filepath = config.KEYWORDS_FILE
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for keyword in keywords:
            f.write(f"{keyword}\n")
    
    logger.info(f"Ключевые слова сохранены в {filepath}")