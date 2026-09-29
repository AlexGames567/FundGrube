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
    model = load_model()
    labels = load_labels()

    print("================================")
    print("MODEL INPUT:")
    print(model.input)

    print("MODEL INPUT SHAPE:")
    print(model.input_shape)

    print("NUMBER OF INPUTS:")
    print(len(model.inputs))

    print("MODEL OUTPUT:")
    print(model.output)

    print("MODEL OUTPUT SHAPE:")
    print(model.output_shape)

    print("================================")

    input_shape = model.input_shape

    target_h = input_shape[1]
    target_w = input_shape[2]

    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((target_w, target_h))

    arr = np.asarray(img, dtype=np.float32)
    arr = (arr / 127.5) - 1.0
    arr = np.expand_dims(arr, axis=0)

    print("ACTUAL IMAGE ARRAY SHAPE:")
    print(arr.shape)

    prediction = model.predict(arr, verbose=0)

    print("PREDICTION:")
    print(prediction)

    top_index = int(np.argmax(prediction[0]))

    if 0 <= top_index < len(labels):
        return [labels[top_index]]

    return [FALLBACK_TAG]
