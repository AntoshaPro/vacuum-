from telethon import TelegramClient
from .config import config
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальная переменная для хранения клиента
_telegram_client = None
_authorization_phone = None
_authorization_hash = None
_authorization_in_progress = False

def get_client():
    """
    Возвращает singleton-экземпляр Telegram клиента
    Использует сессию из файла для повторного использования между запусками
    """
    global _telegram_client
    
    if _telegram_client is None:
        logger.info("Инициализация нового Telegram клиента")
        try:
            _telegram_client = TelegramClient(
                config.TG_SESSION_NAME,
                config.TG_API_ID,
                config.TG_API_HASH
            )
        except ValueError as e:
            logger.error(f"Ошибка инициализации клиента: {e}")
            raise
        except Exception as e:
            logger.error(f"Неизвестная ошибка при инициализации клиента: {e}")
            raise
    
    return _telegram_client

async def is_authorized():
    """
    Проверяет, авторизован ли клиент в Telegram
    """
    try:
        client = get_client()
        await client.get_me()
        return True
    except ValueError:
        # Credentials are missing
        return False
    except Exception:
        return False

async def start_authorization(phone_number: str):
    """
    Начинает процесс авторизации в Telegram
    """
    global _authorization_phone, _authorization_hash, _authorization_in_progress
    try:
        client = get_client()
        
        # Проверяем, уже ли авторизованы
        if await is_authorized():
            return {"status": "already_authorized", "message": "Уже авторизованы"}
        
        # Начинаем процесс авторизации
        _authorization_in_progress = True
        
        # Подключаемся к Telegram
        if not await client.is_connected():
            await client.connect()
        
        # Проверяем, нужна ли регистрация
        if not await client.is_user_authorized():
            # Отправляем код подтверждения
            _authorization_phone = phone_number
            sent_code = await client.send_code_request(phone_number)
            _authorization_hash = sent_code.phone_code_hash
            
            return {
                "status": "waiting_code", 
                "message": "Код подтверждения отправлен на ваш номер. Ожидание ввода кода...",
                "phone": phone_number
            }
        else:
            _authorization_in_progress = False
            return {"status": "already_authorized", "message": "Уже авторизованы"}
    
    except Exception as e:
        _authorization_in_progress = False
        _authorization_phone = None
        _authorization_hash = None
        logger.error(f"Ошибка при начале авторизации: {e}")
        return {"status": "error", "message": str(e)}

async def complete_authorization(code: str):
    """
    Завершает процесс авторизации, используя полученный код
    """
    global _authorization_phone, _authorization_hash, _authorization_in_progress
    try:
        client = get_client()
        
        if not _authorization_in_progress or not _authorization_phone:
            return {"status": "error", "message": "Процесс авторизации не начат"}
        
        # Завершаем авторизацию с помощью кода
        await client.sign_in(_authorization_phone, code)
        
        _authorization_in_progress = False
        _authorization_phone = None
        _authorization_hash = None
        
        if await is_authorized():
            return {"status": "success", "message": "Авторизация успешна"}
        else:
            return {"status": "error", "message": "Не удалось завершить авторизацию"}
    
    except Exception as e:
        _authorization_in_progress = False
        _authorization_phone = None
        _authorization_hash = None
        logger.error(f"Ошибка при завершении авторизации: {e}")
        return {"status": "error", "message": f"Ошибка авторизации: {str(e)}"}