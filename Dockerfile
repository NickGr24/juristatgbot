# Используем Python 3.12 как базовый образ
FROM python:3.12

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска бота
CMD ["python", "bot.py"]
