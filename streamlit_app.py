import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Configuration Pro
st.set_page_config(page_title="ROTAGAMING GNF - Business", layout="wide")

# Style sombre "Gaming"
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { color: #00ff00; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #00ff00; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 ROTAGAMING : Expert & Gestion")

# --- CHARGEMENT DES DONNÉES ---
def load_data(file, columns):
    try:
        df = pd.read_csv(file)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=columns)

df_ventes = load_data('database_ventes.csv', ["Date", "Prestation", "Jeu", "Client", "Revenu"])
df_depenses = load_data('database_depenses.csv', ["Date", "Type", "Description", "Montant"])

# --- NAVIGATION ---
menu = st.sidebar.selectbox("Menu Principal", ["Tableau de Bord", "Ajouter une Vente", "Ajouter une Dépense"])

# --- OPTION 1 : TABLEAU DE BORD ---
if menu == "Tableau de Bord":
    total_revenu = df_ventes['Revenu'].sum()
    total_depense = df_depenses['Montant'].sum()
    benefice_reel = total_revenu - total_depense

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("TOTAL ENCAISSÉ", f"{total_revenu:,.0f} GNF".replace(",", " "))
    with col2:
        st.metric("TOTAL DÉPENSES", f"{total_depense:,.0f} GNF".replace(",", " "), delta_color="inverse")
    with col3:
        st.metric("BÉNÉFICE NET", f"{benefice_reel:,.0f} GNF".replace(",", " "))

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Journal des Ventes")
        st.dataframe(df_ventes.sort_values(by="Date", ascending=False), use_container_width=True)
    with c2:
        st.subheader("Journal des Dépenses")
        st.dataframe(df_depenses.sort_values(by="Date", ascending=False), use_container_width=True)

# --- OPTION 2 : AJOUTER UNE VENTE ---
elif menu == "Ajouter une Vente":
    st.subheader("🛒 Enregistrer un nouveau revenu")
    with st.form("form_vente"):
        date_v = st.date_input("Date", datetime.now())
        presta = st.selectbox("Type de Service", ["Installation Jeu Solo", "Installation Jeu Online", "Abonnement", "Vente Matériel"])
        jeu = st.text_input("Nom du Jeu / Article")
        client = st.text_input("Nom du Client")
        prix = st.number_input("Somme reçue (GNF)", min_value=0, step=5000)
        
        if st.form_submit_button("Valider la Vente"):
            new_v = {"Date": date_v, "Prestation": presta, "Jeu": jeu, "Client": client, "Revenu": prix}
            df_ventes = pd.concat([df_ventes, pd.DataFrame([new_v])], ignore_index=True)
            df_ventes.to_csv('database_ventes.csv', index=False)
            st.success("Vente enregistrée !")

# --- OPTION 3 : AJOUTER UNE DÉPENSE ---
elif menu == "Ajouter une Dépense":
    st.subheader("📉 Enregistrer une charge / achat")
    with st.form("form_depense"):
        date_d = st.date_input("Date", datetime.now())
        type_d = st.selectbox("Type de dépense", ["Loyer", "Électricité", "Achat Matériel", "Internet", "Transport", "Autre"])
        desc = st.text_input("Détails (ex: Facture EDG, Achat Clé USB)")
        montant = st.number_input("Montant payé (GNF)", min_value=0, step=1000)
        
        if st.form_submit_button("Enregistrer la Dépense"):
            new_d = {"Date": date_d, "Type": type_d, "Description": desc, "Montant": montant}
            df_depenses = pd.concat([df_depenses, pd.DataFrame([new_d])], ignore_index=True)
            df_depenses.to_csv('database_depenses.csv', index=False)
            st.success("Dépense notée !")
