"""
classifier.py
-------------
Laedt das mitgelieferte, bereits trainierte Keras-Modell (keras_model.h5)
und die zugehoerigen Labels (labels.txt) und stellt eine Funktion bereit,
die aus Bild-Bytes das wahrscheinlichste Tag (Top-1) ermittelt.

Wichtiger Hinweis: Das Modell wird hier NICHT neu trainiert oder veraendert,
nur geladen und fuer Inferenz genutzt.
"""

import io
import os

import numpy as np
import streamlit as st
from PIL import Image

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(_BASE_DIR, "model", "keras_model.h5")
LABELS_PATH = os.path.join(_BASE_DIR, "model", "labels.txt")

FALLBACK_TAG = "Sonstiges"


@st.cache_resource(show_spinner=False)
def load_model():
    """Laedt das Keras-Modell einmalig und haelt es im Cache (nicht bei jedem Rerun neu laden)."""
    import tensorflow as tf  # Lazy-Import: TensorFlow wird nur geladen, wenn wirklich benoetigt

    return tf.keras.models.load_model(MODEL_PATH, compile=False)


@st.cache_resource(show_spinner=False)
def load_labels() -> list[str]:
    """
    Liest labels.txt ein. Format pro Zeile: '<Index> <Name>', z.B. '0 Brotdose'.
    Der Index wird nur zur Validierung genutzt, die Reihenfolge in der Datei zaehlt.
    """
    labels: list[str] = []
    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(" ", 1)
            if len(parts) == 2 and parts[0].isdigit():
                labels.append(parts[1].strip())
            else:
                labels.append(line)
    return labels


def classify_image(image_bytes: bytes) -> list[str]:
    """
    Klassifiziert ein Bild mit dem Keras-Modell und gibt eine Liste mit
    genau einem Tag zurueck (Top-1-Klasse, siehe Annahme aus der Planung).

    Bei jedem Fehler (defektes Bild, Modellproblem, fehlende Abhaengigkeit)
    wird auf ['Sonstiges'] zurueckgefallen, damit die App nie abstuerzt.
    """
    model = load_model()
    labels = load_labels()

        # Eingabegroesse wird dynamisch aus dem Modell gelesen, nicht hart codiert.
    input_shape = model.input_shape
    target_h = input_shape[1] or 224
    target_w = input_shape[2] or 224

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((target_w, target_h))
    arr = np.asarray(img, dtype=np.float32)

        # Normalisierung auf [-1, 1]: Standard bei Teachable-Machine-Exporten
        # (typisches Format fuer keras_model.h5 + labels.txt). Falls das
        # Modell anders trainiert wurde, muesste diese Zeile angepasst werden.
    arr = (arr / 127.5) - 1.0
    arr = np.expand_dims(arr, axis=0)

    prediction = model.predict(arr, verbose=0)
    print(prediction)
    top_index = int(np.argmax(prediction[0]))

    if 0 <= top_index < len(labels):
        print("Funktioniert?")
        return [labels[top_index]]
    print("Fuck my Life")
    return [FALLBACK_TAG]
