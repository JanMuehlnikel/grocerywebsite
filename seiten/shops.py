import streamlit as st
from matplotlib import pyplot as plt
from datetime import datetime, timedelta, date
from PIL import Image
import seiten.product as product_site
import sqlite3


def app(shop: str) -> None:
    # VARIABLES
    SHOP = shop
    DB = f'Products.db'
    IMAGEFILE = f'{SHOP}.png'
    TODAY = date.today().strftime('%Y-%m-%d')
    YESTERDAY = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    COLORS = ['#ff6961', '#ffb480', '#f8f38d', '#42d6a4', '#08cad1', '#59adf6', '#9d94ff', '#c780e8', '#D876AC']

    # Database Conection
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Category List
    CATEGORIES = []
    cur.execute("SELECT DISTINCT category FROM aldi")
    rows = cur.fetchall()
    for row in rows:
        CATEGORIES.append(row[0])

    def data_metric():

        def compare(day):
            cur.execute("SELECT COUNT(name) FROM aldi WHERE date = ?", (day,))
            number_products = cur.fetchall()

            cur.execute("SELECT SUM(price) FROM aldi WHERE date = ?", (day,))
            sum_price = cur.fetchall()

            cur.execute("SELECT COUNT(name) FROM aldi WHERE date = ?", (YESTERDAY,))
            number_products_yesterday = cur.fetchall()


            return [
                number_products[0][0],
                round(sum_price[0][0] / number_products[0][0], 2),
                abs(number_products_yesterday[0][0] - number_products[0][0])
            ]

        number_products_today = compare(TODAY)[0]
        number_products_yesterday = compare(YESTERDAY)[0]
        avg_price_today = compare(TODAY)[1]
        avg_price_yesterday = compare(YESTERDAY)[1]
        changes_today = compare(TODAY)[2]

        # WRITE COLUMNS
        products, avg_price, change = st.columns(3)
        products.metric(f'Number Of Products',
                        f'{number_products_today} Products',
                        f'{round(((number_products_yesterday - number_products_today) / number_products_yesterday) * 100, 2)} %')

        avg_price.metric(f'Average Price', f'{avg_price_today} EUR',
                         f'{round(((avg_price_today - avg_price_yesterday) / avg_price_yesterday) * 100, 2)} %')

        change.metric(f'Price Changes', f'{changes_today} changes')

    def products_table():
        # Sidebar
        st.write(' ')
        st.write(
            '──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────')
        st.write(' ')
        st.title('Product Information')

        space, clm1, space, clm2, space = st.columns((1, 5, 1, 5, 1))

        sb_category = clm1.selectbox('Select category', CATEGORIES, index=0)

        cur.execute("SELECT name, price FROM aldi WHERE category = ? AND date = ?", (sb_category, TODAY,))
        products = cur.fetchall()
        selection = [
            product[0]
            for product in products
        ]
        selection.insert(0, 'show no product')

        sb_product = clm2.selectbox('Select a product see more information', selection, index=0, key=sb_category)

        if sb_product != 'show no product':
            product_site.app(sb_product, SHOP)

        st.write(' ')
        st.write(
            '──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────')
        st.write(' ')

    def statistics_1():
        space, clm1, space, clm2, space = st.columns((1, 5, 1, 5, 1))

        ### MAP ###
        clm1.title('Map')
        clm1.write(' ')
        image = Image.open(IMAGEFILE)
        clm1.image(image, f'All {SHOP.capitalize()} shops in a certain area', width=300)

        ### CATEGROIES PIE CHART ###
        clm2.title('Categories')
        clm1.write(' ')

        # Plot pie chart
        labels = [
            category
            for category in CATEGORIES
        ]
        sizes = []
        for category in CATEGORIES:
            cur.execute("SELECT COUNT(name) FROM aldi WHERE date = ? AND category = ?", (TODAY, category,))
            products_in_category = cur.fetchall()
            sizes.append(products_in_category[0][0])

        colors = ['#ff6961', '#ffb480', '#f8f38d', '#42d6a4', '#08cad1', '#59adf6', '#9d94ff', '#c780e8', '#D876AC']
        explode = [
            0.05
            for i in CATEGORIES
        ]

        fig, ax = plt.subplots()

        ax.pie(
            sizes, colors=colors, autopct='%1.0f%%', pctdistance=1.13, labeldistance=1.2, startangle=90,
            textprops=dict(color="black"), wedgeprops={'linewidth': 0.1, 'edgecolor': 'black'}, explode=explode
        )
        ax.legend(labels=labels, title='Categories', loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        centre_circle = plt.Circle((0, 0), 0.50, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        clm2.pyplot(fig, transparent=True)

    def statistics_2():
        space, clm1, space, clm2, space = st.columns((1, 5, 1, 5, 1))
        ### Line Graph Average Price ###
        clm1.title('Average Price')
        clm1.write(' ')

        cur.execute("SELECT DISTINCT date FROM aldi")
        dates = cur.fetchall()

        x_axis = [
            selected_date[0]
            for selected_date in dates
        ]

        y_axis = []
        for selected_date in dates:
            cur.execute("SELECT SUM(price), COUNT(name) FROM aldi WHERE date = ?", (selected_date[0],))
            sum_prices = cur.fetchall()
            y_axis.append(str(round(sum_prices[0][0] / sum_prices[0][1], 2)))

        # Plot line chart
        fig, ax = plt.subplots()
        ax.plot(x_axis, y_axis, color='#ff6961')
        ax.scatter(x_axis, y_axis, color='#ffb480')
        plt.fill_between(x_axis, y_axis, color='#ffb480')
        plt.xlabel('Time')
        plt.ylabel('Price in EUR')
        clm1.pyplot(fig, transparent=True)

        ### Prices and Categories ###
        clm2.title('Average Price per Category')
        clm2.write(' ')

        y_axis = []
        for category in CATEGORIES:
            cur.execute("SELECT SUM(price), COUNT(name) FROM aldi WHERE category = ? AND date = ?", (category, TODAY))
            prices_and_count = cur.fetchall()

            y_axis.append(round(prices_and_count[0][0] / prices_and_count[0][1], 2))

        fig, ax = plt.subplots()
        ax.barh(CATEGORIES, y_axis, color=COLORS)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        plt.setp(ax.get_yticklabels(), fontsize=10, rotation='horizontal')
        plt.xlabel('Price in EUR')
        clm2.pyplot(fig, transparent=True)

    def placeholder():
        st.write(' ')
        st.write(' ')
        st.write(' ')

    def run():
        st.title(SHOP.capitalize())
        placeholder()
        data_metric()
        placeholder()
        statistics_1()
        statistics_2()
        products_table()

    run()
