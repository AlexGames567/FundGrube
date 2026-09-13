"""
app.py
------
Einstiegspunkt der "Fund Grube"-App. Uebernimmt nur das Routing zwischen
den drei Seiten - die eigentliche Logik liegt in pages_logic/.

Start lokal:  streamlit run app.py
"""

import streamlit as st

from pages_logic import detail, home, search
from src import state, styles

st.set_page_config(page_title="Fund Grube", page_icon="🔍", layout="centered")

state.init_state()
styles.inject_css()

_PAGES = {
    "home": home.render,
    "search": search.render,
    "detail": detail.render,
}

current_page = st.session_state.page
render_fn = _PAGES.get(current_page, home.render)
render_fn()
