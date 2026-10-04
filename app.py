import os
import sqlite3
import uuid
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
import tensorflow as tf


# ============================================================
# KONFIGURATION
# ============================================================

APP_NAME = "Meine Fundgrube"

IMAGE_FOLDER = "bilder"
MODEL_FOLDER = "model"

MODEL_PATH = os.path.join(MODEL_FOLDER, "model.h5")
LABELS_PATH = os.path.join(MODEL_FOLDER, "labels.txt")

DATABASE_PATH = "fundgrube.db"

# Größe, auf die das Bild für das KI-Modell gebracht wird
IMAGE_SIZE = (224, 224)

# Wie sicher muss die KI sein, damit ein Tag übernommen wird?
MIN_CONFIDENCE = 0.50

# Wie viele Tags maximal pro Bild?
MAX_TAGS = 5


# ============================================================
# ORDNER ANLEGEN
# ============================================================

os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(MODEL_FOLDER, exist_ok=True)


# ============================================================
# SEITENKONFIGURATION
# ============================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🗃️",
    layout="wide"
)


# ============================================================
# DATENBANK
# ============================================================

def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def init_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bilder (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dateiname TEXT NOT NULL,
            pfad TEXT NOT NULL,
            hochgeladen_am TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bild_id INTEGER NOT NULL,
            tag TEXT NOT NULL,
            confidence REAL NOT NULL,
            FOREIGN KEY (bild_id) REFERENCES bilder(id)
        )
    """)

    connection.commit()
    connection.close()


init_database()


# ============================================================
# KI-MODELL LADEN
# ============================================================

@st.cache_resource
def load_ai_model():
    if not os.path.exists(MODEL_PATH):
        return None

    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        return model

    except Exception as error:
        st.error(f"Das KI-Modell konnte nicht geladen werden: {error}")
        return None


@st.cache_data
def load_labels():
    if not os.path.exists(LABELS_PATH):
        return []

    with open(LABELS_PATH, "r", encoding="utf-8") as file:
        labels = [
            line.strip()
            for line in file.readlines()
            if line.strip()
        ]

    return labels


model = load_ai_model()
labels = load_labels()


# ============================================================
# BILD FÜR KI VORBEREITEN
# ============================================================

def prepare_image(image):
    """
    Bereitet ein PIL-Bild für das KI-Modell vor.
    """

    image = image.convert("RGB")
    image = image.resize(IMAGE_SIZE)

    image_array = np.asarray(image).astype(np.float32)

    # Normalisierung auf 0-1
    image_array = image_array / 255.0

    # Batch-Dimension hinzufügen
    image_array = np.expand_dims(image_array, axis=0)

    return image_array


# ============================================================
# KI-ANALYSE
# ============================================================

def predict_tags(image):
    """
    Analysiert ein Bild mit dem Teachable-Machine-Modell.

    Gibt eine Liste zurück:
    [
        {
            "tag": "Hund",
            "confidence": 0.94
        },
        ...
    ]
    """

    if model is None:
        return []

    image_array = prepare_image(image)

    predictions = model.predict(image_array, verbose=0)

    # Ausgabe aus dem Modell holen
    predictions = np.asarray(predictions)

    if predictions.ndim > 1:
        predictions = predictions[0]

    results = []

    for index, confidence in enumerate(predictions):

        if index < len(labels):
            tag = labels[index]
        else:
            tag = f"Klasse {index + 1}"

        confidence = float(confidence)

        if confidence >= MIN_CONFIDENCE:
            results.append({
                "tag": tag,
                "confidence": confidence
            })

    # Höchste Wahrscheinlichkeit zuerst
    results.sort(
        key=lambda x: x["confidence"],
        reverse=True
    )

    return results[:MAX_TAGS]


# ============================================================
# BILD SPEICHERN
# ============================================================

def save_image(image, original_filename):
    """
    Speichert das Bild mit einem eindeutigen Dateinamen.
    """

    extension = os.path.splitext(original_filename)[1].lower()

    if extension not in [".jpg", ".jpeg", ".png", ".webp"]:
        extension = ".jpg"

    filename = f"{uuid.uuid4().hex}{extension}"

    path = os.path.join(
        IMAGE_FOLDER,
        filename
    )

    image.save(path)

    return filename, path


# ============================================================
# BILD + TAGS IN DATENBANK SPEICHERN
# ============================================================

def save_to_database(filename, path, tags):
    connection = get_connection()
    cursor = connection.cursor()

    upload_time = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO bilder
        (dateiname, pfad, hochgeladen_am)
        VALUES (?, ?, ?)
    """, (
        filename,
        path,
        upload_time
    ))

    image_id = cursor.lastrowid

    for tag in tags:
        cursor.execute("""
            INSERT INTO tags
            (bild_id, tag, confidence)
            VALUES (?, ?, ?)
        """, (
            image_id,
            tag["tag"],
            tag["confidence"]
        ))

    connection.commit()
    connection.close()


# ============================================================
# BILDER AUS DATENBANK LADEN
# ============================================================

def get_all_images():
    connection = get_connection()

    query = """
        SELECT
            b.id,
            b.dateiname,
            b.pfad,
            b.hochgeladen_am,
            GROUP_CONCAT(t.tag, ', ') AS tags
        FROM bilder b
        LEFT JOIN tags t
            ON b.id = t.bild_id
        GROUP BY b.id
        ORDER BY b.id DESC
    """

    dataframe = pd.read_sql_query(
        query,
        connection
    )

    connection.close()

    return dataframe


# ============================================================
# TAGS LADEN
# ============================================================

def get_all_tags():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT tag
        FROM tags
        ORDER BY tag
    """)

    tags = [
        row[0]
        for row in cursor.fetchall()
    ]

    connection.close()

    return tags


# ============================================================
# NACH TAGS SUCHEN
# ============================================================

def search_images(selected_tags):
    """
    Liefert Bilder, die alle ausgewählten Tags besitzen.
    """

    if not selected_tags:
        return get_all_images()

    connection = get_connection()

    placeholders = ",".join(
        ["?"] * len(selected_tags)
    )

    query = f"""
        SELECT
            b.id,
            b.dateiname,
            b.pfad,
            b.hochgeladen_am,
            GROUP_CONCAT(t2.tag, ', ') AS tags
        FROM bilder b
        JOIN tags t
            ON b.id = t.bild_id
        LEFT JOIN tags t2
            ON b.id = t2.bild_id
        WHERE t.tag IN ({placeholders})
        GROUP BY b.id
        HAVING COUNT(DISTINCT t.tag) = ?
        ORDER BY b.id DESC
    """

    parameters = selected_tags + [len(selected_tags)]

    dataframe = pd.read_sql_query(
        query,
        connection,
        params=parameters
    )

    connection.close()

    return dataframe


# ============================================================
# BILD LÖSCHEN
# ============================================================

def delete_image(image_id):
    connection = get_connection()
    cursor = connection.cursor()

    # Pfad des Bildes herausfinden
    cursor.execute("""
        SELECT pfad
        FROM bilder
        WHERE id = ?
    """, (image_id,))

    result = cursor.fetchone()

    if result:
        path = result[0]

        # Datei löschen
        if os.path.exists(path):
            os.remove(path)

    # Tags löschen
    cursor.execute("""
        DELETE FROM tags
        WHERE bild_id = ?
    """, (image_id,))

    # Bild löschen
    cursor.execute("""
        DELETE FROM bilder
        WHERE id = ?
    """, (image_id,))

    connection.commit()
    connection.close()


# ============================================================
# HEADER
# ============================================================

st.title("🗃️ Meine Fundgrube")

st.write(
    "Bilder hochladen, automatisch mit KI verschlagworten "
    "und später über die Tags wiederfinden."
)


# ============================================================
# SEITENLEISTE
# ============================================================

with st.sidebar:

    st.header("⚙️ Einstellungen")

    st.write(
        f"**Mindestwahrscheinlichkeit:** "
        f"{MIN_CONFIDENCE:.0%}"
    )

    st.write(
        f"**Maximale Tags pro Bild:** "
        f"{MAX_TAGS}"
    )

    st.divider()

    if model is None:
        st.error(
            "⚠️ KI-Modell nicht gefunden.\n\n"
            "Lege `model.h5` in den Ordner `model/`."
        )
    else:
        st.success("✅ KI-Modell geladen")

    if labels:
        st.success(
            f"✅ {len(labels)} Klassen geladen"
        )
    else:
        st.warning(
            "Keine labels.txt gefunden."
        )


# ============================================================
# TABS
# ============================================================

tab_upload, tab_search, tab_all = st.tabs([
    "📤 Bilder hochladen",
    "🔎 Fundgrube durchsuchen",
    "🖼️ Alle Bilder"
])


# ============================================================
# UPLOAD
# ============================================================

with tab_upload:

    st.header("📤 Neue Bilder hinzufügen")

    uploaded_files = st.file_uploader(
        "Bilder auswählen",
        type=[
            "jpg",
            "jpeg",
            "png",
            "webp"
        ],
        accept_multiple_files=True
    )

    if uploaded_files:

        st.write(
            f"**{len(uploaded_files)} Bild(er) ausgewählt.**"
        )

        if st.button(
            "🤖 Bilder analysieren und speichern",
            type="primary"
        ):

            if model is None:
                st.error(
                    "Das KI-Modell ist nicht verfügbar."
                )

            else:

                progress = st.progress(0)

                for index, uploaded_file in enumerate(
                    uploaded_files
                ):

                    try:

                        # Bild öffnen
                        image = Image.open(
                            uploaded_file
                        )

                        # KI-Analyse
                        predicted_tags = predict_tags(
                            image
                        )

                        # Bild speichern
                        filename, path = save_image(
                            image,
                            uploaded_file.name
                        )

                        # Datenbank
                        save_to_database(
                            filename,
                            path,
                            predicted_tags
                        )

                        # Ergebnis anzeigen
                        st.success(
                            f"✅ {uploaded_file.name} gespeichert"
                        )

                        if predicted_tags:

                            tag_text = ", ".join(
                                [
                                    f"{item['tag']} "
                                    f"({item['confidence']:.0%})"
                                    for item in predicted_tags
                                ]
                            )

                            st.write(
                                f"**Erkannte Tags:** {tag_text}"
                            )

                        else:

                            st.warning(
                                "Keine Tags mit ausreichender "
                                "Sicherheit erkannt."
                            )

                    except Exception as error:

                        st.error(
                            f"Fehler bei "
                            f"{uploaded_file.name}: {error}"
                        )

                    progress.progress(
                        (index + 1) /
                        len(uploaded_files)
                    )

                st.success(
                    "🎉 Alle Bilder wurden verarbeitet!"
                )

                st.rerun()


# ============================================================
# SUCHE
# ============================================================

with tab_search:

    st.header("🔎 Fundgrube durchsuchen")

    available_tags = get_all_tags()

    if not available_tags:

        st.info(
            "Es wurden noch keine Bilder mit Tags gespeichert."
        )

    else:

        selected_tags = st.multiselect(
            "Nach Tags suchen",
            options=available_tags,
            placeholder="z. B. Hund, Auto, Landschaft ..."
        )

        if selected_tags:

            st.write(
                "**Gesuchte Tags:** "
                + ", ".join(selected_tags)
            )

        results = search_images(
            selected_tags
        )

        st.write(
            f"**{len(results)} Bild(er) gefunden**"
        )

        if results.empty:

            st.warning(
                "Keine passenden Bilder gefunden."
            )

        else:

            columns = st.columns(4)

            for index, row in results.iterrows():

                column = columns[
                    index % 4
                ]

                with column:

                    if os.path.exists(row["pfad"]):

                        st.image(
                            row["pfad"],
                            use_container_width=True
                        )

                    else:

                        st.error(
                            "Bilddatei nicht gefunden."
                        )

                    st.caption(
                        f"🏷️ {row['tags'] or 'Keine Tags'}"
                    )

                    st.caption(
                        f"📅 {row['hochgeladen_am'][:10]}"
                    )

                    if st.button(
                        "🗑️ Löschen",
                        key=f"delete_search_{row['id']}"
                    ):

                        delete_image(
                            int(row["id"])
                        )

                        st.success(
                            "Bild gelöscht."
                        )

                        st.rerun()


# ============================================================
# ALLE BILDER
# ============================================================

with tab_all:

    st.header("🖼️ Alle gespeicherten Bilder")

    all_images = get_all_images()

    if all_images.empty:

        st.info(
            "Noch keine Bilder vorhanden."
        )

    else:

        st.write(
            f"**{len(all_images)} Bild(er) gespeichert**"
        )

        columns = st.columns(4)

        for index, row in all_images.iterrows():

            column = columns[
                index % 4
            ]

            with column:

                if os.path.exists(row["pfad"]):

                    st.image(
                        row["pfad"],
                        use_container_width=True
                    )

                else:

                    st.error(
                        "Bilddatei nicht gefunden."
                    )

                st.caption(
                    f"🏷️ {row['tags'] or 'Keine Tags'}"
                )

                if st.button(
                    "🗑️ Bild löschen",
                    key=f"delete_all_{row['id']}"
                ):

                    delete_image(
                        int(row["id"])
                    )

                    st.success(
                        "Bild gelöscht."
                    )

                    st.rerun()
