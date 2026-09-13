"""
state.py
--------
Zentrale Verwaltung des st.session_state.
Alle Daten (Bilder + Tags) leben ausschliesslich hier - es gibt keine
Datenbank- oder Backend-Anbindung. Das bedeutet: Jede Browser-Sitzung
hat ihre eigenen Fundstuecke, ein Reload/Neustart der App loescht sie.
"""

import uuid
from datetime import datetime

import streamlit as st


def init_state() -> None:
    """Initialisiert alle benoetigten Keys im session_state, falls noch nicht vorhanden."""
    if "fund_entries" not in st.session_state:
        # Liste von Dicts: id, image_bytes, ki_tags, user_tags, timestamp
        st.session_state.fund_entries = []
    if "page" not in st.session_state:
        st.session_state.page = "home"  # "home" | "search" | "detail"
    if "current_item_id" not in st.session_state:
        st.session_state.current_item_id = None
    if "mode" not in st.session_state:
        st.session_state.mode = "upload"  # "upload" | "edit"
    if "pending_image_bytes" not in st.session_state:
        st.session_state.pending_image_bytes = None
    if "pending_ki_tags" not in st.session_state:
        st.session_state.pending_ki_tags = []
    if "pending_user_tags" not in st.session_state:
        st.session_state.pending_user_tags = []
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""


def go_to(page: str, item_id: str | None = None, mode: str = "upload") -> None:
    """Wechselt die aktuelle Seite und setzt den Kontext fuer die Detailseite."""
    st.session_state.page = page
    st.session_state.current_item_id = item_id
    st.session_state.mode = mode


def add_item(image_bytes: bytes, ki_tags: list[str], user_tags: list[str]) -> str:
    """Speichert ein neues Fundstueck. Neueste Eintraege stehen vorne (fuer 'Zuletzt Gefunden')."""
    item_id = str(uuid.uuid4())
    st.session_state.fund_entries.insert(
        0,
        {
            "id": item_id,
            "image_bytes": image_bytes,
            "ki_tags": ki_tags,
            "user_tags": user_tags,
            "timestamp": datetime.now(),
        },
    )
    return item_id


def get_item(item_id: str) -> dict | None:
    for item in st.session_state.fund_entries:
        if item["id"] == item_id:
            return item
    return None


def update_user_tags(item_id: str, new_user_tags: list[str]) -> bool:
    item = get_item(item_id)
    if item is None:
        return False
    item["user_tags"] = new_user_tags
    return True


def delete_item(item_id: str) -> None:
    st.session_state.fund_entries = [i for i in st.session_state.fund_entries if i["id"] != item_id]


def latest_items(n: int = 3) -> list[dict]:
    return st.session_state.fund_entries[:n]


def search_items(query: str) -> list[dict]:
    """
    Case-insensitive Teilstring-Suche: ein Eintrag ist ein Treffer, sobald
    mindestens eines der eingegebenen Stichwoerter in mindestens einem
    seiner Tags (KI- oder User-Tag) vorkommt.
    """
    if not query or not query.strip():
        return []

    keywords = [kw.strip().lower() for kw in query.replace(",", " ").split() if kw.strip()]
    if not keywords:
        return []

    results = []
    for item in st.session_state.fund_entries:
        haystack = " ".join(item["ki_tags"] + item["user_tags"]).lower()
        if any(kw in haystack for kw in keywords):
            results.append(item)
    return results


def reset_pending_upload() -> None:
    """Setzt den Zwischenspeicher fuer einen neuen Upload-Vorgang zurueck."""
    st.session_state.pending_image_bytes = None
    st.session_state.pending_ki_tags = []
    st.session_state.pending_user_tags = []
