import sqlite3
from random import random


def create_connection():
    return sqlite3.connect('my_database.db')

def find_user(tg_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE tg_id = ?', (tg_id,))
    if cursor.fetchone():
        return True
    conn.close()



def get_random_year_for_user(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    print(user_id)

    cursor.execute('SELECT year_start, year_end FROM Years WHERE user_id = ?', (user_id,))
    intervals = cursor.fetchall()
    print(intervals)

    conn.close()

    if not intervals:
        return None

    random_interval = random.choice(intervals)

    random_year = random.randint(random_interval[0], random_interval[1])

    return random_year

def get_random_country_for_user(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    query = """
    SELECT name FROM Countries 
    WHERE user_id = ? 
    ORDER BY RANDOM() 
    LIMIT 1
    """
    cursor.execute(query, (user_id,))

    result = cursor.fetchone()

    if result:
        return result[0]
    conn.close()

def add_user(tg_id):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Users WHERE tg_id = ?', (tg_id,))
    count = cursor.fetchone()

    if not count:
        cursor.execute('INSERT INTO Users(tg_id) VALUES (?)', (tg_id,))
        conn.commit()

    conn.close()


def add_country(tg_id, country_name):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Countries WHERE user_id = ? AND name = ?', (tg_id, country_name))
    count = cursor.fetchone()

    if not count:
        cursor.execute('INSERT INTO Countries(user_id, name) VALUES (?, ?)', (tg_id, country_name))
        conn.commit()

    conn.close()


def add_time_interval(user_id, year_start, year_end):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM Years WHERE user_id = ? AND year_start = ? AND year_end = ?',
                   (user_id, year_start, year_end))
    count = cursor.fetchone()


    if not count :
        cursor.execute('INSERT INTO Years(user_id, year_start, year_end) VALUES (?, ?, ?)',
                       (user_id, year_start, year_end))
        conn.commit()
    conn.close()

connection = create_connection()

cursor = connection.cursor()

cursor.execute('''
SELECT year_start, year_end FROM Years WHERE user_id = 449408221
''')
print(cursor.fetchone())


#cursor.execute('''
    #DROP TABLE IF EXISTS Users ''')

#cursor.execute('''
    #DROP TABLE IF EXISTS Countries ''')


#cursor.execute('''
    #DROP TABLE IF EXISTS Years''')



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
