import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Configuration
st.set_page_config(page_title="ROTAGAMING GNF - Pro", layout="wide")

# Style Gaming
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
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=columns)

df_ventes = load_data('database_ventes.csv', ["Date", "Prestation", "Jeu", "Client", "Revenu"])
df_depenses = load_data('database_depenses.csv', ["Date", "Type", "Description", "Montant"])

# --- NAVIGATION ---
menu = st.sidebar.selectbox("Navigation", ["Tableau de Bord", "Ajouter une Vente", "Ajouter une Dépense"])

# --- 1. TABLEAU DE BORD ---
if menu == "Tableau de Bord":
    df_ventes['Revenu'] = pd.to_numeric(df_ventes['Revenu'], errors='coerce').fillna(0)
    df_depenses['Montant'] = pd.to_numeric(df_depenses['Montant'], errors='coerce').fillna(0)
    
    total_rev = df_ventes['Revenu'].sum()
    total_dep = df_depenses['Montant'].sum()
    net = total_rev - total_dep

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("TOTAL REVENUS", f"{total_rev:,.0f} GNF".replace(",", " "))
    with col2:
        st.metric("TOTAL DÉPENSES", f"{total_dep:,.0f} GNF".replace(",", " "), delta_color="inverse")
    with col3:
        st.metric("BÉNÉFICE NET", f"{net:,.0f} GNF".replace(",", " "))

    st.markdown("---")
    
    # SECTION SUPPRESSION
    with st.expander("🗑️ Supprimer une erreur (Vente ou Dépense)"):
        type_suppr = st.radio("Que voulez-vous supprimer ?", ["Une Vente", "Une Dépense"])
        
        if type_suppr == "Une Vente" and not df_ventes.empty:
            vente_a_suppr = st.selectbox("Sélectionnez la vente à supprimer", df_ventes.index, format_func=lambda x: f"{df_ventes.iloc[x]['Date']} - {df_ventes.iloc[x]['Client']} ({df_ventes.iloc[x]['Revenu']} GNF)")
            if st.button("Confirmer la suppression de la vente"):
                df_ventes = df_ventes.drop(vente_a_suppr)
                df_ventes.to_csv('database_ventes.csv', index=False)
                st.success("Vente supprimée !")
                st.rerun()
        
        elif type_suppr == "Une Dépense" and not df_depenses.empty:
            dep_a_suppr = st.selectbox("Sélectionnez la dépense à supprimer", df_depenses.index, format_func=lambda x: f"{df_depenses.iloc[x]['Date']} - {df_depenses.iloc[x]['Description']} ({df_depenses.iloc[x]['Montant']} GNF)")
            if st.button("Confirmer la suppression de la dépense"):
                df_depenses = df_depenses.drop(dep_a_suppr)
                df_depenses.to_csv('database_depenses.csv', index=False)
                st.success("Dépense supprimée !")
                st.rerun()
        else:
            st.info("Aucune donnée à supprimer pour le moment.")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Dernières Ventes")
        st.dataframe(df_ventes.tail(10), use_container_width=True)
    with c2:
        st.subheader("Dernières Dépenses")
        st.dataframe(df_depenses.tail(10), use_container_width=True)

# --- 2. AJOUTER UNE VENTE ---
elif menu == "Ajouter une Vente":
    st.subheader("🛒 Enregistrer une Vente")
    with st.form("form_v", clear_on_submit=True):
        d_v = st.date_input("Date", datetime.now())
        type_v = st.selectbox("Prestation", ["Installation PES", "Installation Autre Jeu", "Mise à jour", "Vente Matériel"])
        nom_jeu = st.text_input("Jeu / Article")
        nom_client = st.text_input("Client")
        prix_v = st.number_input("Montant Reçu (GNF)", min_value=0, step=5000)
        
        if st.form_submit_button("Valider la Vente"):
            n_v = {"Date": d_v, "Prestation": type_v, "Jeu": nom_jeu, "Client": nom_client, "Revenu": prix_v}
            df_ventes = pd.concat([df_ventes, pd.DataFrame([n_v])], ignore_index=True)
            df_ventes.to_csv('database_ventes.csv', index=False)
            st.success("Vente enregistrée !")
            st.rerun()

# --- 3. AJOUTER UNE DÉPENSE ---
elif menu == "Ajouter une Dépense":
    st.subheader("📉 Enregistrer une Dépense")
    with st.form("form_d", clear_on_submit=True):
        d_d = st.date_input("Date", datetime.now())
        type_d = st.selectbox("Catégorie", ["Loyer", "Électricité", "Achat Matériel", "Internet", "Perte/Vol", "Autre"])
        desc_d = st.text_input("Description détaillée")
        prix_d = st.number_input("Montant Payé (GNF)", min_value=0, step=1000)
        
        if st.form_submit_button("Valider la Dépense"):
            n_d = {"Date": d_d, "Type": type_d, "Description": desc_d, "Montant": prix_d}
            df_depenses = pd.concat([df_depenses, pd.DataFrame([n_d])], ignore_index=True)
            df_depenses.to_csv('database_depenses.csv', index=False)
            st.success("Dépense enregistrée !")
            st.rerun()


