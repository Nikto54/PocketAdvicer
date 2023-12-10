import sqlite3

def create_connection():
    return sqlite3.connect('my_database.db')


def add_user(tg_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM Users WHERE tg_id = ?', (tg_id,))
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute('INSERT INTO Users(tg_id) VALUES (?)', (tg_id,))
        conn.commit()

    conn.close()


def add_country(tg_id, country_name):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM Countries WHERE user_id = ? AND name = ?', (tg_id, country_name))
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute('INSERT INTO Countries(user_id, name) VALUES (?, ?)', (tg_id, country_name))
        conn.commit()

    conn.close()


def add_time_interval(user_id, year_start, year_end):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM Years WHERE user_id = ? AND year_start = ? AND year_end = ?',
                   (user_id, year_start, year_end))
    count = cursor.fetchone()[0]


    if count == 0:
        cursor.execute('INSERT INTO Years(user_id, year_start, year_end) VALUES (?, ?, ?)',
                       (user_id, year_start, year_end))
        conn.commit()
    conn.close()

connection = create_connection()

cursor = connection.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
     id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,                                
    tg_id INTEGER UNIQUE NOT NULL
)
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Countries (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    user_id INTEGER,
    name TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES Users(tg_id)
)
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Years (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    user_id INTEGER,
    year_start INTEGER UNIQUE NOT NULL,
    year_end INTEGER UNIQUE NOT NULL,
    FOREIGN KEY(user_id) REFERENCES Users(tg_id)
)
''')

connection.commit()
connection.close()
