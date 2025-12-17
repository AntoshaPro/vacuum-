import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

class Config:
    """
    Конфигурация приложения для работы с Telegram API
    """
    def __init__(self):
        # Получаем или запрашиваем у пользователя ключи API
        self.TG_API_ID = self._get_or_ask('TG_API_ID', int, 'Введите TG_API_ID (получить можно на https://my.telegram.org): ')
        self.TG_API_HASH = self._get_or_ask('TG_API_HASH', str, 'Введите TG_API_HASH (получить можно на https://my.telegram.org): ')
        self.TG_SESSION_NAME = os.getenv('TG_SESSION_NAME', 'my_session')
        self.OUTPUT_FILE = os.getenv('OUTPUT_FILE', 'thanks_dialogs.txt')
        self.KEYWORDS_FILE = os.getenv('KEYWORDS_FILE', 'keywords.txt')

    def _get_or_ask(self, key, expected_type, prompt):
        """Проверяет наличие переменной окружения и запрашивает у пользователя при отсутствии"""
        value = os.getenv(key)
        if not value:
            # Проверяем, можем ли мы получить ввод от пользователя (не в контейнере или в интерактивном режиме)
            import sys
            if sys.stdin.isatty():
                # Работает в интерактивном режиме
                value = input(prompt)
                # Сохраняем в .env файл
                with open('.env', 'a') as f:
                    f.write(f'{key}={value}\n')
            else:
                # Работает в контейнере или без возможности ввода
                raise ValueError(f"{key} не задан. Пожалуйста, установите переменную окружения {key}.")
        
        if expected_type == int:
            try:
                return int(value)
            except ValueError:
                print(f'Ошибка: значение {key} должно быть числом')
                raise
        else:
            return value

    def update_config(self, **kwargs):
        """Обновляет конфигурацию и сохраняет в .env файл"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                
        # Обновляем .env файл
        env_vars = {}
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                for line in f:
                    if '=' in line:
                        k, v = line.split('=', 1)
                        env_vars[k.strip()] = v.strip()
        
        # Обновляем значения
        env_vars.update({
            'TG_API_ID': str(self.TG_API_ID),
            'TG_API_HASH': str(self.TG_API_HASH),
            'TG_SESSION_NAME': str(self.TG_SESSION_NAME),
            'OUTPUT_FILE': str(self.OUTPUT_FILE),
            'KEYWORDS_FILE': str(self.KEYWORDS_FILE)
        })
        
        # Перезаписываем файл
        with open('.env', 'w') as f:
            for k, v in env_vars.items():
                f.write(f'{k}={v}\n')

# Глобальный экземпляр конфигурации
config = Config()