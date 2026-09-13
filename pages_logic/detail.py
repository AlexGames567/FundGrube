"""
detail.py
---------
Detailseite (Screenshot 3). Ein Layout, zwei Modi:

  - mode == "upload": neues Bild wurde gerade auf der Startseite ausgewaehlt.
    KI-Tags stehen schon in st.session_state.pending_* bereit.
    Button: "Hochladen" -> speichert das Fundstueck neu.

  - mode == "edit": ein bestehendes Fundstueck wurde ueber die Suche/Startseite
    angeklickt. Buttons: "Aendern" (speichert neue User-Tags) und "Loeschen".
"""

import base64

import streamlit as st

from src import components, state


def _render_big_image(image_bytes: bytes) -> None:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    st.markdown(
        f'<div class="fg-image-box" style="max-width:320px;">'
        f'<img src="data:image/png;base64,{b64}" /></div>',
        unsafe_allow_html=True,
    )


def _add_tag_callback(working_key: str, input_key: str) -> None:
    """
    Callback fuer den on_change-Event des Tag-Eingabefelds.
    Nur innerhalb eines Callbacks darf der Wert eines Widgets (hier: das
    Eingabefeld selbst) direkt im session_state zurueckgesetzt werden.
    """
    new_tag = st.session_state.get(input_key, "").strip()
    if new_tag and new_tag not in st.session_state[working_key]:
        st.session_state[working_key].append(new_tag)
    st.session_state[input_key] = ""


def _render_editable_tags(working_key: str) -> None:
    """
    Zeigt die aktuell in st.session_state[working_key] liegenden User-Tags
    als entfernbare Chips plus ein Eingabefeld, um neue Tags hinzuzufuegen.
    """
    tags: list[str] = st.session_state[working_key]

    if tags:
        chip_cols = st.columns(min(len(tags), 4) or 1)
        for i, tag in enumerate(tags):
            with chip_cols[i % len(chip_cols)]:
                if st.button(f"{tag}  ✕", key=f"{working_key}-remove-{i}-{tag}"):
                    tags.pop(i)
                    st.rerun()
    else:
        st.markdown('<span class="fg-empty-hint">Noch keine eigenen Tags</span>', unsafe_allow_html=True)

    input_key = f"{working_key}-input"
    st.text_input(
        "Neuen Tag hinzufuegen",
        key=input_key,
        placeholder="Tag eingeben und Enter druecken",
        label_visibility="collapsed",
        on_change=_add_tag_callback,
        args=(working_key, input_key),
    )


def render() -> None:
    components.render_logo()

    mode = st.session_state.mode
    item_id = st.session_state.current_item_id

    if mode == "upload":
        image_bytes = st.session_state.pending_image_bytes
        ki_tags = st.session_state.pending_ki_tags

        if image_bytes is None:
            st.warning("Kein Bild ausgewaehlt. Bitte zuerst ueber die Startseite ein Bild hochladen.")
            if st.button("Zur Startseite"):
                state.go_to("home")
                st.rerun()
            return

        working_key = "pending_user_tags"
        if working_key not in st.session_state:
            st.session_state[working_key] = []

    else:  # mode == "edit"
        item = state.get_item(item_id)
        if item is None:
            st.warning("Dieses Fundstueck existiert nicht mehr.")
            if st.button("Zur Startseite"):
                state.go_to("home")
                st.rerun()
            return

        image_bytes = item["image_bytes"]
        ki_tags = item["ki_tags"]

        # Arbeitskopie der User-Tags fuer diesen Eintrag anlegen, falls noch nicht vorhanden
        working_key = f"edit_user_tags_{item_id}"
        if working_key not in st.session_state:
            st.session_state[working_key] = list(item["user_tags"])

    col_image, col_tags = st.columns([1, 1])

    with col_image:
        _render_big_image(image_bytes)

    with col_tags:
        with st.container(border=True):
            st.markdown('<p class="fg-tagbox-title">KI generierte Tags</p>', unsafe_allow_html=True)
            components.render_tag_chips(ki_tags)

        st.write("")

        with st.container(border=True):
            st.markdown('<p class="fg-tagbox-title">Tags selbst hinzufügen</p>', unsafe_allow_html=True)
            _render_editable_tags(working_key)

        st.write("")

        if mode == "upload":
            if st.button("Hochladen", type="primary", use_container_width=True):
                state.add_item(
                    image_bytes=image_bytes,
                    ki_tags=ki_tags,
                    user_tags=st.session_state[working_key],
                )
                state.reset_pending_upload()
                del st.session_state[working_key]
                state.go_to("home")
                st.rerun()
        else:
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("Ändern", use_container_width=True):
                    state.update_user_tags(item_id, st.session_state[working_key])
                    del st.session_state[working_key]
                    state.go_to("home")
                    st.rerun()
            with btn_col2:
                if st.button("Löschen", use_container_width=True):
                    state.delete_item(item_id)
                    del st.session_state[working_key]
                    state.go_to("home")
                    st.rerun()
