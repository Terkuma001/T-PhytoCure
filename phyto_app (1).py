
import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
from streamlit_option_menu import option_menu
from sklearn.feature_extraction.text import TfidfVectorizer

# Configure page
st.set_page_config(page_title="🌿 PhytoCure", layout="centered")

# Developer Info Box
st.markdown("""
<div style="background-color:#f0f8ff; padding:10px; border-radius:10px;">
<h6>Developed by: <strong>Terkuma Saaondo</strong></h6>
<p>A bioinformatics enthusiast focused on plant-based drug discovery and AI-powered health insights.</p>
</div>
""", unsafe_allow_html=True)

# Language Translation Dictionary
translations = {
    "title": {
        "English": "🌿 PhytoCure - Plant-Based Drug Discovery",
        "Español": "🌿 PhytoCure - Descubrimiento de Medicamentos Basados en Plantas",
        "हिंदी": "🌿 फाइटोक्योर - पौधे आधारित औषधि खोज",
        "Français": "🌿 PhytoCure - Découverte de médicaments à base de plantes"
    },
    "search_placeholder": {
        "English": "Enter botanical name...",
        "Español": "Ingrese el nombre botánico...",
        "हिंदी": "वनस्पति नाम दर्ज करें...",
        "Français": "Entrez le nom botanique..."
    }
}

# Language Selection Menu
lang = option_menu(
    menu_title=None,
    options=["English", "Español", "हिंदी", "Français"],
    icons=["globe", "flag", "flag", "flag"],
    default_index=0,
    orientation="horizontal"
)

# Set App Title Based on Language
st.title(translations["title"][lang])

# Fetch compounds from KNApSAcK
def get_knapsack_compounds(plant_name):
    try:
        url = "https://kanaya.nuap.jp/servlet/SearchServlet"
        params = {"action": "search", "query": plant_name, "type": "plant"}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find("table", {"class": "list_table"})
            compounds = []

            if table:
                rows = table.find_all("tr")[1:]
                for row in rows:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        compound = cols[0].get_text(strip=True)
                        percentage = cols[1].get_text(strip=True)
                        compounds.append({"Compound": compound, "Percentage Range": percentage})
            return compounds
    except Exception as e:
        st.error(f"Error fetching from KNApSAcK: {e}")
    return []

# Scrape Dr. Duke or PFAF info
def scrape_dr_duke(plant_name):
    try:
        url = f"https://pfaf.org/user/Search.aspx?LatinName={plant_name}"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        result = {}
        common_name_tag = soup.find("span", id="ctl00_ContentPlaceHolder1_lblCommon")
        uses_section = soup.find("div", id="uses")

        if common_name_tag:
            result["Common Name"] = common_name_tag.text.strip()
        if uses_section:
            result["Uses"] = uses_section.text.strip()
        return result
    except Exception:
        return {}

# Disease Prediction Logic
compound_disease_map = {
    "Curcumin": ["Arthritis", "Diabetes", "Cancer"],
    "Epigallocatechin gallate": ["Heart disease", "Obesity"],
    "Quercetin": ["Allergies", "Inflammation"],
    "Azadirachtin": ["Malaria", "Skin infection"]
}

vectorizer = TfidfVectorizer()
disease_descriptions = [
    "Anti-inflammatory and pain relief",
    "Metabolic regulation",
    "Immune system boost",
    "Antimicrobial properties",
    "Neuroprotective effects"
]
X = vectorizer.fit_transform(disease_descriptions)

def predict_diseases(compounds):
    unique_diseases = set()
    for compound in compounds:
        for disease in compound_disease_map.get(compound, []):
            unique_diseases.add(disease)
    return list(unique_diseases)[:5] if unique_diseases else ["No strong association found."]

# Main App Interface
plant_name = st.text_input("", placeholder=translations["search_placeholder"][lang])

if st.button("🔍 Search"):
    if plant_name:
        with st.spinner("Fetching data from global databases..."):
            knapsack_data = get_knapsack_compounds(plant_name)
            duke_data = scrape_dr_duke(plant_name)

            if knapsack_data:
                st.subheader("🧬 Bioactive Compounds")
                df = pd.DataFrame(knapsack_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("⚠️ No compound data found in KNApSAcK database.")

            if duke_data:
                st.subheader("🌿 Uses & Properties")
                for key, value in duke_data.items():
                    st.markdown(f"**{key}:** {value[:500]}...")
            else:
                st.info("ℹ️ No additional information from Dr. Duke’s database.")

            compound_names = [c["Compound"] for c in knapsack_data]
            predictions = predict_diseases(compound_names)
            st.subheader("🧠 AI-Predicted Diseases")
            st.write(", ".join(predictions))
    else:
        st.warning("Please enter a plant name.")
