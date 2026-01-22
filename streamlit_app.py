import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Configuration de la page
st.set_page_config(page_title="ROTAGAMING - ULTIMATE GESTION", layout="wide")

# CSS pour l'image de fond et le style Gaming
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.8), rgba(0, 0, 0, 0.8)), 
        url("https://images.unsplash.com/photo-1542751371-adc38448a05e?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80");
        background-size: cover;
    }
    .main { color: white; }
    div[data-testid="stMetricValue"] { color: #00ff00; font-size: 30px; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 10px; background: linear-gradient(45deg, #00ff00, #008000); color: black; font-weight: bold; border: none; }
    .css-1d391kg { background-color: rgba(0, 0, 0, 0.7); } /* Sidebar transparency */
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 ROTAGAMING : Hub de Gestion Professionnel")

# --- CHARGEMENT DES DONNÉES ---
def load_data(file, columns):
    try:
        df = pd.read_csv(file)
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=columns)

df_ventes = load_data('database_ventes.csv', ["Date", "Prestation", "Jeu", "Client", "Revenu", "Statut"])
df_depenses = load_data('database_depenses.csv', ["Date", "Type", "Description", "Montant"])

# --- NAVIGATION ---
menu = st.sidebar.selectbox("🚀 MENU PRINCIPAL", 
    ["Tableau de Bord", "🔥 Nouvelle Vente", "💸 Nouvelle Dépense", "📑 Gestion des Dettes"])

# --- 1. TABLEAU DE BORD ---
if menu == "Tableau de Bord":
    df_ventes['Revenu'] = pd.to_numeric(df_ventes['Revenu'], errors='coerce').fillna(0)
    df_depenses['Montant'] = pd.to_numeric(df_depenses['Montant'], errors='coerce').fillna(0)
    
    # Calculs
    total_rev = df_ventes[df_ventes['Statut'] == "Payé"]['Revenu'].sum()
    dettes = df_ventes[df_ventes['Statut'] == "Dette"]['Revenu'].sum()
    total_dep = df_depenses['Montant'].sum()
    net = total_rev - total_dep

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("ENCAISSÉ", f"{total_rev:,.0f} GNF".replace(",", " "))
    with col2:
        st.metric("DETTES CLIENTS", f"{dettes:,.0f} GNF".replace(",", " "), delta="À récupérer", delta_color="inverse")
    with col3:
        st.metric("CHARGES", f"{total_dep:,.0f} GNF".replace(",", " "), delta_color="inverse")
    with col4:
        st.metric("BÉNÉFICE RÉEL", f"{net:,.0f} GNF".replace(",", " "))

    st.markdown("---")
    
    # ANALYSE PAR JEU
    if not df_ventes.empty:
        st.subheader("🏆 Top Services (Revenus)")
        top_service = df_ventes.groupby('Prestation')['Revenu'].sum().sort_values(ascending=False)
        st.bar_chart(top_service)

    # SUPPRESSION
    with st.expander("⚠️ Zone de Correction (Supprimer une erreur)"):
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if not df_ventes.empty:
                v_idx = st.selectbox("Vente à supprimer", df_ventes.index, format_func=lambda x: f"{df_ventes.loc[x, 'Client']} - {df_ventes.loc[x, 'Revenu']} GNF")
                if st.button("🗑️ Supprimer Vente"):
                    df_ventes = df_ventes.drop(v_idx)
                    df_ventes.to_csv('database_ventes.csv', index=False)
                    st.rerun()
        with col_s2:
            if not df_depenses.empty:
                d_idx = st.selectbox("Dépense à supprimer", df_depenses.index, format_func=lambda x: f"{df_depenses.loc[x, 'Description']} - {df_depenses.loc[x, 'Montant']} GNF")
                if st.button("🗑️ Supprimer Dépense"):
                    df_depenses = df_depenses.drop(d_idx)
                    df_depenses.to_csv('database_depenses.csv', index=False)
                    st.rerun()

# --- 2. NOUVELLE VENTE ---
elif menu == "🔥 Nouvelle Vente":
    st.subheader("💰 Enregistrer un Service")
    with st.form("vente_form"):
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            d = st.date_input("Date", datetime.now())
            p = st.selectbox("Prestation", ["Installation PES", "Patch / Mise à jour", "Jeu Complet PC", "Abonnement Salle", "Réparation"])
            c = st.text_input("Nom du Client")
        with col_v2:
            j = st.text_input("Jeu / Article")
            m = st.number_input("Montant (GNF)", min_value=0, step=5000)
            s = st.radio("Statut du paiement", ["Payé", "Dette"])
        
        if st.form_submit_button("VALIDER L'OPÉRATION"):
            new_v = {"Date": d, "Prestation": p, "Jeu": j, "Client": c, "Revenu": m, "Statut": s}
            df_ventes = pd.concat([df_ventes, pd.DataFrame([new_v])], ignore_index=True)
            df_ventes.to_csv('database_ventes.csv', index=False)
            st.success(f"Opération enregistrée pour {c} !")

# --- 3. NOUVELLE DÉPENSE ---
elif menu == "💸 Nouvelle Dépense":
    st.subheader("📉 Enregistrer un frais")
    with st.form("dep_form"):
        d_d = st.date_input("Date", datetime.now())
        t_d = st.selectbox("Catégorie", ["Électricité / EDG", "Loyer", "Internet / Data", "Achat Matériel", "Transport", "Autre"])
        desc = st.text_input("Description (ex: Facture Janvier)")
        mont = st.number_input("Montant payé (GNF)", min_value=0, step=1000)
        
        if st.form_submit_button("ENREGISTRER LA DÉPENSE"):
            new_d = {"Date": d_d, "Type": t_d, "Description": desc, "Montant": mont}
            df_depenses = pd.concat([df_depenses, pd.DataFrame([new_d])], ignore_index=True)
            df_depenses.to_csv('database_depenses.csv', index=False)
            st.warning("Dépense comptabilisée.")

# --- 4. GESTION DES DETTES ---
elif menu == "📑 Gestion des Dettes":
    st.subheader("🕵️ Suivi des impayés")
    dettes_df = df_ventes[df_ventes['Statut'] == "Dette"]
    if dettes_df.empty:
        st.success("Félicitations ! Aucun client n'a de dette.")
    else:
        st.dataframe(dettes_df, use_container_width=True)
        st.info("Lorsqu'un client paie, supprimez sa dette et ré-enregistrez la vente en 'Payé'.")
