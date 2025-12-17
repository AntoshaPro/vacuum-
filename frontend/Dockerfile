FROM node:18-alpine

WORKDIR /app

# Копирование файлов зависимостей
COPY package*.json ./

# Установка зависимостей
RUN npm install

# Копирование исходного кода
COPY . .

# Установка переменных окружения
ENV VITE_API_URL=http://localhost:8000

# Открытие порта
EXPOSE 5173

# Запуск приложения
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]