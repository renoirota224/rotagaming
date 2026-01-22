import streamlit as st
import pandas as pd
from datetime import datetime
import io

# 1. CONFIGURATION ET DESIGN
st.set_page_config(page_title="ROTAGAMING - ULTIMATE GESTION", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
        url("https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=2070");
        background-size: cover;
    }
    div[data-testid="stMetricValue"] { color: #00ff00; font-weight: bold; }
    .stButton>button { width: 100%; background: linear-gradient(45deg, #00ff00, #008000); color: black; font-weight: bold; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 ROTAGAMING : Hub de Gestion Professionnel")

# 2. CHARGEMENT SÉCURISÉ DES DONNÉES
def load_data(file, columns):
    try:
        df = pd.read_csv(file)
        # Sécurité : Ajouter les colonnes manquantes si le fichier est ancien
        for col in columns:
            if col not in df.columns:
                df[col] = "Payé" if col == "Statut" else 0
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=columns)

df_ventes = load_data('database_ventes.csv', ["Date", "Prestation", "Jeu", "Client", "Revenu", "Statut"])
df_depenses = load_data('database_depenses.csv', ["Date", "Type", "Description", "Montant"])

# 3. NAVIGATION
menu = st.sidebar.selectbox("🚀 MENU", ["Tableau de Bord", "🔥 Nouvelle Vente", "💸 Nouvelle Dépense", "📑 Gestion des Dettes"])

# 4. LOGIQUE DES PAGES
if menu == "Tableau de Bord":
    # Conversion numérique
    df_ventes['Revenu'] = pd.to_numeric(df_ventes['Revenu'], errors='coerce').fillna(0)
    df_depenses['Montant'] = pd.to_numeric(df_depenses['Montant'], errors='coerce').fillna(0)
    
    # Calculs avec filtres de statut
    total_rev = df_ventes[df_ventes['Statut'] == "Payé"]['Revenu'].sum()
    total_dettes = df_ventes[df_ventes['Statut'] == "Dette"]['Revenu'].sum()
    total_dep = df_depenses['Montant'].sum()
    net = total_rev - total_dep

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ENCAISSÉ", f"{total_rev:,.0f} GNF")
    c2.metric("DETTES", f"{total_dettes:,.0f} GNF", delta="À récupérer", delta_color="inverse")
    c3.metric("CHARGES", f"{total_dep:,.0f} GNF", delta_color="inverse")
    c4.metric("BÉNÉFICE NET", f"{net:,.0f} GNF")

    st.markdown("---")
    st.subheader("📝 Historique des 10 dernières opérations")
    st.dataframe(df_ventes.tail(10), use_container_width=True)

    # Zone de suppression
    with st.expander("🗑️ Supprimer une erreur"):
        if not df_ventes.empty:
            v_idx = st.selectbox("Sélectionner la vente", df_ventes.index, format_func=lambda x: f"{df_ventes.loc[x, 'Client']} - {df_ventes.loc[x, 'Revenu']} GNF")
            if st.button("Confirmer la suppression"):
                df_ventes = df_ventes.drop(v_idx)
                df_ventes.to_csv('database_ventes.csv', index=False)
                st.rerun()

elif menu == "🔥 Nouvelle Vente":
    with st.form("v_form"):
        col1, col2 = st.columns(2)
        d = col1.date_input("Date", datetime.now())
        p = col1.selectbox("Prestation", ["Installation PES", "Jeu PC", "Mise à jour", "Réparation"])
        c = col1.text_input("Client")
        j = col2.text_input("Jeu / Article")
        m = col2.number_input("Montant (GNF)", min_value=0, step=5000)
        s = col2.radio("Statut", ["Payé", "Dette"])
        
        if st.form_submit_button("VALIDER"):
            new_v = pd.DataFrame([{"Date": d, "Prestation": p, "Jeu": j, "Client": c, "Revenu": m, "Statut": s}])
            df_ventes = pd.concat([df_ventes, new_v], ignore_index=True)
            df_ventes.to_csv('database_ventes.csv', index=False)
            st.success("Enregistré !")

elif menu == "💸 Nouvelle Dépense":
    with st.form("d_form"):
        d_d = st.date_input("Date", datetime.now())
        t_d = st.selectbox("Type", ["Loyer", "EDG", "Internet", "Matériel", "Autre"])
        desc = st.text_input("Détails")
        mont = st.number_input("Montant (GNF)", min_value=0, step=1000)
        
        if st.form_submit_button("ENREGISTRER CHARGE"):
            new_d = pd.DataFrame([{"Date": d_d, "Type": t_d, "Description": desc, "Montant": mont}])
            df_depenses = pd.concat([df_depenses, new_d], ignore_index=True)
            df_depenses.to_csv('database_depenses.csv', index=False)
            st.warning("Dépense ajoutée.")

elif menu == "📑 Gestion des Dettes":
    st.subheader("🕵️ Suivi des impayés")
    dettes_only = df_ventes[df_ventes['Statut'] == "Dette"]
    if dettes_only.empty:
        st.success("Aucune dette en cours !")
    else:
        st.dataframe(dettes_only, use_container_width=True)
