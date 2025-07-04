import sqlite3

def connect_db():
    return sqlite3.connect('embroidery.db')

def insert_design(img_filename, design_text):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO designs (img_name, design_text) VALUES (?, ?)", (img_filename, design_text))
    conn.commit()
    conn.close()

def search_in_db(query_text):
    conn = connect_db()
    cursor = conn.cursor()
    search_term = f'%{query_text}%'
    cursor.execute("SELECT * FROM designs WHERE design_text LIKE ?", (search_term,))
    results = cursor.fetchall()
    conn.close()
    return results
