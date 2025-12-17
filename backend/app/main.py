from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import asyncio
import logging

from .config import config
from .tg_client import get_client, is_authorized
from .keywords import load_keywords, save_keywords
from .thanks_service import search_thanks, write_results_to_file, send_thanks, ThankMessage

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Telegram Thanks Extractor API", version="1.0.0")

# Настройка CORS для взаимодействия с фронтендом
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене нужно указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    """
    Модель запроса для поиска сообщений
    """
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    limit_per_dialog: Optional[int] = None

class SendRequest(BaseModel):
    """
    Модель запроса для отправки сообщений
    """
    message_ids: List[int]
    dest: str
    mode: str  # "forward" или "copy"

class UpdateConfigRequest(BaseModel):
    """
    Модель запроса для обновления конфигурации
    """
    TG_API_ID: Optional[int] = None
    TG_API_HASH: Optional[str] = None
    TG_SESSION_NAME: Optional[str] = None
    OUTPUT_FILE: Optional[str] = None
    KEYWORDS_FILE: Optional[str] = None

class ConfigResponse(BaseModel):
    """
    Модель ответа с конфигурацией (с маскировкой чувствительных данных)
    """
    TG_API_ID: int
    TG_API_HASH: str
    TG_SESSION_NAME: str
    OUTPUT_FILE: str
    KEYWORDS_FILE: str

@app.on_event("startup")
async def startup_event():
    """
    Инициализация при старте приложения
    """
    logger.info("Инициализация приложения...")
    try:
        client = get_client()
        # Не подключаемся сразу, а проверим при необходимости
        logger.info("Приложение инициализировано")
    except ValueError as e:
        logger.warning(f"Предупреждение при инициализации: {e}")
        # Продолжаем работу, но с возможностью настроить конфиг через API
    except Exception as e:
        logger.error(f"Ошибка при инициализации: {e}")
        raise

@app.get("/api/status")
async def get_status():
    """
    Возвращает статус приложения и состояние подключения к Telegram
    """
    client = get_client()
    auth_status = await is_authorized()
    
    return {
        "status": "ok",
        "version": "1.0.0",
        "telegram_connected": auth_status,
        "message": "Сервер работает нормально" if auth_status else "Требуется авторизация в Telegram"
    }

@app.get("/api/config")
async def get_config():
    """
    Возвращает текущую конфигурацию с маскировкой чувствительных данных
    """
    # Маскируем большую часть API HASH
    masked_hash = config.TG_API_HASH[:3] + "***" + config.TG_API_HASH[-3:] if config.TG_API_HASH else ""
    
    return ConfigResponse(
        TG_API_ID=config.TG_API_ID,
        TG_API_HASH=masked_hash,
        TG_SESSION_NAME=config.TG_SESSION_NAME,
        OUTPUT_FILE=config.OUTPUT_FILE,
        KEYWORDS_FILE=config.KEYWORDS_FILE
    )

@app.post("/api/config")
async def update_config(request: UpdateConfigRequest):
    """
    Обновляет конфигурацию и сохраняет в .env файл
    """
    try:
        # Обновляем конфигурацию
        updates = request.dict(exclude_unset=True)
        config.update_config(**updates)
        
        # Перезагружаем клиента если изменились ключи API
        if 'TG_API_ID' in updates or 'TG_API_HASH' in updates:
            global _telegram_client
            _telegram_client = None  # Сбросим глобальный клиент
        
        return {"message": "Конфигурация успешно обновлена"}
    except Exception as e:
        logger.error(f"Ошибка при обновлении конфигурации: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка обновления конфигурации: {str(e)}")

@app.get("/api/keywords")
async def get_keywords():
    """
    Возвращает текущий список ключевых слов
    """
    try:
        keywords = load_keywords()
        return {"keywords": keywords}
    except Exception as e:
        logger.error(f"Ошибка при загрузке ключевых слов: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки ключевых слов: {str(e)}")

@app.post("/api/keywords")
async def update_keywords(keywords: List[str]):
    """
    Обновляет список ключевых слов
    """
    try:
        save_keywords(keywords)
        return {"message": "Ключевые слова успешно обновлены"}
    except Exception as e:
        logger.error(f"Ошибка при сохранении ключевых слов: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка сохранения ключевых слов: {str(e)}")

@app.post("/api/search")
async def search_thanks_endpoint(request: SearchRequest):
    """
    Выполняет поиск сообщений с благодарностями
    """
    try:
        # Преобразуем даты из строк в datetime объекты
        from_date = datetime.fromisoformat(request.from_date.replace('Z', '+00:00')) if request.from_date else None
        to_date = datetime.fromisoformat(request.to_date.replace('Z', '+00:00')) if request.to_date else None
        
        # Получаем клиента и ключевые слова
        client = get_client()
        keywords = load_keywords()
        
        # Проверяем авторизацию
        if not await is_authorized():
            raise HTTPException(status_code=401, detail="Требуется авторизация в Telegram")
        
        # Выполняем поиск
        messages = await search_thanks(
            client=client,
            keywords=keywords,
            from_date=from_date,
            to_date=to_date,
            limit_per_dialog=request.limit_per_dialog
        )
        
        # Записываем результаты в файл
        write_results_to_file(messages)
        
        return messages
    except Exception as e:
        logger.error(f"Ошибка при поиске благодарностей: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")

@app.post("/api/send")
async def send_thanks_endpoint(request: SendRequest):
    """
    Отправляет/пересылает выбранные сообщения
    """
    try:
        # Получаем клиента
        client = get_client()
        
        # Проверяем авторизацию
        if not await is_authorized():
            raise HTTPException(status_code=401, detail="Требуется авторизация в Telegram")
        
        # Фильтруем сообщения по ID
        # Так как мы не можем получить полные объекты ThankMessage из базы, 
        # выполним новый поиск и фильтруем по ID
        all_keywords = load_keywords()
        all_messages = await search_thanks(client, all_keywords)
        selected_messages = [msg for msg in all_messages if msg.id in request.message_ids]
        
        if not selected_messages:
            raise HTTPException(status_code=404, detail="Выбранные сообщения не найдены")
        
        # Выполняем отправку
        result = await send_thanks(
            client=client,
            messages=selected_messages,
            dest=request.dest,
            mode=request.mode
        )
        
        return result
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщений: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка отправки: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)