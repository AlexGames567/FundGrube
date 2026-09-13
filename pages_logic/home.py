"""
home.py
-------
Startseite (Screenshot 1): Logo, Upload-Icon-Button, Suchleiste,
Bereich "Zuletzt Gefunden".
"""

import streamlit as st

from src import components, state
from src.classifier import classify_image


def render() -> None:
    components.render_logo()

    # --- Upload-Icon -------------------------------------------------------
    st.markdown('<div class="fg-upload-wrap">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        label="Bild hochladen",
        type=["png", "jpg", "jpeg"],
        key="home_uploader",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()
        state.reset_pending_upload()
        st.session_state.pending_image_bytes = image_bytes
        # KI-Klassifikation direkt beim Hochladen ausloesen, damit die
        # Tags schon auf der Detailseite bereitstehen.
        with st.spinner("Bild wird analysiert..."):
            st.session_state.pending_ki_tags = classify_image(image_bytes)
        state.go_to("detail", item_id=None, mode="upload")
        st.rerun()

    st.write("")  # kleiner vertikaler Abstand

    # --- Suchleiste ----------------------------------------------------------
    query = components.render_search_bar(placeholder="Suche", key="home_search")
    if query:
        st.session_state.search_query = query
        state.go_to("search")
        st.rerun()

    st.write("")

    # --- Zuletzt Gefunden ----------------------------------------------------
    st.markdown('<p class="fg-section-title">Zuletzt Gefunden</p>', unsafe_allow_html=True)
    components.render_item_grid(state.latest_items(3), columns=3, on_click_mode="edit")
