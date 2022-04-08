import streamlit as st
import sqlite3
from datetime import timedelta, date
from operator import itemgetter
from PIL import Image


def app():
    st.header('HOME')
    # Database Connection
    DB = f'Products.db'
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # DATES
    TODAY = date.today()
    THIS_MONDAY = TODAY - timedelta(days=TODAY.weekday())
    LAST_MONDAY = TODAY - timedelta(days=TODAY.weekday(), weeks=1)

    # COLORS
    COLORS = ['#ff6961', '#ffb480', '#f8f38d', '#42d6a4', '#08cad1', '#59adf6', '#9d94ff', '#c780e8', '#D876AC']

    def compare_stores():
        # Compare Inflation Rate with shops
        st.title('Compare Inflation Rate')
        space, clm1, space, clm2, space, clm3, space = st.columns((1, 5, 1, 5, 1, 5, 1))

        # Select the shops from the DB
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        shops = cur.fetchall()

        # Append shop to list
        shop_list = ['NO SHOP']
        for shop in shops:
            shop_list.append(str(shop[0]).upper().replace('_', ' '))

        # Select a shop
        with clm1:
            select1 = st.selectbox('Select a shop', shop_list)

        # Select a category
        with clm2:
            # Disabled if no shop
            if select1 == 'NO SHOP':
                select2 = st.selectbox('Select a inflation category', shop_list, disabled=True)

            # Select box with all categories(labels) from shop
            else:
                # Select all categories
                cur.execute(f"SELECT DISTINCT label FROM {select1.lower().replace(' ', '_')} WHERE date = ?",
                            (LAST_MONDAY,))
                labels = cur.fetchall()

                # List with all categories
                label_list = ['All Categories']
                for label in labels:
                    label_list.append(str(label[0]))
                select2 = st.selectbox('Select a inflation category', label_list)

                def calc_inflation(store):
                    if select2 != 'All Categories':
                        cur.execute(f"SELECT AVG(price) FROM {store} WHERE date = ? AND label = ?",
                                    (THIS_MONDAY, select2,))
                        result = cur.fetchall()
                        price_now = result[0][0]

                        cur.execute(f"SELECT AVG(price) FROM {store} WHERE date = ? AND label = ?",
                                    (LAST_MONDAY, select2,))
                        result = cur.fetchall()
                        price_then = result[0][0]
                    else:
                        cur.execute(f"SELECT AVG(price) FROM {store} WHERE date = ?",
                                    (THIS_MONDAY,))
                        result = cur.fetchall()
                        price_now = result[0][0]

                        cur.execute(f"SELECT AVG(price) FROM {store} WHERE date = ?",
                                    (LAST_MONDAY,))
                        result = cur.fetchall()
                        price_then = result[0][0]
                    try:
                        return f'{round(((price_now - price_then) / price_then) * 100, 2)}%'
                    except:
                        return '0%'

                clm1.markdown(f'<FONT COLOR="#D876AC"> _____________________________________________________ </FONT>',
                              unsafe_allow_html=True)
                clm1.subheader(select1)
                clm1.subheader(f"Inflation Rate: {calc_inflation(str(select1.lower().replace(' ', '_')))}")
                clm1.markdown(f'<FONT COLOR="#9e5993"> _____________________________________________________ </FONT>',
                              unsafe_allow_html=True)

                clm2.markdown(f'<FONT COLOR="#ff6961"> _____________________________________________________ </FONT>',
                              unsafe_allow_html=True)
                clm2.subheader(f'Category:')
                if select2 != 'All Categories':
                    clm2.subheader(f'{select2[5:]}')
                else:
                    clm2.subheader(f'All Categories')
                clm2.markdown(f'<FONT COLOR="#ffb480"> _____________________________________________________ </FONT>',
                              unsafe_allow_html=True)

        # Shop to compare with
        with clm3:
            if select1 == 'NO SHOP':
                select3 = st.selectbox('Select a shop to compare', shop_list, disabled=True)
            else:
                select3 = st.selectbox('Select a shop to compare', shop_list)
            if select1 == select3 and select3 != 'NO SHOP':
                st.write('Please do not select the same shop!')
            elif select3 != 'NO SHOP':
                clm3.markdown(f'<FONT COLOR="#08cad1"> _____________________________________________________ </FONT>',
                              unsafe_allow_html=True)
                clm3.subheader(select3)
                clm3.subheader(f"Inflation Rate: {calc_inflation(str(select3.lower().replace(' ', '_')))}")
                clm3.markdown(f'<FONT COLOR="#59adf6"> _____________________________________________________ </FONT>',
                              unsafe_allow_html=True)

    def information():
        space, clm1, space, clm2 = st.columns((1, 7, 1, 4))
        with clm1:
            st.title('Intention / Information')
            image = Image.open('p1.png')
            st.image(image, f'', width=500)

            st.write('')
        # WARN SYSTEM
        with clm2:
            # Select the shops from the DB
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            shops = cur.fetchall()

            # Append shop to list
            shop_list = []
            for shop in shops:
                shop_list.append(str(shop[0]))

            warnings = []
            for shop in shop_list:
                cur.execute(f"SELECT DISTINCT label FROM {shop}")
                labels = cur.fetchall()
                for label in labels:
                    cur.execute(f"SELECT avg(price) FROM {shop} WHERE label = ? AND date = ?",
                                (label[0], str(THIS_MONDAY),))
                    price_now = cur.fetchall()

                    cur.execute(f"SELECT avg(price) FROM {shop} WHERE label = ? AND date = ?",
                                (label[0], str(LAST_MONDAY),))
                    price_then = cur.fetchall()

                    try:
                        inflation = round(((price_now[0][0] - price_then[0][0]) / price_then[0][0]) * 100, 2)
                    except:
                        inflation = 0

                    if inflation > 0:
                        warnings.append([inflation, label[0], shop])

            sorted_warnings = sorted(warnings, key=itemgetter(0))

            st.title('Inflation Warning 🚨')
            for i in range(-1, -6, -1):
                st.subheader(f'{sorted_warnings[i][1][5:]}')
                st.markdown(f'Inflation: <FONT COLOR="#ff6961"> {sorted_warnings[i][0]}% </FONT>', unsafe_allow_html=True)
                st.caption(f'Shop: {sorted_warnings[i][2].upper().replace("_", " ")}')
                st.markdown(f'<FONT COLOR="#ff6961"> _____________________________________________________ </FONT>',
                            unsafe_allow_html=True)

    def placeholder():
        st.write(' ')
        st.write('________________________________________________________________________________________________________')
        st.write(' ')

    def run():
        information()
        placeholder()
        compare_stores()

    run()
