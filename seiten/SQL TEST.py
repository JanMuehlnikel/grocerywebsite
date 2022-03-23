import sqlite3

conn = sqlite3.connect('C:/Users/UserNA6153/PycharmProjects/GIZ_Projects/groceryscraper/Products.db')
cur = conn.cursor()

cur.execute("""SELECT price FROM aldi""")
rows = cur.fetchall()

for row in rows:
    print(row)