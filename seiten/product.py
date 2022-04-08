import streamlit as st
import sqlite3
from matplotlib import pyplot as plt
from datetime import timedelta, date
from operator import itemgetter

TODAY = date.today()
THIS_MONDAY = TODAY - timedelta(days=TODAY.weekday())
LAST_MONDAY = TODAY - timedelta(days=TODAY.weekday(), weeks=1)
DB = f'Products.db'


def remove_duplicates(l: list) -> list:
    l2 = []
    l3 = []
    for element in l:
        if element[0] not in l3:
            l2.append([element[0], element[1]])
            l3.append(element[0])
    return l2


def app(product: str, shop: str, currency: str) -> None:
    SHOP = shop

    # Database Connection
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Write space
    st.write(' ')
    st.write(' ')

    # Create Columns
    space, clm1, clm2, space = st.columns((1, 5, 5, 1))

    # Get Data from DB
    cur.execute(f"SELECT name, price, image FROM {shop} WHERE name = ? AND date = ?", (product, THIS_MONDAY,))
    data = cur.fetchall()

    # Write Data on Website
    clm1.image(data[0][2], width=400)
    clm2.title(data[0][0])
    clm2.header(f'{data[0][1]}  {currency}')
    clm2.write(' ')
    clm2.write(' ')
    clm2.write(' ')
    clm2.write(' ')

    def statistics1():
        # Create Columns
        space, clm1, space, clm2, space = st.columns((1, 5, 1, 5, 1))

        # Line graph price
        # Get Data
        cur.execute(f"SELECT DISTINCT price, date FROM {shop} WHERE name = ?", (product,))
        product_data = cur.fetchall()

        # DATES
        axis_unsorted = [[p_data[1], p_data[0]] for p_data in product_data]
        axis = remove_duplicates(sorted(axis_unsorted, key=itemgetter(0)))

        x_axis = [
            x[0]
            for x in axis
        ]
        # PRICES
        y_axis = [
            float(y[1])
            for y in axis
        ]

        # Plot line chart
        fig, ax = plt.subplots()

        ax.axis([None, None, 0, max(y_axis) + 1])
        ax.fill_between(x_axis, y_axis, color='#59adf6')

        plt.xticks([])
        plt.xlabel('Time')
        plt.ylabel('Price in EUR')
        clm1.pyplot(fig, transparent=True)

        # Crete METRIC
        cur.execute(f"SELECT MAX(price), MIN(price), AVG(price) FROM {shop} WHERE name = ?", (product,))
        max_min = cur.fetchall()

        # Write Metric
        clm2.metric(f'Highest ↗', f'{max_min[0][0]} {currency}')
        clm2.metric(f'Lowest ↘', f'{max_min[0][1]} {currency}')
        clm2.metric(f'Average ↭', f'{round(max_min[0][2], 2)} {currency}')

    statistics1()
