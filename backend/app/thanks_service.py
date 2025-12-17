from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from telethon import TelegramClient
from telethon.tl.types import User, Chat, Channel
from telethon.errors import PeerIdInvalidError
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThankMessage(BaseModel):
    """
    Модель сообщения с благодарностью
    """
    id: int
    chat_id: int
    chat_name: str
    username: Optional[str] = None
    date: str  # ISO формат даты
    text: str
    peer_type: str  # 'user', 'chat', 'channel'

async def search_thanks(
    client: TelegramClient,
    keywords: List[str],
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    limit_per_dialog: Optional[int] = None
) -> List[ThankMessage]:
    """
    Поиск сообщений с благодарностями в диалогах
    Возвращает уникальный список сообщений с благодарностями
    """
    found_messages = []
    seen_message_ids = set()  # Для отслеживания уникальных сообщений
    
    logger.info(f"Начинается поиск благодарностей по {len(keywords)} ключевым словам...")
    
    # Проходим по всем диалогам
    async for dialog in client.iter_dialogs():
        # Оставляем только приватные чаты с пользователями, исключая ботов
        if isinstance(dialog.entity, User) and not dialog.entity.bot:
            logger.info(f"Поиск в диалоге: {dialog.name} (ID: {dialog.id})")
            
            for keyword in keywords:
                try:
                    # Ищем сообщения с ключевым словом в указанном диапазоне дат
                    async for msg in client.iter_messages(
                        dialog.id,
                        search=keyword,
                        min_date=from_date,
                        max_date=to_date,
                        reverse=False,  # Новые сообщения первыми
                        limit=limit_per_dialog
                    ):
                        # Учитываем только входящие сообщения с текстом
                        if msg.out or not msg.text:
                            continue
                        
                        # Проверяем, что это сообщение еще не было добавлено
                        if msg.id not in seen_message_ids:
                            seen_message_ids.add(msg.id)
                            
                            # Определяем тип пира
                            peer_type = 'user'
                            if isinstance(dialog.entity, Chat):
                                peer_type = 'chat'
                            elif isinstance(dialog.entity, Channel):
                                peer_type = 'channel'
                            
                            thank_msg = ThankMessage(
                                id=msg.id,
                                chat_id=dialog.id,
                                chat_name=dialog.name,
                                username=getattr(dialog.entity, 'username', None),
                                date=msg.date.isoformat(),
                                text=msg.text,
                                peer_type=peer_type
                            )
                            
                            found_messages.append(thank_msg)
                            logger.debug(f"Найдено сообщение с благодарностью: {msg.text[:50]}...")
                            
                except Exception as e:
                    logger.error(f"Ошибка при поиске по ключевому слову '{keyword}' в диалоге {dialog.name}: {e}")
                    continue
    
    logger.info(f"Найдено {len(found_messages)} уникальных сообщений с благодарностями")
    return found_messages

def write_results_to_file(messages: List[ThankMessage], filename: str = None):
    """
    Записывает результаты поиска в файл в человекочитаемом формате
    """
    from .config import config
    
    if filename is None:
        filename = config.OUTPUT_FILE
    
    with open(filename, 'w', encoding='utf-8') as f:
        for msg in messages:
            f.write("=========================\n")
            f.write(f"[{msg.date}] chat={msg.chat_name} user={msg.username or 'N/A'} ({msg.chat_id}) : {msg.text}\n\n")
    
    logger.info(f"Результаты записаны в файл: {filename}")

async def send_thanks(
    client: TelegramClient,
    messages: List[ThankMessage],
    dest: str,
    mode: str = "forward"
):
    """
    Отправляет/пересылает выбранные сообщения в указанный чат
    dest: имя пользователя или ID
    mode: "forward" - переслать, "copy" - скопировать текст
    """
    try:
        # Решаем, куда отправлять
        entity = await client.get_entity(dest)
    except PeerIdInvalidError:
        logger.error(f"Не удалось найти получателя: {dest}")
        return {"success": False, "error": f"Не удалось найти получателя: {dest}"}
    except Exception as e:
        logger.error(f"Ошибка при разрешении получателя {dest}: {e}")
        return {"success": False, "error": str(e)}
    
    successful_count = 0
    failed_count = 0
    errors = []
    
    for msg in messages:
        try:
            if mode == "forward":
                # Пересылаем сообщение
                await client.forward_messages(entity, msg.id, from_peer=msg.chat_id)
            elif mode == "copy":
                # Копируем текст сообщения
                formatted_text = f"[{msg.date}] {msg.chat_name} ({msg.username or 'N/A'}): {msg.text}"
                await client.send_message(entity, formatted_text)
            else:
                raise ValueError(f"Неизвестный режим: {mode}")
            
            successful_count += 1
            
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения {msg.id}: {e}")
            errors.append(f"Сообщение {msg.id}: {str(e)}")
            failed_count += 1
    
    result = {
        "success": True,
        "successful": successful_count,
        "failed": failed_count,
        "total_processed": len(messages),
        "errors": errors
    }
    
    logger.info(f"Отправка завершена. Успешно: {successful_count}, Неудачно: {failed_count}")
    return result