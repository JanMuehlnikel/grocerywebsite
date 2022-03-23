import streamlit as st
from streamlit_option_menu import option_menu

import seiten.shops as shops
import seiten.home as home

st.set_page_config(f'GROCERIES', layout="wide")

def menu():
    selected = option_menu(
        menu_title=None,
        options=['Home', 'Aldi', 'REWE'],
        icons=['house'],
        menu_icon=['cast'],
        default_index=0,
        orientation='horizontal',
        styles={
            "container": {"padding": "0!important", "background-color": "#grey"},
            "icon": {"color": "#ff6961", "font-size": "25px"},
            "nav-link": {
                "font-size": "25px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#ff6961",
            },
            "nav-link-selected": {"background-color": "grey"},
        },
    )
    return selected


selected = menu()

if selected == 'Home':
    home.app()
if selected == 'Aldi':
    shops.app('aldi')