import streamlit as st
import numpy as np
import json

# --- Fonction pour charger le texte en fonction de la langue ---
def load_text(language):
    try:
        with open(f"lang_spt_{language}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Le fichier de langue 'lang_spt_{language}.json' n'a pas été trouvé.")
        return {}

# --- Création des fichiers de langue (lang_spt_fr.json et lang_spt_en.json) ---
# Assurez-vous que ces fichiers sont dans le même répertoire que votre script Streamlit


# --- Sélection de la langue ---
languages = ["fr", "en"]
selected_language = st.sidebar.selectbox(
    "🌐 " + load_text(st.session_state.get("language", "fr")).get("select_language", "Select language:"),
    languages,
    index=languages.index(st.session_state.get("language", "fr")) if st.session_state.get("language") else 0,
    format_func=lambda lang: "Français" if lang == "fr" else "English",
    key="language_selector"
)

# --- Mise à jour de la langue dans la session state ---
if "language" not in st.session_state or st.session_state["language"] != selected_language:
    st.session_state["language"] = selected_language
    st.rerun()

# --- Chargement du texte dans la langue sélectionnée ---
text = load_text(st.session_state["language"])

# --- Titre de l'application ---
st.title(text.get("title", "Standard Penetration Test (SPT) Calculator"))
st.markdown(text.get("subtitle", "A simple tool to calculate and estimate bearing capacity."))

# --- Saisie des données ---
st.subheader(text.get("input_data_header", "1. Input Test Data"))

profondeur = st.number_input(text.get("depth", "Test Depth (m)"), min_value=0.0, step=0.1)
n1 = st.number_input(text.get("n_blows_1", "Blow Count N1 (0-15 cm)"), min_value=0, step=1)
n2 = st.number_input(text.get("n_blows_2", "Blow Count N2 (15-30 cm)"), min_value=0, step=1)
n3 = st.number_input(text.get("n_blows_3", "Blow Count N3 (30-45 cm)"), min_value=0, step=1)

type_marteau = st.selectbox(
    text.get("hammer_type", "Hammer Type"),
    options=[
        text.get("hammer_donut", "Donut (Ce ≈ 0.45-0.60)"),
        text.get("hammer_safety", "Safety (Ce ≈ 0.70-0.85)"),
        text.get("hammer_automatic", "Automatic (Ce ≈ 0.80-1.00)"),
    ],
    index=1 if text["select_language"] == "Select language:" else 1 # Garder l'index par défaut
)

longueur_tige = st.number_input(text.get("rod_length", "Drill Rod Length (m)"), min_value=0.0, step=0.1, value=5.0)
diametre_forage = st.selectbox(
    text.get("borehole_diameter", "Borehole Diameter (mm) (optional)"),
    options=[60, 75, 100, 115, 150, 200],
    index=0
)
liner = st.checkbox(text.get("liner", "Split-spoon sampler with liner?"))
sigma_vo_prime = st.number_input(text.get("effective_stress", "Effective Vertical Stress (σ'vo) at test depth (kPa)"), min_value=0.0, step=0.1, value=100.0)
pa = st.number_input(text.get("atmospheric_pressure", "Reference Atmospheric Pressure (kPa)"), min_value=0.0, step=0.1, value=101.3)

# --- Calcul de Nfield ---
n_field = n2 + n3

# --- Détermination des facteurs de correction ---
st.subheader(text.get("calculation_header", "2. Correction Calculations"))

# Correction d'énergie (Ce)
if text.get("hammer_donut", "Donut") in type_marteau:
    ce = st.slider(text.get("energy_coefficient", "Energy Ratio (Ce)"), min_value=0.45, max_value=0.60, value=0.55, step=0.01)
elif text.get("hammer_safety", "Safety") in type_marteau:
    ce = st.slider(text.get("energy_coefficient", "Energy Ratio (Ce)"), min_value=0.70, max_value=0.85, value=0.80, step=0.01)
else:  # Automatique
    ce = st.slider(text.get("energy_coefficient", "Energy Ratio (Ce)"), min_value=0.80, max_value=1.00, value=0.90, step=0.01)

# Correction de la longueur de la tige (Cr)
if longueur_tige < 3:
    cr = 0.75
elif longueur_tige <= 4:
    cr = 0.85
elif longueur_tige <= 6:
    cr = 0.95
else:
    cr = 1.00
st.write(f"{text.get('rod_length_coefficient', 'Rod Length Correction Factor (Cr):')} {cr:.2f}")

# Correction du diamètre du forage (Cb)
if diametre_forage <= 115:
    cb = 1.00
elif diametre_forage == 150:
    cb = 1.05
elif diametre_forage == 200:
    cb = 1.15
else:
    cb = 1.00
st.write(f"{text.get('borehole_coefficient', 'Borehole Diameter Correction Factor (Cb):')} {cb:.2f}")

# Correction du tubage (Cs)
cs = 1.00 if liner else 1.20
st.write(f"{text.get('liner_coefficient', 'Sampler with Liner Correction Factor (Cs):')} {cs:.2f}")

# Correction de la pression de confinement (Cn) - Formule de Liao et Whitman
cn = np.sqrt(pa / sigma_vo_prime)
if cn > 2.0:
    cn = 2.0
st.write(f"{text.get('confinement_coefficient', 'Overburden Pressure Correction Factor (Cn):')} {cn:.2f}")

# --- Calcul des valeurs N corrigées ---
st.subheader(text.get("results_header", "3. Calculation Results"))

st.write(f"{text.get('n_field_value', 'Raw N-value (Nfield):')} **{n_field}**")

# Formule modifiée pour N60
n60 = n_field * ce * cb * cs * cr
st.write(f"{text.get('n60_value', 'N corrigé (énergie, diamètre, tubage, longueur) (N60):')} **{n60:.2f}**")

# Formule modifiée pour (N1)60
n1_60 = n60 * cn
st.write(f"{text.get('n1_60_value', 'N corrigé final (énergie, confinement) ((N1)60):')} **{n1_60:.2f}**")

# --- Estimation préliminaire de la capacité portante ---
st.subheader(text.get("bearing_capacity_header", "4. Preliminary Bearing Capacity Estimation"))

soil_type = st.selectbox(
    text.get("soil_type", "Soil Type (for estimation)"),
    options=[text.get("granular_soil", "Granular (Sand/Gravel)"), text.get("cohesive_soil", "Cohesive (Clay/Silt)")],
)

foundation_width = st.number_input(text.get("foundation_width", "Foundation Width (B) (m)"), min_value=0.5, step=0.5, value=1.0)
water_table_depth = st.number_input(text.get("water_table_depth", "Water Table Depth (m) (optional)"), min_value=0.0, step=0.5, value=10.0)

estimated_bearing_capacity = 0.0

if soil_type == text.get("granular_soil", "Granular (Sand/Gravel)"):
    # Corrélation simplifiée pour les sables (Meyerhof, 1956 - très approximatif)
    # Qa ≈ N60 / FOS (FOS = facteur de sécurité, ici simplifié à 10 pour l'exemple)
    fos = 10
    estimated_bearing_capacity = n60 / fos
elif soil_type == text.get("cohesive_soil", "Cohesive (Clay/Silt)"):
    # Corrélation simplifiée pour les argiles (Terzaghi - très approximatif)
    # Su ≈ k * N_field (k entre 25 et 100) et Qa ≈ Su / FOS
    k = st.slider("Coefficient k (pour argile, kPa/coup)", min_value=25, max_value=100, value=50, step=5)
    fos = 3
    estimated_bearing_capacity = (k * n_field) / fos

st.write(f"**{text.get('estimated_bearing_capacity', 'Estimated Allowable Bearing Capacity (kPa)')}:** {estimated_bearing_capacity:.2f}")
st.markdown(f"<small>{text.get('bearing_capacity_disclaimer', 'Note: This estimation is based on empirical correlations and is preliminary. A detailed geotechnical analysis is recommended.')}</small>", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown(f"Langue sélectionnée : **{text.get('select_language', '').replace('Sélectionnez la langue :', 'Français').replace('Select language:', 'English').split(': ')[0]}**: **{'Français' if st.session_state.language == 'fr' else 'English'}**")
