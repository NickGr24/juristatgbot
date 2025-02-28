import sqlite3
import logging

DB_PATH = "bot_database.db"

def create_tables():
    """Создает таблицы, если их нет"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            time TEXT NOT NULL,
            last_sent_id INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT NOT NULL,
            definition TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def register_user(user_id: int, time: str):
    """Добавляет пользователя, если его еще нет"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, time) VALUES (?, ?)", (user_id, time))
        conn.commit()

    conn.close()

def update_user_time(user_id: int, new_time: str):
    """Обновляет время получения терминов"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET time = ? WHERE user_id = ?", (new_time, user_id))
    conn.commit()
    conn.close()
    logging.info(f"⏰ Время для пользователя {user_id} обновлено на {new_time}")

if __name__ == "__main__":
    create_tables()
    print("База данных успешно создана!")
