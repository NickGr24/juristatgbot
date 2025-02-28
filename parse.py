import sqlite3
from bs4 import BeautifulSoup

html_file = "/mnt/data/defs.html"
conn = sqlite3.connect("bot_database.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        term TEXT NOT NULL,
        definition TEXT NOT NULL
    )
""")

with open(html_file, "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

terms = []
for term_tag in soup.find_all("strong"):
    term = term_tag.text.strip()
    definition = term_tag.next_sibling.strip() if term_tag.next_sibling else ""

    if definition.startswith("&#8211;"):
        definition = definition.replace("&#8211;", "").strip()

    if term and definition:
        terms.append((term, definition))

cursor.executemany("INSERT INTO words (term, definition) VALUES (?, ?)", terms)
conn.commit()
conn.close()

print(f"✅ Успешно добавлено {len(terms)} терминов в базу данных.")
