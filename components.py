"""
components.py
--------------
Wiederverwendbare UI-Bausteine, damit home/search/detail nicht dieselbe
Markup-Logik doppeln muessen.
"""

import base64

import streamlit as st

from src import state


def render_logo() -> None:
    st.markdown(
        """
        <div class="fg-logo-wrap">
            <div class="fg-logo">Fund Grube</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_search_bar(placeholder: str, key: str) -> str | None:
    """
    Zeigt eine Suchleiste. Gibt den eingegebenen Text zurueck, sobald der
    Nutzer Enter drueckt (st.text_input mit on_change waere hier unnoetig
    komplex, da wir sowieso bei jedem Rerun den aktuellen Wert brauchen).
    """
    query = st.text_input(
        label="Suche",
        placeholder=placeholder,
        key=key,
        label_visibility="collapsed",
    )
    return query


def _image_box_html(image_bytes: bytes | None) -> str:
    if image_bytes:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        return f'<div class="fg-image-box"><img src="data:image/png;base64,{b64}" /></div>'
    return '<div class="fg-image-box"></div>'


def render_item_grid(items: list[dict], columns: int = 3, on_click_mode: str = "edit") -> None:
    """
    Zeigt eine Reihe/Grid von Fundstuecken. Ein Klick auf ein Bild fuehrt
    zur Detailseite im gewuenschten Modus (Standard: Bearbeiten).
    Wenn 'items' leer ist, wird ein Hinweistext angezeigt statt eines leeren Grids.
    """
    if not items:
        st.markdown(
            '<p class="fg-empty-hint">Noch keine Eintraege vorhanden.</p>',
            unsafe_allow_html=True,
        )
        return

    rows = [items[i : i + columns] for i in range(0, len(items), columns)]
    for row in rows:
        cols = st.columns(columns)
        for col, item in zip(cols, row):
            with col:
                st.markdown(_image_box_html(item["image_bytes"]), unsafe_allow_html=True)
                # Klickbarer Button unter dem Bild oeffnet die Detailseite.
                if st.button("Ansehen", key=f"open-{item['id']}", use_container_width=True):
                    state.go_to("detail", item_id=item["id"], mode=on_click_mode)
                    st.rerun()


def render_tag_chips(tags: list[str]) -> None:
    if not tags:
        st.markdown('<span class="fg-empty-hint">Keine Tags</span>', unsafe_allow_html=True)
        return
    chips_html = "".join(f'<span class="fg-chip">{tag}</span>' for tag in tags)
    st.markdown(chips_html, unsafe_allow_html=True)
