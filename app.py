import streamlit as st
from streamlit_option_menu import option_menu

import seiten.shops as shops
import seiten.home as home

# page config
st.set_page_config(f'Dashboard', layout="wide", page_icon='icon.png')

def menu():
    selected = option_menu(
        menu_title=None,
        options=['Home', 'Aldi', "Carrefour Cote D'Ivoire"],
        icons=['house'],
        menu_icon=['cast'],
        default_index=0,
        orientation='horizontal',
        styles={
            "container": {"padding": "0!important", "background-color": "#grey"},
            "icon": {"color": "#E4E4E4", "font-size": "25px"},
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
    shops.app('aldi', 'EUR')
if selected == "Carrefour Cote D'Ivoire":
    shops.app('carrefour_cote_divoire', 'CFA')