import streamlit as st
from matplotlib import pyplot as plt
from datetime import timedelta, date
import matplotlib.dates
import seiten.product as product_site
from PIL import Image
import sqlite3
from operator import itemgetter


def app(shop: str, currency: str) -> None:
    # VARIABLES
    SHOP = shop
    SHOP_STR = shop.replace('_', ' ')
    DB = f'Products.db'
    CURRENCY = currency
    IMAGEFILE = f'{SHOP}.png'
    COLORS = ['#ff6961', '#ffb480', '#f8f38d', '#42d6a4', '#08cad1', '#59adf6', '#9d94ff', '#c780e8', '#D876AC']

    # DATES
    TODAY = date.today()
    THIS_MONDAY = TODAY - timedelta(days=TODAY.weekday())
    LAST_MONDAY = TODAY - timedelta(days=TODAY.weekday(), weeks=1)

    # Database Connection
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Category List
    CATEGORIES = []
    cats_count = []
    cur.execute(f"SELECT DISTINCT label FROM {SHOP} WHERE date = ?", (THIS_MONDAY,))
    rows = cur.fetchall()
    for row in rows:
        cur.execute(f"SELECT COUNT(name) FROM {SHOP} WHERE date = ? AND label = ?", (THIS_MONDAY, row[0],))
        count = cur.fetchall()
        CATEGORIES.append(row[0])
        cats_count.append([row[0], count[0][0]])

    sorted_cats = sorted(cats_count, key=itemgetter(1), reverse=True)
    if len(sorted_cats) > 9:
        CATEGORIES_PIE = sorted_cats[:9]
        rest = 0
        for cat in sorted_cats[9:]:
            rest += cat[1]
        CATEGORIES_PIE.append(['Other Categories', rest])
    else:
        CATEGORIES_PIE = sorted_cats

    def data_metric():
        def compare(day):
            cur.execute(f"SELECT COUNT(name) FROM {SHOP} WHERE date = ?", (day,))
            number_products = cur.fetchall()

            cur.execute(f"SELECT SUM(price) FROM {SHOP} WHERE date = ?", (day,))
            sum_price = cur.fetchall()

            cur.execute(f"SELECT price, name FROM {SHOP} WHERE date = ?", (THIS_MONDAY,))
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

        number_products_today = compare(THIS_MONDAY)[0]
        number_products_yesterday = compare(LAST_MONDAY)[0]
        avg_price_today = compare(THIS_MONDAY)[1]
        avg_price_yesterday = compare(LAST_MONDAY)[1]
        changes_today = compare(THIS_MONDAY)[2]

        # WRITE COLUMNS
        products, avg_price, change = st.columns(3)
        products.metric(f'Number Of Products',
                        f'{number_products_today} Products',
                        f'{round(((number_products_today - number_products_yesterday) / number_products_yesterday) * 100, 2)} %')

        avg_price.metric(f'Average Price', f'{avg_price_today} {CURRENCY}',
                         f'{round(((avg_price_today - avg_price_yesterday) / avg_price_yesterday) * 100, 2)} %')

        change.metric(f'Price Changes', f'{changes_today} changes', f'since {LAST_MONDAY}')

    def products_table():
        # Sidebar
        st.write(' ')
        st.write(
            '──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────'
            '──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────'
        )
        st.write(' ')
        st.title('Product Information')

        space, clm1, space, clm2, space = st.columns((1, 5, 1, 5, 1))

        sb_category = clm1.selectbox('Select category', CATEGORIES, index=0)

        cur.execute(f"SELECT name, price FROM {SHOP} WHERE label = ? AND date = ?", (sb_category, THIS_MONDAY,))
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
            '──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────'
            '──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────'
        )
        st.write(' ')

    def statistics_1():
        space, clm1, space, clm2, space = st.columns((1, 5, 1, 5, 1))

        clm1.title(f'{SHOP.upper().replace("_", " ")}')
        clm1.write(' ')
        image = Image.open(IMAGEFILE)
        clm1.image(image, width=400)

        ### CATEGROIES PIE CHART ###
        clm2.title('Categories')
        clm1.write(' ')

        # Plot pie chart
        labels = [
            category[0]
            for category in CATEGORIES_PIE
        ]
        sizes = []
        for category in CATEGORIES_PIE:
            sizes.append(category[1])

            colors = ['#ff6961', '#ffb480', '#f8f38d', '#42d6a4', '#08cad1', '#59adf6', '#9d94ff', '#c780e8',
                      '#D876AC', '#9e5993']
        explode = [
            0.05
            for i in CATEGORIES_PIE
        ]

        fig, ax = plt.subplots()

        ax.pie(
            sizes, colors=colors, labeldistance=None, explode=explode
        )
        labels = [f'{l} - {s} Products' for l, s in zip(labels, sizes)]
        ax.legend(labels=labels, title='Categories', loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        centre_circle = plt.Circle((0, 0), 0.50, fc='white')
        fig = plt.gcf()
        fig.gca().add_artist(centre_circle)

        clm2.pyplot(fig, transparent=True)

    def statistics_2():
        space, clm1, space, clm2, space = st.columns((1, 5, 1, 5, 1))
        space, clm1_1, space, clm2_1, space, clm2_2, space = st.columns((1, 11, 1, 5, 1, 5, 1))

        def avg():
            ### AVG Prices per Categories ###
            clm1.title('Average Price')
            clm1.write(' ')

            cur.execute(f"SELECT DISTINCT label FROM {SHOP}")
            labels = cur.fetchall()
            labels_list = ['Total - All Categories']
            for label in labels:
                labels_list.append(label[0])
            select = clm1.selectbox('Select a category', labels_list)

            clm1_1.write(' ')
            clm1_1.write(' ')
            clm1_1.write(' ')

            if select != 'Total - All Categories':
                cur.execute(f"SELECT DISTINCT date FROM {SHOP} WHERE label = ?", (select,))
                dates = cur.fetchall()

                x_axis_unsorted = [
                    selected_date[0]
                    for selected_date in dates
                ]
                x_axis = sorted(x_axis_unsorted)

                y_axis = []
                for selected_date in x_axis:
                    cur.execute(f"SELECT AVG(price) FROM {SHOP} WHERE date = ? AND label = ?", (selected_date, select,))
                    avg_price = cur.fetchall()
                    y_axis.append(avg_price[0][0])
            else:
                cur.execute(f"SELECT DISTINCT date FROM {SHOP}")
                dates = cur.fetchall()
                x_axis_unsorted = [
                    selected_date[0]
                    for selected_date in dates
                ]
                x_axis = sorted(x_axis_unsorted)

                y_axis = []
                for selected_date in x_axis:
                    cur.execute(f"SELECT AVG(price) FROM {SHOP} WHERE date = ?", (selected_date,))
                    avg_price = cur.fetchall()
                    y_axis.append(avg_price[0][0])

            # Plot line chart
            fig1, ax1 = plt.subplots()

            ax1.fill_between(x_axis, y_axis, color=COLORS[0])
            ax1.axis([None, None, 0, max(y_axis) + 1])

            plt.xticks([])
            plt.xlabel('Time')
            plt.ylabel(f'Price in {CURRENCY}')

            clm1_1.pyplot(fig1, transparent=True)

        def one_to_watch():
            clm2.title('Ones To Watch')
            clm2.write(' ')
            otw = ['Categories to watch 📋',  'Products - Price Rise 📈', 'Products - Price Fall 📉', 'Out Of Portfolio ⬅', 'New In Portfolio ➡']

            select = clm2.selectbox('Select', otw)

            def categories():
                unsorted_cats = []
                cur.execute(f"SELECT DISTINCT label FROM {SHOP}")
                labels = cur.fetchall()
                for label in labels:
                    cur.execute(f"SELECT avg(price) FROM {SHOP} WHERE label = ? AND date = ?",
                                (label[0], str(THIS_MONDAY),))
                    price_now = cur.fetchall()

                    cur.execute(f"SELECT avg(price) FROM {SHOP} WHERE label = ? AND date = ?",
                                (label[0], str(LAST_MONDAY),))
                    price_then = cur.fetchall()

                    try:
                        inflation = round(((price_now[0][0] - price_then[0][0]) / price_then[0][0]) * 100, 2)
                    except:
                        inflation = 0

                    unsorted_cats.append([abs(inflation), label[0], inflation])

                cats = sorted(unsorted_cats, key=itemgetter(0))

                for i in range(-1, -11, -1):
                    if i >= -5:
                        clm2_1.write('-----------------------------------------------------------------------')
                        clm2_1.write(f'{i * -1}: {cats[i][1][5:]}')
                        if cats[i][2] >= 0:
                            clm2_1.markdown(f'<FONT COLOR="#ff6961">+ {cats[i][2]} %</FONT>', unsafe_allow_html=True)
                        else:
                            clm2_1.markdown(f'<FONT COLOR="#42d6a4">{cats[i][2]} %</FONT>', unsafe_allow_html=True)
                    else:
                        clm2_2.write('-----------------------------------------------------------------------')
                        clm2_2.write(f'{i * -1}: {cats[i][1][5:]}')
                        if cats[i][2] >= 0:
                            clm2_2.markdown(f'<FONT COLOR="#ff6961">+ {cats[i][2]} %</FONT>', unsafe_allow_html=True)
                        else:
                            clm2_2.markdown(f'<FONT COLOR="#42d6a4">{cats[i][2]} %</FONT>', unsafe_allow_html=True)

            def rises_falls(status: str):
                # products with most relative price rise and fall
                DATE_TO_COMPARE = LAST_MONDAY
                # DB Cnnection
                cur.execute(f"SELECT price, name FROM {SHOP} WHERE date = ?", (DATE_TO_COMPARE,))
                products_then = cur.fetchall()

                # Iterate through all products and select 10 with highest rise
                rises = []
                for product_then in products_then:
                    try:
                        cur.execute(f"SELECT price, image FROM {SHOP} WHERE date = ? AND name = ?",
                                    (THIS_MONDAY, product_then[1],))
                        product_today = cur.fetchall()

                        price_rise = round(
                            (((float(product_today[0][0]) - float(product_then[0])) / float(product_then[0])) * 100), 2)

                        # Price rise / Name / Price today / Price then / Image
                        rises.append(
                            [price_rise, product_then[1], product_today[0][0], product_then[0], product_today[0][1]])

                    except:
                        continue

                top_ten_rises = sorted(rises, key=itemgetter(0))

                ### RISES ###
                if status == 'rise':
                    for j in range(5):
                        i = -j - 1

                        clm2_1.write('-----------------------------------------------------------------------')
                        clm2_1.image(top_ten_rises[i][4], width=67)
                        clm2_1.markdown(' ')
                        clm2_2.write('-----------------------------------------------------------------------')
                        clm2_2.markdown(f'{top_ten_rises[i][1]}')
                        clm2_2.markdown(f'{top_ten_rises[i][3]} {CURRENCY} ➩ {top_ten_rises[i][2]} {CURRENCY} '
                                        f'(<FONT COLOR="#ff6961">+ {top_ten_rises[i][0]} %</FONT>)',
                                        unsafe_allow_html=True)
                        if len(top_ten_rises[i][1]) < 46:
                            clm2_2.markdown(' ')

                ### FALLS ###
                elif status == 'fall':
                    for j in range(0, 5):
                        clm2_1.caption('-----------------------------------------------------------------------')
                        clm2_1.image(top_ten_rises[j][4], width=67)
                        clm2_1.markdown(' ')
                        clm2_2.caption('-----------------------------------------------------------------------')
                        clm2_2.write(f'{top_ten_rises[j][1]}')
                        clm2_2.markdown(f'{top_ten_rises[j][3]} {CURRENCY} ➩ {top_ten_rises[j][2]} {CURRENCY} '
                                        f'(<FONT COLOR="#42d6a4">{top_ten_rises[j][0]} %</FONT>)',
                                        unsafe_allow_html=True)
                        if len(top_ten_rises[j][1]) < 46:
                            clm2_2.markdown(' ')

            def portfolio(status: str):
                if status == 'new':
                    base_date = LAST_MONDAY
                    compare_date = THIS_MONDAY
                    st = 'new products in portfolio'
                elif status == 'out':
                    base_date = THIS_MONDAY
                    compare_date = LAST_MONDAY
                    st = 'products out of portfolio'

                compare_list = []
                base_list = []
                for c in CATEGORIES:
                    cur.execute(f"SELECT COUNT(label) FROM {SHOP} WHERE label = ? AND date = ?", (c, base_date,))
                    c1_sum = cur.fetchall()
                    base_list.append([c1_sum[0][0], c])

                    cur.execute(f"SELECT COUNT(label) FROM {SHOP} WHERE label = ? AND date = ?", (c, compare_date,))
                    c2_sum = cur.fetchall()
                    compare_list.append(c2_sum[0][0])

                result_list = []
                for i in range(len(base_list)):
                    result_list.append([base_list[i][0] - compare_list[i], base_list[i][1]])

                sorted_results = sorted(result_list, key=itemgetter(0))

                for i in range(-1, -11, -1):
                    if i > -6:
                        clm2_1.write('-----------------------------------------------------------------------')
                        clm2_1.write(f'{sorted_results[i][1][5:]}')
                        clm2_1.caption(f'➟ {sorted_results[i][0]} {st}')
                    else:
                        clm2_2.write('-----------------------------------------------------------------------')
                        clm2_2.write(f'{sorted_results[i][1][5:]}')
                        clm2_2.caption(f'➟ {sorted_results[i][0]} {st}')

            if select == 'Categories to watch 📋':
                categories()
            elif select == 'Products - Price Rise 📈':
                rises_falls('rise')
            elif select == 'Products - Price Fall 📉':
                rises_falls('fall')
            elif select == 'Out Of Portfolio ⬅':
                portfolio('out')
            elif select == 'New In Portfolio ➡':
                portfolio('new')

        avg()
        one_to_watch()

    def placeholder():
        st.write(' ')
        st.write(' ')
        st.write(' ')

    def run():
        st.title(f'DASHBOARD - {SHOP_STR.upper().replace("_", " ")}')
        placeholder()
        data_metric()
        st.write(' ')
        st.write(
            '──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────'
            '──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────'
        )
        placeholder()
        statistics_1()
        st.write(' ')
        st.write(
            '──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────'
            '──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────'
        )
        placeholder()
        statistics_2()
        placeholder()
        products_table()
        placeholder()
        # statistics_4()

    run()
