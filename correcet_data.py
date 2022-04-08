from datetime import timedelta, date
import sqlite3
from transformers import pipeline

conn = sqlite3.connect('old_Products.db')
cur = conn.cursor()

TODAY = date.today()
THIS_MONDAY = TODAY - timedelta(days=TODAY.weekday())
LAST_MONDAY = TODAY - timedelta(days=TODAY.weekday(), weeks=1)

print(THIS_MONDAY, LAST_MONDAY)
dates = [LAST_MONDAY, THIS_MONDAY]
shops = ['aldi', 'carrefour_cote_divoire']

#API
finetuned_checkpoint = "peter2000/xlm-roberta-base-finetuned-ecoicop"
classifier = pipeline("text-classification", model=finetuned_checkpoint)
print('API LOAD')


def crate_table(store):
    conn1 = sqlite3.connect('Products.db')
    cur1 = conn1.cursor()

    cur1.execute(f"""CREATE TABLE IF NOT EXISTS {store}(
    name text,
    category text,
    price text,
    image text,
    date text,
    label,
    score
    )""")


for shop in shops:
    crate_table(shop)
    for date in dates:
        conn = sqlite3.connect('old_Products.db')
        cur = conn.cursor()
        cur.execute(f"SELECT name, category, price, image, date FROM {shop} WHERE date = ?", (date,))
        rows = cur.fetchall()

        for row in rows:
            cla = classifier(f'{row[1]} <sep> {row[0]} <sep> {row[1]}')

            conn1 = sqlite3.connect('Products.db')
            cur1 = conn1.cursor()
            cur1.execute(f"""INSERT OR IGNORE INTO {shop} VALUES(?,?,?,?,?,?,?)""",
                             (row[0],
                              row[1],
                              row[2],
                              row[3],
                              row[4],
                              cla[0].get('label'),
                              cla[0].get('score')))
            conn1.commit()

            print(row[0],
                              row[1],
                              row[2],
                              row[3],
                              row[4],
                              cla[0].get('label'),
                              cla[0].get('score'))
