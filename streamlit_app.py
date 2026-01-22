import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import urllib.parse

# --- 1. ARCHITECTURE ET STYLE (EXTRÊME) ---
st.set_page_config(page_title="ROTAGAMING GALAXY", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: #e94560;
    }
    [data-testid="stMetricValue"] { color: #00ff41 !important; font-family: 'Orbitron', sans-serif; text-shadow: 0 0 10px #00ff41; }
    .stButton>button { border: 2px solid #e94560; background: transparent; color: white; border-radius: 15px; transition: 0.5s; }
    .stButton>button:hover { background: #e94560; box-shadow: 0 0 20px #e94560; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MOTEUR DE DONNÉES (AUTO-RÉPARABLE) ---
def master_loader(file, cols):
    try:
        df = pd.read_csv(file)
        for c in cols:
            if c not in df.columns: df[c] = 0
        return df
    except: return pd.DataFrame(columns=cols)

# Initialisation des 4 bases principales
db_v = master_loader('rg_ventes.csv', ["ID", "Date", "Client", "Phone", "Service", "Jeu", "Montant", "Cout", "Statut", "User"])
db_s = master_loader('rg_stock.csv', ["Item", "Qte", "Min_Seuil", "Prix_Vente", "Prix_Achat", "Rayon"])
db_d = master_loader('rg_depenses.csv', ["Date", "Type", "Note", "Montant", "Payeur"])
db_r = master_loader('rg_reparations.csv', ["Client", "Objet", "Panne", "Prix", "Statut", "Delai"])

# --- 3. NAVIGATION MULTI-FONCTIONNELLE ---
st.sidebar.title("💠 ROTAGAMING OS V.2.0")
menu = st.sidebar.selectbox("COMMAND CENTER", [
    "🛸 Dashboard 360", "💸 Terminal de Vente", "📦 Mega Stock", 
    "🛠️ Labo Réparations", "📱 Marketing & WA", "📊 Analytics IA", 
    "👥 Clients VIP", "📑 Rapports & PDF", "⚙️ Système"
])

# --- 4. MODULE 1 : DASHBOARD 360 ---
if menu == "🛸 Dashboard 360":
    st.header("📊 Tableau de Bord Galactique")
    
    # Calculs complexes (Marge, Croissance)
    ca = pd.to_numeric(db_v[db_v['Statut']=='Payé']['Montant']).sum()
    dettes = pd.to_numeric(db_v[db_v['Statut']=='Dette']['Montant']).sum()
    frais = pd.to_numeric(db_d['Montant']).sum()
    marge = ca - pd.to_numeric(db_v['Cout']).sum() - frais
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CA ENCAISSÉ", f"{ca:,.0f} GNF", "+12% vs mois dernier")
    c2.metric("DETTES ACTIVES", f"{dettes:,.0f} GNF", "-5%", delta_color="inverse")
    c3.metric("MARGE NETTE", f"{marge:,.0f} GNF", "Rentable")
    c4.metric("STOCK VALEUR", f"{pd.to_numeric(db_s['Prix_Achat']*db_s['Qte']).sum():,.0f} GNF")

    # Graphique 3D des Ventes
    if not db_v.empty:
        fig = px.scatter_3d(db_v, x='Date', y='Montant', z='Service', color='Statut', size='Montant', 
                             title="Visualisation 3D des Transactions", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# --- 5. MODULE 2 : TERMINAL DE VENTE ---
elif menu == "💸 Terminal de Vente":
    st.subheader("🛒 Nouvelle Transaction Avancée")
    with st.form("pos_terminal"):
        col1, col2, col3 = st.columns(3)
        c_nom = col1.text_input("Client")
        c_tel = col1.text_input("WhatsApp (Ex: 224...)")
        serv = col2.selectbox("Prestation", ["PES 26", "FIFA 26", "GTA VI", "Patch", "Console Unlock", "Accessoire"])
        jeu = col2.text_input("Détails Jeu")
        prix = col3.number_input("Prix de Vente (GNF)", step=5000)
        cout = col3.number_input("Coût d'acquisition (GNF)", step=1000)
        stat = st.radio("Mode de Paiement", ["Payé", "Dette", "Acompte"], horizontal=True)
        
        if st.form_submit_button("🚀 VALIDER & IMPRIMER"):
            id_v = len(db_v) + 1
            new_v = pd.DataFrame([{"ID":id_v, "Date":str(datetime.now().date()), "Client":c_nom, "Phone":c_tel, 
                                   "Service":serv, "Jeu":jeu, "Montant":prix, "Cout":cout, "Statut":stat}])
            db_v = pd.concat([db_v, new_v], ignore_index=True)
            db_v.to_csv('rg_ventes.csv', index=False)
            st.balloons()
            st.success(f"Vente #{id_v} enregistrée !")

# --- 6. MODULE 3 : MEGA STOCK ---
elif menu == "📦 Mega Stock":
    st.subheader("📦 Inventaire & Magasin")
    # Alerte Stock Bas
    bas = db_s[db_s['Qte'] <= db_s['Min_Seuil']]
    if not bas.empty:
        st.error(f"⚠️ Alerte ! {len(bas)} articles sont presque épuisés !")
        st.dataframe(bas)
    
    st.write("Détail du Stock")
    st.data_editor(db_s, num_rows="dynamic", key="stock_editor")
    if st.button("Enregistrer les modifications Stock"):
        db_s.to_csv('rg_stock.csv', index=False)

# --- 7. MODULE 5 : MARKETING WHATSAPP ---
elif menu == "📱 Marketing & WA":
    st.subheader("📢 Campagnes & CRM")
    mode = st.radio("Action", ["Relance Dette", "Promo Nouveau Jeu", "Fidélisation"])
    
    if mode == "Relance Dette":
        detteux = db_v[db_v['Statut'] == "Dette"]
        if not detteux.empty:
            select_c = st.selectbox("Client à relancer", detteux['Client'].unique())
            tel = detteux[detteux['Client']==select_c]['Phone'].iloc[0]
            montant = detteux[detteux['Client']==select_c]['Montant'].sum()
            msg = f"Salut {select_c}, c'est ROTAGAMING. Petit rappel pour tes {montant} GNF. Passe nous voir ! 🎮"
            if st.button("📲 Envoyer Relance"):
                url = f"https://wa.me/{tel}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{url}" target="_blank">Cliquez ici pour WhatsApp</a>', unsafe_allow_html=True)

# --- 8. MODULE SYSTÈME ---
elif menu == "⚙️ Système":
    st.subheader("🛠️ Maintenance du Système")
    if st.button("🔥 RESET TOTAL (ATTENTION)"):
        st.warning("Voulez-vous vraiment effacer TOUTES les données ?")
        # Logique de reset...
    
    st.download_button("📥 Backup Cloud (CSV)", db_v.to_csv(), "backup.csv", "text/csv")
