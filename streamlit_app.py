import streamlit as st
import pandas as pd
from datetime import datetime
import io
import urllib.parse

# 1. CONFIGURATION ET DESIGN GAMING
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

st.title("🎮 ROTAGAMING : Hub de Gestion & Marketing")

# 2. CHARGEMENT SÉCURISÉ
def load_data(file, columns):
    try:
        df = pd.read_csv(file)
        for col in columns:
            if col not in df.columns:
                df[col] = "Payé" if col == "Statut" else 0
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=columns)

df_ventes = load_data('database_ventes.csv', ["Date", "Prestation", "Jeu", "Client", "Revenu", "Statut"])
df_depenses = load_data('database_depenses.csv', ["Date", "Type", "Description", "Montant"])

# 3. NAVIGATION AMÉLIORÉE
menu = st.sidebar.selectbox("🚀 MENU", ["Tableau de Bord", "🔥 Nouvelle Vente", "💸 Nouvelle Dépense", "📑 Gestion des Dettes", "📱 Marketing WhatsApp"])

# --- PAGE TABLEAU DE BORD ---
if menu == "Tableau de Bord":
    df_ventes['Revenu'] = pd.to_numeric(df_ventes['Revenu'], errors='coerce').fillna(0)
    df_depenses['Montant'] = pd.to_numeric(df_depenses['Montant'], errors='coerce').fillna(0)
    
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
    st.subheader("📝 Dernières Opérations")
    st.dataframe(df_ventes.tail(5), use_container_width=True)

# --- PAGE WHATSAPP (PROSPECTS) ---
elif menu == "📱 Marketing WhatsApp":
    st.subheader("📢 Envoyer un message au client")
    colw1, colw2 = st.columns(2)
    
    with colw1:
        nom_c = st.text_input("Nom du prospect / client")
        num_c = st.text_input("Numéro WhatsApp (ex: 224622...)", placeholder="224XXXXXXXXX")
    
    with colw2:
        msg_type = st.selectbox("Type de message", ["Confirmation Installation", "Relance Dette", "Promo Nouveau Jeu"])
        
        if msg_type == "Confirmation Installation":
            base_msg = f"Bonjour {nom_c}, votre jeu est installé et prêt chez ROTAGAMING ! Merci de votre confiance. 🎮"
        elif msg_type == "Relance Dette":
            base_msg = f"Bonjour {nom_c}, petit rappel concernant votre reste à payer chez ROTAGAMING. Merci de passer nous voir ! 😊"
        else:
            base_msg = f"Salut {nom_c} ! On vient de recevoir de nouveaux jeux et patchs chez ROTAGAMING. Passe vite voir ça ! 🔥"
        
        message = st.text_area("Modifier le message :", base_msg)

    if st.button("📲 Envoyer sur WhatsApp"):
        if num_c:
            # Encodage du message pour l'URL
            msg_encoded = urllib.parse.quote(message)
            whatsapp_url = f"https://wa.me/{num_c}?text={msg_encoded}"
            st.markdown(f'<a href="{whatsapp_url}" target="_blank" style="text-decoration:none;"><button style="width:100%; background-color:#25D366; color:white; border-radius:10px; padding:10px; border:none; font-weight:bold;">CLIQUER ICI POUR OUVRIR WHATSAPP</button></a>', unsafe_allow_html=True)
        else:
            st.error("Veuillez saisir un numéro de téléphone.")
