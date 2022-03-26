import requests
import sqlite3
from datetime import date
import json
import csv

# Database Conection
DB = f'Products.db'
conn = sqlite3.connect(DB, check_same_thread=False)
cur = conn.cursor()

# Today
TODAY = date.today().strftime('%Y-%m-%d')

API_URL = "https://api-inference.huggingface.co/models/peter2000/xlm-roberta-base-finetuned-ecoicop"
API_TOKEN = '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'
headers = {"Authorization": f"Bearer {API_TOKEN}"}


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def write_csv(info: str):
    info_list = info.split("*")

    with open('Categories.csv', 'a', encoding='utf8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(info_list)


cur.execute("SELECT name, category FROM aldi WHERE date = ?", (TODAY,))
names = cur.fetchall()
'''
for name in names:
    output = query({"inputs": f"{name[1]} {name[0]}", })
    for product in output:
        score = 0
        label = ''
        print(product)
        for categories in product:
            try:
                if categories.get("score") > score:
                    score = categories.get("score")
                    label = categories.get("label")
            except:
                #print(product)
                continue
        print(f'{name[0]}*{label}*{score}')
'''