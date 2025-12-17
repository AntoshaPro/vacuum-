from telethon import TelegramClient
from .config import config
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальная переменная для хранения клиента
_telegram_client = None

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