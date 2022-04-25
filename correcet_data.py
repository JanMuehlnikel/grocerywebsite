from datetime import timedelta, date
import sqlite3

TODAY = date.today()
THIS_MONDAY = TODAY - timedelta(days=TODAY.weekday())
LAST_MONDAY = TODAY - timedelta(days=TODAY.weekday(), weeks=1)

dates = ['2022-04-18', '2022-04-11']
shops = ['aldi', 'carrefour_cote_divoire']

min_score = '2022-03-28'

conn = sqlite3.connect('Products.db')
cur = conn.cursor()
cur.execute(f"DELETE FROM {shops[1]} WHERE date = ?", (min_score,))
conn.commit()