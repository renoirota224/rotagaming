> Mes fichiers:
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io
import urllib.parse

# --- CONFIGURATION DESIGN ---
st.set_page_config(page_title="ROTAGAMING - BUSINESS PRO", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #00ecff; }
    [data-testid="stMetricValue"] { color: #00ecff !important; font-size: 35px !important; text-shadow: 0 0 10px #00ecff; }
    .stButton>button { background: linear-gradient(90deg, #00ecff, #0046ff); color: white; border-radius: 8px; font-weight: bold; border: none; }
    .sidebar .sidebar-content { background-color: #111; }
    </style>
    """, unsafe_allow_html=True)

# --- CHARGEMENT DES DONNÉES ---
def get_db(file, cols):
    try:
        df = pd.read_csv(file)
        for c in cols:
            if c not in df.columns: df[c] = 0
        return df
    except:
        return pd.DataFrame(columns=cols)

df_v = get_db('ventes_final.csv', ["Date", "Client", "Article", "Prix", "Source", "WhatsApp"])
df_s = get_db('stock_manettes.csv', ["Modele", "Quantite", "Prix_Achat", "Prix_Vente"])
df_d = get_db('depenses_pub.csv', ["Date", "Type", "Montant", "Note"])

# --- MENU ---
st.title("🎮 ROTAGAMING : Installation & Ventes")
menu = st.sidebar.radio("GESTION", [
    "📈 Performance & Pubs", 
    "💸 Caisse (Ventes & Install)", 
    "📦 Stock Manettes",
    "📢 WhatsApp Marketing",
    "📉 Frais & Pub Facebook"
])

# --- 1. PERFORMANCE & PUBS ---
if menu == "📈 Performance & Pubs":
    st.header("Analyse de tes Publicités Facebook")
    
    rev = pd.to_numeric(df_v['Prix']).sum()
    dep_pub = pd.to_numeric(df_d[df_d['Type'] == "Pub Facebook"]['Montant']).sum()
    benef = rev - dep_pub - (pd.to_numeric(df_s['Prix_Achat']).sum() if not df_s.empty else 0)

    c1, c2, c3 = st.columns(3)
    c1.metric("CHIFFRE D'AFFAIRES", f"{rev:,.0f} GNF")
    c2.metric("COÛT PUBS FB", f"{dep_pub:,.0f} GNF", delta_color="inverse")
    c3.metric("BÉNÉFICE ESTIMÉ", f"{benef:,.0f} GNF")

    if not df_v.empty:
        st.subheader("D'où viennent tes clients ?")
        fig = px.pie(df_v, names='Source', title="Origine des clients (Facebook vs Bouche à oreille)")
        st.plotly_chart(fig, use_container_width=True)

# --- 2. CAISSE ---
elif menu == "💸 Caisse (Ventes & Install)":
    st.subheader("💰 Enregistrer une vente ou installation")
    with st.form("vente_form"):
        c1, c2 = st.columns(2)
        cl = c1.text_input("Nom du Client")
        wa = c1.text_input("Numéro WhatsApp")
        src = c1.selectbox("Source du client", ["Pub Facebook", "Recommandation", "Passant"])
        
        type_v = c2.selectbox("Type d'opération", ["Vente Manette", "Installation Jeux PC", "Pack Complet"])
        art = c2.text_input("Détails (ex: Manette PS4 Noir / PES 17)")
        prix = c2.number_input("Somme payée (GNF)", step=5000)
        
        if st.form_submit_button("VALIDER L'OPÉRATION"):
            new_v = pd.DataFrame([{"Date": str(datetime.now().date()), "Client": cl, "Article": art, "Prix": prix, "Source": src, "WhatsApp": wa}])
            df_v = pd.concat([df_v, new_v], ignore_index=True)
            df_v.to_csv('ventes_final.csv', index=False)
            st.success("Enregistré !")

# --- 3. STOCK MANETTES ---
elif menu == "📦 Stock Manettes":
    st.subheader("🕹️ Inventaire des Manettes")
    with st.expander("Ajouter un nouveau modèle"):
        with st.form("stock_form"):
            mod = st.text_input("Modèle (ex: PS4 Pro Dualshock)")
            qte = st.number_input("Quantité reçue", min_value=1)
            pa = st.number_input("Prix d'Achat (GNF)", step=1000)
            pv = st.number_input("Prix de Vente prévu (GNF)", step=1000)
            if st.form_submit_button("Ajouter au stock"):
                new_s = pd.DataFrame([{"Modele": mod, "Quantite": qte, "Prix_Achat": pa, "Prix_Vente": pv}])
                df_s = pd.concat([df_s, new_s], ignore_index=True)
                df_s.to_csv('stock_manettes.csv', index=False)
    st.dataframe(df_s, use_container_width=True)

# --- 4. WHATSAPP MARKETING ---

> Mes fichiers:
elif menu == "📢 WhatsApp Marketing":
    st.subheader("🔗 Générateur de lien pour Pub Facebook")
    st.info("Utilise ce lien dans tes publicités Facebook pour que les clients t'envoient un message direct.")
    
    pre_msg = st.text_input("Message automatique (ex: Bonjour ROTAGAMING, je veux installer PES)")
    mon_num = "224622000000" # REMPLACE PAR TON NUMÉRO
    
    link = f"https://wa.me/{mon_num}?text={urllib.parse.quote(pre_msg)}"
    st.code(link)
    st.write("Copie ce lien dans le bouton 'Envoyer un message' de ta pub Facebook.")

# --- 5. FRAIS & PUBS ---
elif menu == "📉 Frais & Pub Facebook":
    st.subheader("Dépenses Publicitaires & Charges")
    with st.form("dep_form"):
        tp = st.selectbox("Type", ["Pub Facebook", "Connexion Internet", "Électricité", "Loyer"])
        mt = st.number_input("Montant (GNF)", step=1000)
        nt = st.text_input("Note")
        if st.form_submit_button("Enregistrer Frais"):
            new_d = pd.DataFrame([{"Date": str(datetime.now().date()), "Type": tp, "Montant": mt, "Note": nt}])
            df_d = pd.concat([df_d, new_d], ignore_index=True)
            df_d.to_csv('depenses_pub.csv', index=False)
            st.rerun()
