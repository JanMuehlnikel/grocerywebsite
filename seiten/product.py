import streamlit as st
import sqlite3
from matplotlib import pyplot as plt
from datetime import date

TODAY = date.today().strftime('%Y-%m-%d')


def app(product: str, shop: str) -> None:
    # Database Connection
    conn = sqlite3.connect('C:/Users/UserNA6153/PycharmProjects/GIZ_Projects/groceryscraper/Products.db')
    cur = conn.cursor()

    # Write space
    st.write(' ')
    st.write(' ')

    # Create Columns
    space, clm1, clm2, space = st.columns((1, 5, 5, 1))

    # Get Data from DB
    cur.execute(f"SELECT name, price, image FROM {shop} WHERE name = ? AND date = ?", (product, TODAY,))
    data = cur.fetchall()

    # Write Data on Website
    clm1.image(data[0][2], width=400)
    clm2.title(data[0][0])
    clm2.header(f'{data[0][1]}  EUR')
    clm2.write(' ')
    clm2.write(' ')
    clm2.write(' ')
    clm2.write(' ')

    def statistics1():
        # Create Columns
        space, clm1, space, clm2, space = st.columns((1, 5, 1, 5, 1))

        # Line graph price
        # Get Data
        cur.execute(f"SELECT price, date FROM {shop} WHERE name = ?", (product,))
        product_data = cur.fetchall()

        # DATES
        x_axis = [
            data[1]
            for data in product_data
        ]
        # PRICES
        y_axis = [
            data[0]
            for data in product_data
        ]

        # Plot line chart
        fig, ax = plt.subplots()
        ax.plot(x_axis, y_axis, color='#ff6961')
        ax.scatter(x_axis, y_axis, color='#ffb480')
        plt.fill_between(x_axis, y_axis, color='#ffb480')
        plt.xlabel('Time')
        plt.ylabel('Price in EUR')
        clm1.pyplot(fig, transparent=True)

        # Crete METRIC
        cur.execute(f"SELECT MAX(price), MIN(price), AVG(price) FROM {shop} WHERE name = ?", (product,))
        max_min = cur.fetchall()

        # Write Metric
        clm2.metric(f'Highest', f'{max_min[0][0]} EUR')
        clm2.metric(f'Lowest', f'{max_min[0][1]} EUR')
        clm2.metric(f'Average', f'{round(max_min[0][2], 2)} EUR')

    statistics1()



