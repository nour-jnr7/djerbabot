import streamlit as st
import openai
import wikipedia
import requests
import folium
import streamlit.components.v1 as components

# ─── CONFIGURATION OPENROUTER & STREAMLIT ────────────────────────────────────
openai.api_base = "https://openrouter.ai/api/v1"
openrouter_api_key = st.secrets["openrouter"]["api_key"]

st.set_page_config(page_title="🌴 DjerbaExplorer", layout="wide")

# ─── STYLE CSS POUR UN DESIGN RADICAL ET MODERNE ─────────────────────────────
st.markdown("""
    <style>
    body {
        font-family: 'Arial', sans-serif;
        background: linear-gradient(135deg, #ff99cc, #66ccff);
        color: #333;
        margin: 0;
    }

    .stApp {
        background-color: transparent;
    }

    h1 {
        font-size: 3em;
        text-align: center;
        color: #ffffff;
        text-shadow: 3px 3px 5px rgba(0, 0, 0, 0.3);
    }

    .stSidebar {
        background-color: #2b2d42;
        color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
    }

    .stSidebar h1 {
        font-size: 1.8em;
        color: #f7f7f7;
    }

    .stButton button {
        background-color: #ff4081;
        color: white;
        font-size: 1.2em;
        padding: 12px 24px;
        border-radius: 8px;
        border: none;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.3);
        cursor: pointer;
    }

    .stButton button:hover {
        background-color: #e3005f;
        box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.3);
    }

    .stTab {
        padding: 20px;
        border-radius: 12px;
        background-color: #ffffff;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .stTab h2 {
        font-size: 1.8em;
        margin-bottom: 15px;
        color: #333;
    }

    .stTextInput input {
        font-size: 1.1em;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ddd;
        width: 100%;
        box-sizing: border-box;
    }

    .stTextInput input:focus {
        border: 2px solid #ff4081;
    }

    .stMarkdown {
        font-size: 1.2em;
        color: #555;
        line-height: 1.6;
    }

    .stImage {
        border-radius: 12px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
    }

    /* Chatbot response style */
    .chatbot-response {
        background-color: #2b2d42;
        color: #fff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        font-size: 1.1em;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# ─── INITIALISATIONS ──────────────────────────────────────────────────────────
wikipedia.set_lang("fr")

# ─── LISTE DES POINTS D’INTÉRÊT ───────────────────────────────────────────────
POINTS_INTERET = {
    "Synagogue El Ghriba": (33.7980, 10.8722),
    "Houmt Souk":          (33.8749, 10.8790),
    "Musée de Guellala":   (33.8060, 10.7590),
    "Djerba Explore Park": (33.8220, 10.8380),
    "Plage de Sidi Mahres": (33.8480, 10.9470),
    "Parc Crocodile Farm": (33.8015, 10.8172),
    "Île des Flamants Roses": (33.8235, 10.8810),
    "Mosquée Fadhloun":    (33.8472, 10.8519),
    "Vieux Phare de Djerba": (33.8701, 10.9304),
}

# ─── FONCTIONS UTILITAIRES ────────────────────────────────────────────────────
@st.cache_data
def get_weather():
    lat, lon = 33.8468, 10.8519  # centre de Djerba
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current_weather=true"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get("current_weather", {})
        if not data:
            return None
        if "temperature" in data and "windspeed" in data:
            return f"{data['temperature']}°C, vent {data['windspeed']} km/h"
        else:
            return "Données météo incomplètes."
    except requests.RequestException as e:
        return f"Erreur lors de la récupération de la météo : {e}"

# ─── BARRE LATÉRALE ───────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🌴 DjerbaExplorer")
    st.write("""
        Avec DjerbaBot, vous pouvez explorer les lieux, poser des questions et obtenir des informations locales en temps réel.
        Ce guide est là pour vous aider à découvrir Djerba sous tous ses aspects !
    """)
    st.write("🔗 [En savoir plus sur Djerba](https://fr.wikipedia.org/wiki/Djerba)")

# ─── INTERFACE PRINCIPALE AVEC ONGLETS ────────────────────────────────────────
st.title("🌴 DjerbaExplorer")
tab1, tab2, tab3 = st.tabs(["🌤️ Météo", "📍 Lieux d’intérêt", "❓ Questions générales"])

# ─── ONGLET MÉTÉO ─────────────────────────────────────────────────────────────
with tab1:
    st.header("🌤️ Météo actuelle à Djerba")
    weather = get_weather()
    if weather:
        st.success(f"**{weather}**")
    else:
        st.error("Impossible de récupérer la météo pour le moment.")

# ─── ONGLET LIEUX D’INTÉRÊT ───────────────────────────────────────────────────
with tab2:
    st.header("📍 Découvrez les lieux d’intérêt")
    lieu_selectionne = st.selectbox("Choisissez un lieu :", list(POINTS_INTERET.keys()))

    if lieu_selectionne:
        nom_lieu = lieu_selectionne
        lat, lon = POINTS_INTERET[nom_lieu]
        try:
            page = wikipedia.page(nom_lieu, auto_suggest=True)
            summary_fr = page.summary[:600] + "…"
            title = page.title

            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader(f"📍 {title}")
                st.write(summary_fr)
                st.markdown(f"[Voir sur Wikipédia]({page.url})")
                images = [u for u in page.images if u.lower().endswith((".png", ".jpg", ".jpeg"))]
                if images:
                    st.image(images[0], caption=title, use_container_width=True)

            with col2:
                m = folium.Map(location=[lat, lon], zoom_start=16)
                folium.Marker([lat, lon], tooltip=title).add_to(m)
                components.html(m._repr_html_(), height=400)
        except wikipedia.exceptions.PageError:
            st.warning(f"Pas d’info disponible pour {nom_lieu}.")

# ─── ONGLET QUESTIONS GÉNÉRALES ───────────────────────────────────────────────
with tab3:
    st.header("❓ Posez une question sur Djerba")
    question = st.text_input("✍️ Votre question :", key="input_general")

    if question:
        with st.spinner("⏳ Recherche en cours..."):
            # Recherche de lieu
            lieu = None
            for nom, coords in POINTS_INTERET.items():
                if nom.lower() in question.lower():
                    lieu = (nom, coords)
                    break

            if lieu:
                nom_lieu, (lat, lon) = lieu
                try:
                    page = wikipedia.page(nom_lieu, auto_suggest=True)
                    summary_fr = page.summary[:600] + "…"
                    title = page.title
                    st.subheader(f"📍 {title}")
                    st.write(summary_fr)
                    st.markdown(f"[Voir sur Wikipédia]({page.url})")
                    m = folium.Map(location=[lat, lon], zoom_start=16)
                    folium.Marker([lat, lon], tooltip=title).add_to(m)
                    components.html(m._repr_html_(), height=400)
                except wikipedia.exceptions.PageError:
                    st.warning(f"Pas d’info pour {nom_lieu}.")
            else:
                # Réponse IA via Gemini 2.5 Pro Experimental
                system_msg = {
                    "role": "system",
                    "content": (
                        "Tu es un guide touristique expert de Djerba, Tunisie. "
                        "Réponds uniquement sur Djerba, dans la langue de l’utilisateur."
                    )
                }
                user_msg = {"role": "user", "content": question}
                try:
                    resp = openai.ChatCompletion.create(
                        model="openai/gpt-4o-mini",
                        messages=[system_msg, user_msg]
                    )

                    # Extraction sécurisée
                    if "choices" in resp and len(resp["choices"]) > 0:
                        answer = resp["choices"][0]["message"]["content"]
                        st.markdown(f'<div class="chatbot-response">{answer}</div>', unsafe_allow_html=True)
                    else:
                        st.warning("La réponse du modèle est vide ou inattendue.")
                        st.json(resp)  # Affiche le retour pour analyse
                except Exception as e:
                    st.error(f"Erreur lors de l'appel à l'IA : {e}")
