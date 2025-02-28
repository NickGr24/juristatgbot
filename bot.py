import asyncio
import logging
import sqlite3
import re
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from database import register_user, update_user_time

# Token-ul botului
TOKEN = "7863600964:AAGEG4Sdhj7ESatcTIFgxwvqujRvJC2Ydvw"

# Creăm botul
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Activăm logarea
logging.basicConfig(level=logging.INFO)

# Conexiune la baza de date
DB_PATH = "bot_database.db"

# Inițializăm programatorul de sarcini
scheduler = AsyncIOScheduler()

# Meniu principal
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📖 Primește un cuvânt")],
        [KeyboardButton(text="🕒 Setează ora de primire a termenilor")],
        [KeyboardButton(text="📚 Lista mea de noțiuni")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(message: types.Message):
    """Înregistrează utilizatorul și afișează mesajul de bun venit"""
    user_id = message.from_user.id
    register_user(user_id, "09:00")  # Ora implicită 09:00

    await message.answer(
    f"👋 Salut, {message.from_user.full_name}!\n\n"
    "📌 <b>Noțiuni Juridice | Academia „Ștefan cel Mare”</b>\n\n"
    "🔹 <b>Ce face acest bot?</b>\n"
    "Acest bot educațional îți oferă definiții zilnice ale termenilor juridici pentru a-ți îmbunătăți cunoștințele în domeniul dreptului. 📚\n\n"
    "💡 <b>Caracteristici principale:</b>\n"
    "✅ <b>Un termen juridic pe zi</b> – Primești automat un termen nou zilnic la ora aleasă de tine.\n"
    "✅ <b>Listă personalizată</b> – Adaugă termenii preferați într-o listă și revizuiește-i oricând dorești.\n"
    "✅ <b>Explorare instantanee</b> – Dacă vrei să înveți mai mult, poți primi termeni suplimentari oricând printr-un simplu click.\n"
    "✅ <b>Interfață prietenoasă</b> – Butoane intuitive pentru a accesa rapid funcțiile principale.\n\n"
    "🎯 <b>Cum să folosești botul?</b>\n"
    "1️⃣ Apasă <b>„📖 Primește un cuvânt”</b> pentru a primi un termen juridic nou.\n"
    "2️⃣ Dacă îți place un termen, apasă <b>„➕ Adaugă în lista mea”</b> pentru a-l salva.\n"
    "3️⃣ Pentru a vedea toate termenii salvați, apasă <b>„📚 Lista mea de noțiuni”</b>.\n"
    "4️⃣ Dacă dorești să elimini un termen, apasă <b>„🗑 Elimină din listă”</b>.\n"
    "5️⃣ Setează ora la care dorești să primești termenii zilnici folosind <b>„🕒 Setează ora de primire a termenilor”</b>.",
    reply_markup=main_keyboard
)

@dp.message(lambda message: message.text == "🕒 Setează ora de primire a termenilor")
async def set_time_button(message: types.Message):
    """Când utilizatorul apasă butonul pentru a seta ora"""
    user_id = message.from_user.id
    await message.answer("📅 Introdu ora în format HH:MM (ex: 14:30).")

@dp.message(lambda message: re.match(r"^([0-9]{1,2}):([0-9]{2})$", message.text))
async def save_time(message: types.Message):
    """Salvează ora introdusă de utilizator"""
    user_id = message.from_user.id
    time_text = message.text.strip()

    hour, minute = map(int, time_text.split(":"))
    if hour > 23 or minute > 59:
        await message.answer("⚠️ Ora introdusă este incorectă. Orele trebuie să fie între 00-23, iar minutele între 00-59.")
        return

    time_text = f"{hour:02}:{minute:02}"

    # Actualizăm ora în baza de date
    update_user_time(user_id, time_text)
    reschedule_jobs()

    await message.answer(f"✅ Ora de primire a termenilor a fost setată la {time_text}.")

@dp.message(lambda message: message.text == "📖 Primește un cuvânt")
async def receive_word(message: types.Message):
    """Trimite imediat un termen juridic utilizatorului"""
    user_id = message.from_user.id
    await send_daily_term(user_id)

async def send_daily_term(user_id: int):
    """Trimite utilizatorului un termen cu butoane"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT last_sent_id FROM users WHERE user_id = ?", (user_id,))
    last_sent_id = cursor.fetchone()[0]

    cursor.execute("SELECT id, term, definition FROM words WHERE id > ? ORDER BY id ASC LIMIT 1", (last_sent_id,))
    term_data = cursor.fetchone()

    if term_data:
        term_id, term, definition = term_data

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="➕ Adaugă în lista mea", callback_data=f"add_{term_id}")],
            [InlineKeyboardButton(text="🗑 Elimină din listă", callback_data=f"del_{term_id}")],
        ])

        await bot.send_message(user_id, f"📖 <b>{term}</b>\n{definition}", reply_markup=keyboard)

        cursor.execute("UPDATE users SET last_sent_id = ? WHERE user_id = ?", (term_id, user_id))
        conn.commit()

    conn.close()

def reschedule_jobs():
    """Repornește sarcinile programate"""
    scheduler.remove_all_jobs()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, time FROM users")
    users = cursor.fetchall()

    for user_id, send_time in users:
        hour, minute = map(int, send_time.split(":"))
        scheduler.add_job(send_daily_term, "cron", hour=hour, minute=minute, args=[user_id])
        logging.info(f"⏳ Programată trimiterea pentru {user_id} la {send_time}")

    conn.close()

    if not scheduler.running:
        scheduler.start()

@dp.callback_query(lambda c: c.data.startswith("add_"))
async def add_to_my_words(callback: types.CallbackQuery):
    """Adaugă un termen în lista utilizatorului"""
    user_id = callback.from_user.id
    word_id = int(callback.data.split("_")[1])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            word_id INTEGER
        )
    """)

    cursor.execute("SELECT * FROM user_words WHERE user_id = ? AND word_id = ?", (user_id, word_id))
    exists = cursor.fetchone()

    if not exists:
        cursor.execute("INSERT INTO user_words (user_id, word_id) VALUES (?, ?)", (user_id, word_id))
        conn.commit()
        await callback.answer("✅ Cuvântul a fost adăugat în lista ta.", show_alert=True)
    else:
        await callback.answer("⚠️ Acest cuvânt este deja în lista ta.", show_alert=True)

    conn.close()

@dp.callback_query(lambda c: c.data.startswith("del_"))
async def delete_from_my_words(callback: types.CallbackQuery):
    """Elimină un termen din lista utilizatorului"""
    user_id = callback.from_user.id
    word_id = int(callback.data.split("_")[1])

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_words WHERE user_id = ? AND word_id = ?", (user_id, word_id))
    conn.commit()
    conn.close()

    await callback.answer("🗑 Cuvântul a fost eliminat din lista ta.", show_alert=True)


@dp.message(lambda message: message.text == "📚 Lista mea de noțiuni")
async def show_my_words(message: types.Message):
    """Afișează lista de cuvinte salvate"""
    user_id = message.from_user.id

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            word_id INTEGER
        )
    """)

    cursor.execute("""
        SELECT words.term, words.definition, words.id FROM user_words
        JOIN words ON user_words.word_id = words.id
        WHERE user_words.user_id = ?
    """, (user_id,))
    
    words = cursor.fetchall()
    conn.close()

    if not words:
        await message.answer("📭 Lista ta este goală. Adaugă noțiuni apăsând '➕ Adaugă în lista mea'.")
        return

    for term, definition, word_id in words:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🗑 Elimină din listă", callback_data=f"del_{word_id}")]
        ])
        await message.answer(f"📖 <b>{term}</b>\n{definition}", reply_markup=keyboard)
        
async def main():
    """Pornirea botului"""
    reschedule_jobs()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())