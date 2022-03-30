import streamlit as st
from matplotlib import pyplot as plt
from datetime import datetime, timedelta, date
import matplotlib.dates
import seiten.product as product_site
from PIL import Image
import sqlite3
from operator import itemgetter


def app(shop: str, currency: str) -> None:
    # VARIABLES
    SHOP = shop
    DB = f'Products.db'
    CURRENCY = currency
    IMAGEFILE = f'{SHOP}.png'
    TODAY = date.today().strftime('%Y-%m-%d')
    YESTERDAY = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    COLORS = ['#ff6961', '#ffb480', '#f8f38d', '#42d6a4', '#08cad1', '#59adf6', '#9d94ff', '#c780e8', '#D876AC']

    # Database Conection
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Category List
    CATEGORIES = []
    cur.execute(f"SELECT DISTINCT category FROM {SHOP}")
    rows = cur.fetchall()
    for row in rows:
        CATEGORIES.append(row[0])

    def data_metric():

        def compare(day):
            cur.execute(f"SELECT COUNT(name) FROM {SHOP} WHERE date = ?", (day,))
            number_products = cur.fetchall()

            cur.execute(f"SELECT SUM(price) FROM {SHOP} WHERE date = ?", (day,))
            sum_price = cur.fetchall()

            cur.execute(f"SELECT price, name FROM {SHOP} WHERE date = ?", (TODAY,))
            prices_td = cur.fetchall()

            changes = 0
            for p in prices_td:
                cur.execute(f"SELECT price FROM {SHOP} WHERE name = ?", (p[1],))
                prices_yd = cur.fetchall()
                if p[0] != prices_yd[0][0]:
                    changes += 1
            try:
                return [
                    number_products[0][0],
                    round(sum_price[0][0] / number_products[0][0], 2),
                    changes
                ]
            except:
                return [1, 1, 1]

        number_products_today = compare(TODAY)[0]
        number_products_yesterday = compare(YESTERDAY)[0]
        avg_price_today = compare(TODAY)[1]
        avg_price_yesterday = compare(YESTERDAY)[1]
        changes_today = compare(TODAY)[2]

        # WRITE COLUMNS
        products, avg_price, change = st.columns(3)
        products.metric(f'Number Of Products',
                        f'{number_products_today} Products',
                        f'{round(((number_products_today - number_products_yesterday) / number_products_yesterday) * 100, 2)} %')

        avg_price.metric(f'Average Price', f'{avg_price_today} {CURRENCY}',
                         f'{round(((avg_price_today - avg_price_yesterday) / avg_price_yesterday) * 100, 2)} %')

        change.metric(f'Price Changes', f'{changes_today} changes', f'since {YESTERDAY}')

    def products_table():
        # Sidebar
        st.write(' ')
        st.write(
            '──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────')
        st.write(' ')
        st.title('Product Information')

        space, clm1, space, clm2, space = st.columns((1, 5, 1, 5, 1))

        sb_category = clm1.selectbox('Select category', CATEGORIES, index=0)

        cur.execute(f"SELECT name, price FROM {SHOP} WHERE category = ? AND date = ?", (sb_category, TODAY,))
        products = cur.fetchall()
        selection = [
            product[0]
            for product in products
        ]
        selection.insert(0, 'show no product')

        sb_product = clm2.selectbox('Select a product see more information', selection, index=0, key=sb_category)

        if sb_product != 'show no product':
            product_site.app(sb_product, SHOP, CURRENCY)

        st.write(' ')
        st.write(
            '──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────')
        st.write(' ')

    def statistics_1():
        space, clm1, space, clm2, space = st.columns((1, 5, 1, 5, 1))

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
            cur.execute(f"SELECT COUNT(name) FROM {SHOP} WHERE date = ? AND category = ?", (TODAY, category,))
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

        cur.execute(f"SELECT DISTINCT date FROM {SHOP}")
        dates = cur.fetchall()

        x_axis = [
            matplotlib.dates.datestr2num(selected_date[0])
            for selected_date in dates
        ]

        y_axis = []
        for selected_date in dates:
            cur.execute(f"SELECT SUM(price), COUNT(name) FROM {SHOP} WHERE date = ?", (selected_date[0],))
            sum_prices = cur.fetchall()
            if sum_prices[0][0] and sum_prices[0][1] is not None:
                y_axis.append(float(round(sum_prices[0][0] / sum_prices[0][1], 2)))


        # Plot line chart
        fig, ax = plt.subplots()

        ax.plot_date(x_axis, y_axis, color='#ff6961')
        ax.scatter(x_axis, y_axis, color='#ffb480')
        ax.axis([None, None, 0, max(y_axis) + 1])

        plt.xticks([])
        plt.xlabel('Time')
        plt.ylabel(f'Price in {CURRENCY}')
        plt.fill_between(x_axis, y_axis, color='#ffb480')

        clm1.pyplot(fig, transparent=True)

        ### Prices and Categories ###
        clm2.title('Average Price per Category')
        clm2.write(' ')

        y_axis = []
        for category in CATEGORIES:
            cur.execute(f"SELECT SUM(price), COUNT(name) FROM {SHOP} WHERE category = ? AND date = ?",
                        (category, TODAY))
            prices_and_count = cur.fetchall()

            if prices_and_count[0][0] and prices_and_count[0][1] is not None:
                y_axis.append(round(prices_and_count[0][0] / prices_and_count[0][1], 2))

        fig, ax = plt.subplots()
        #ax.barh(CATEGORIES, y_axis, color=COLORS)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        plt.setp(ax.get_yticklabels(), fontsize=10, rotation='horizontal')
        plt.xlabel('Price in EUR')
        clm2.pyplot(fig, transparent=True)

    def statistics_3():
        # products with most relative price rise and fall
        # date to compare
        # three_month_ago = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
        three_month_ago = '2022-03-28'

        # DB Cnnection
        cur.execute(f"SELECT price, name FROM {SHOP} WHERE date = ?", (three_month_ago,))
        products_then = cur.fetchall()

        # Iterate through all products and select 10 with highest rise
        rises = []
        for product_then in products_then:
            try:
                cur.execute(f"SELECT price, image FROM {SHOP} WHERE date = ? AND name = ?", (TODAY, product_then[1],))
                product_today = cur.fetchall()

                price_rise = round(
                    (((float(product_today[0][0]) - float(product_then[0])) / float(product_then[0])) * 100), 2)

                # Price rise / Name / Price today / Price then / Image
                rises.append([price_rise, product_then[1], product_today[0][0], product_then[0], product_today[0][1]])

            except:
                continue

        top_ten_rises = sorted(rises, key=itemgetter(0))
        space, clm1, space, clm2, space = st.columns((1, 5, 1, 5, 1))

        clm1.header('Top 5 - Relative Price Rise 📈')
        clm1.caption(f'➠ since {three_month_ago}')
        clm2.header('Top 5 - Relative Price Fall 📉')
        clm2.caption(f'➠ since {three_month_ago}')

        for j in range(5):
            i = -j - 1
            space, clm1_0, clm1_1, border, clm2_0, clm2_1, space = st.columns((1, 5, 5, 1, 5, 5, 1))

            ### RISES ###
            clm1_0.write('-----------------------------------------------------------------------')
            clm1_0.write(' ')
            clm1_0.image(top_ten_rises[i][4], width=140)
            clm1_1.write('-----------------------------------------------------------------------')
            clm1_1.write(f'{top_ten_rises[i][1]}')
            clm1_1.write(f'{top_ten_rises[i][3]} {CURRENCY} ➩ {top_ten_rises[i][2]} {CURRENCY}')
            clm1_1.markdown(f'<FONT COLOR="#ff6961"> + {top_ten_rises[i][0]} % </FONT>', unsafe_allow_html=True)

            ### FALLS ###
            j = abs(i) + 1
            clm2_0.write('-----------------------------------------------------------------------')
            clm2_0.write(' ')
            clm2_0.image(top_ten_rises[j][4], width=140)
            clm2_1.write('-----------------------------------------------------------------------')
            clm2_1.write(f'{top_ten_rises[j][1]}')
            clm2_1.write(f'{top_ten_rises[j][3]} {CURRENCY} ➩ {top_ten_rises[j][2]} {CURRENCY}')
            clm2_1.markdown(f'<FONT COLOR="#42d6a4"> - {top_ten_rises[j][0]} % </FONT>', unsafe_allow_html=True)

            ### BORDER ###
            for i in range(8):
                border.markdown('┃')

    def placeholder():
        st.write(' ')
        st.write(' ')
        st.write(' ')

    def run():
        st.title(SHOP.strip('_').capitalize())
        placeholder()
        data_metric()
        placeholder()
        statistics_1()
        placeholder()
        statistics_2()
        placeholder()
        statistics_3()
        products_table()

    run()
