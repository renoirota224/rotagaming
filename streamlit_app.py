import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Configuration Pro
st.set_page_config(page_title="ROTAGAMING GNF - Pro", layout="wide")

# Style personnalisé
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    div[data-testid="stMetricValue"] { color: #00ff00; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #00ff00; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 ROTAGAMING : Gestion & Export")

# --- CHARGEMENT DES DONNÉES ---
def load_data(file, columns):
    try:
        df = pd.read_csv(file)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=columns)

df_ventes = load_data('database_ventes.csv', ["Date", "Prestation", "Jeu", "Client", "Revenu"])
df_depenses = load_data('database_depenses.csv', ["Date", "Type", "Description", "Montant"])

# --- NAVIGATION ---
menu = st.sidebar.selectbox("Menu Principal", ["Tableau de Bord", "Ajouter une Vente", "Ajouter une Dépense"])

# --- OPTION 1 : TABLEAU DE BORD & EXPORT ---
if menu == "Tableau de Bord":
    total_revenu = pd.to_numeric(df_ventes['Revenu']).sum()
    total_depense = pd.to_numeric(df_depenses['Montant']).sum()
    benefice_reel = total_revenu - total_depense

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("TOTAL ENCAISSÉ", f"{total_revenu:,.0f} GNF".replace(",", " "))
    with col2:
        st.metric("TOTAL DÉPENSES", f"{total_depense:,.0f} GNF".replace(",", " "), delta_color="inverse")
    with col3:
        st.metric("BÉNÉFICE NET", f"{benefice_reel:,.0f} GNF".replace(",", " "))

    st.markdown("---")
    
    # BOUTON D'EXPORT EXCEL
    st.subheader("📊 Exporter le Bilan")
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_ventes.to_excel(writer, sheet_name='Ventes', index=False)
        df_depenses.to_excel(writer, sheet_name='Depenses', index=False)
        # Création d'un petit résumé
        resume = pd.DataFrame({"Indicateur": ["Total Revenu", "Total Dépenses", "Bénéfice Net"], 
                               "Valeur (GNF)": [total_revenu, total_depense, benefice_reel]})
        resume.to_excel(writer, sheet_name='Resume', index=False)
    
    st.download_button(
        label="📥 Télécharger le bilan complet (Excel)",
        data=buffer,
        file_name=f"Bilan_ROTAGAMING_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
        mime="application/vnd.ms-excel"
    )

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Dernières Ventes")
        st.dataframe(df_ventes.tail(10), use_container_width=True)
    with c2:
        st.subheader("Dernières Dépenses")
        st.dataframe(df_depenses.tail(10), use_container_width=True)

# --- OPTION 2 : AJOUTER UNE VENTE ---
elif menu == "Ajouter une Vente":
    st.subheader("🛒 Nouvelle Vente")
    with st.form("form_vente"):
        date_v = st.date_input("Date", datetime.now())
        presta = st.selectbox("Type", ["Installation PES", "Installation Autre Jeu", "Abonnement", "Vente Matériel"])
        jeu = st.text_input("Jeu / Article")
        client = st.text_input("Client")
        prix = st.number_input("Prix (GNF)", min_value=0, step=5000)
        if st.form_submit_button("Enregistrer"):
            new_v = {"Date": date_v, "Prestation": presta, "Jeu": jeu, "Client": client, "Revenu": prix}
            df_ventes = pd.concat([df_ventes, pd.DataFrame([new_v])], ignore_index=True)
            df_ventes.to_csv('database_ventes.csv', index=False)
            st.success("Vente enregistrée !")

# --- OPTION 3 : AJOUTER UNE DÉPENSE ---
elif menu == "Ajouter une Dépense":
    st.subheader("📉 Nouvelle Charge")
    with st.form("form_depense"):
        date_d = st.date_input("Date", datetime.now())
        type_d = st.selectbox("Catégorie", ["Loyer", "Électricité", "Achat Matériel", "Internet", "Perte/Vol", "Autre"])
        desc = st.text_input("Détails")
        montant = st.number_input("Montant (GNF)", min_value=0, step=1000)

> Mes fichiers:
if st.form_submit_button("Enregistrer"):
            new_d = {"Date": date_d, "Type": type_d, "Description": desc, "Montant": montant}
            df_depenses = pd.concat([df_depenses, pd.DataFrame([new_d])], ignore_index=True)
            df_depenses.to_csv('database_depenses.csv', index=False)
            st.success("Dépense enregistrée !")

