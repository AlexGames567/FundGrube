"""
search.py
---------
Suchergebnis-Seite (Screenshot 2): Suchleiste mit anderem Platzhaltertext
und ein Grid mit passenden Fundstuecken.
"""

import streamlit as st

from src import components, state


def render() -> None:
    components.render_logo()

    query = components.render_search_bar(
        placeholder="Beschreibe deinen Gegenstand in kurzen Stichpunkten",
        key="search_page_search",
    )

    # Zurueck-Link zur Startseite (im Design nicht explizit vorhanden,
    # aber notwendig fuer die Navigation ohne Backend/Routing).
    if st.button("← Zurueck zur Startseite"):
        state.go_to("home")
        st.rerun()

    st.write("")

    if query is not None and query != "":
        st.session_state.search_query = query

    results = state.search_items(st.session_state.search_query)

    if st.session_state.search_query and not results:
        st.markdown(
            '<p class="fg-empty-hint">Keine Fundstuecke zu diesen Stichworten gefunden.</p>',
            unsafe_allow_html=True,
        )
    else:
        components.render_item_grid(results, columns=3, on_click_mode="edit")
