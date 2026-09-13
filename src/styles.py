"""
styles.py
---------
Injiziert das komplette CSS fuer das "Fund Grube"-Design.
Alle Farbwerte wurden direkt aus den gelieferten Screenshots extrahiert
(per Pixel-Sampling), nicht frei erfunden.
"""

import streamlit as st

# --- Design-Tokens (aus den Screenshots extrahiert) -------------------------
COLOR_BG = "#FFFFFF"
COLOR_LIGHT_BLUE_FILL = "#EDF6FF"
COLOR_BLUE_BORDER = "#53AAFF"
COLOR_BLUE_TEXT = "#007AFF"
COLOR_PLACEHOLDER_FILL = "#E5E5E5"
COLOR_PLACEHOLDER_BORDER = "#000000"
COLOR_SEARCH_FILL = "#F6F5F5"
COLOR_SEARCH_BORDER = "#A8A6A1"


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&display=swap');

        .stApp {{
            background-color: {COLOR_BG};
        }}
        /* Streamlit-Standardabstaende etwas reduzieren, damit das Design kompakter wirkt */
        .block-container {{
            padding-top: 2rem;
            max-width: 900px;
        }}

        /* --- Logo "Fund Grube" ------------------------------------------ */
        .fg-logo-wrap {{
            display: flex;
            justify-content: center;
            margin-bottom: 1.5rem;
        }}
        .fg-logo {{
            display: inline-block;
            background-color: {COLOR_LIGHT_BLUE_FILL};
            border: 4px solid {COLOR_BLUE_BORDER};
            border-radius: 40px;
            padding: 0.6rem 3rem;
            transform: rotate(-4deg);
            font-family: 'Caveat', cursive;
            font-size: 3rem;
            font-weight: 700;
            color: {COLOR_BLUE_TEXT};
            line-height: 1;
        }}

        /* --- "Zuletzt Gefunden" Ueberschrift ------------------------------ */
        .fg-section-title {{
            font-style: italic;
            text-decoration: underline;
            color: #333333;
            margin: 0.5rem 0 0.8rem 0;
        }}

        /* --- Suchleiste: st.text_input via placeholder-Attribut anpassen -- */
        div[data-testid="stTextInput"] input {{
            background-color: {COLOR_SEARCH_FILL} !important;
            border: 2px solid {COLOR_SEARCH_BORDER} !important;
            border-radius: 30px !important;
            padding: 0.6rem 1rem 0.6rem 2.4rem !important;
            color: #333333 !important;
        }}
        div[data-testid="stTextInput"] {{
            position: relative;
        }}
        div[data-testid="stTextInput"]::before {{
            content: "\\1F50D";
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            z-index: 2;
            font-size: 0.95rem;
            opacity: 0.6;
            pointer-events: none;
        }}

        /* --- Upload-Icon-Button: st.file_uploader wird zum runden Icon --- */
        .fg-upload-wrap div[data-testid="stFileUploaderDropzone"] {{
            background-color: {COLOR_LIGHT_BLUE_FILL} !important;
            border: 4px solid {COLOR_BLUE_BORDER} !important;
            border-radius: 32px !important;
            width: 140px;
            height: 140px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }}
        /* Standardtexte/Icons von Streamlit im Dropzone-Bereich ausblenden */
        .fg-upload-wrap div[data-testid="stFileUploaderDropzone"] > * {{
            visibility: hidden;
        }}
        /* Eigenes Wolken-Icon per Pseudo-Element ueberlagern */
        .fg-upload-wrap div[data-testid="stFileUploaderDropzone"]::after {{
            content: "";
            position: absolute;
            width: 60px;
            height: 60px;
            background-repeat: no-repeat;
            background-position: center;
            background-size: contain;
            background-image: url("data:image/svg+xml;utf8,\
<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'>\
<path d='M20 44 a12 12 0 0 1 -2 -23.8 A14 14 0 0 1 45 17 a10 10 0 0 1 -1 27 z' \
fill='none' stroke='black' stroke-width='3'/>\
<line x1='32' y1='26' x2='32' y2='48' stroke='black' stroke-width='3'/>\
<polyline points='24,34 32,26 40,34' fill='none' stroke='black' stroke-width='3'/>\
</svg>");
            pointer-events: none;
            visibility: visible !important;
        }}
        .fg-upload-wrap small {{
            display: none;
        }}
        .fg-upload-caption {{
            text-align: center;
            color: #888888;
            font-size: 0.8rem;
            margin-top: 0.3rem;
        }}

        /* --- Bild-Platzhalter-Boxen (Grid) -------------------------------- */
        .fg-image-box {{
            background-color: {COLOR_PLACEHOLDER_FILL};
            border: 1.5px solid {COLOR_PLACEHOLDER_BORDER};
            border-radius: 2px;
            aspect-ratio: 3 / 4;
            width: 100%;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .fg-image-box img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        /* --- Tag-Boxen (KI-Tags / eigene Tags) ---------------------------- */
        .fg-tagbox-title {{
            font-weight: 600;
            margin-bottom: 0.4rem;
            color: #222222;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 22px !important;
        }}

        /* --- Tag-Chips ----------------------------------------------------- */
        .fg-chip {{
            display: inline-block;
            background-color: {COLOR_LIGHT_BLUE_FILL};
            border: 1.5px solid {COLOR_BLUE_BORDER};
            border-radius: 16px;
            padding: 0.15rem 0.7rem;
            margin: 0.15rem;
            font-size: 0.85rem;
            color: #222222;
        }}
        .fg-empty-hint {{
            color: #999999;
            font-size: 0.85rem;
            font-style: italic;
        }}

        /* --- Grosse Detail-Box-Buttons (Hochladen / Aendern / Loeschen) --- */
        div.stButton > button {{
            border-radius: 24px;
            font-weight: 600;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
