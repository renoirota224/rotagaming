import streamlit as st
import pandas as pd
from datetime import datetime
import io
import urllib.parse
import plotly.express as px

# 1. CONFIGURATION ÉLÉGANTE
st.set_page_config(page_title="ROTAGAMING ULTIMATE", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.9), rgba(0, 0, 0, 0.8)), 
        url("https://images.unsplash.com/photo-1511512578047-dfb367046420?q=80&w=2070");
        background-size: cover;
    }
    .metric-card { background: rgba(255, 255, 255, 0.05); border-radius: 10px; padding: 15px; border-left: 5px solid #00ff00; }
    div[data-testid="stMetricValue"] { color: #00ff00; font-family: 'Courier New'; }
    .stButton>button { border-radius: 20px; background: #00ff00; color: black; transition: 0.3s; font-weight: bold; }
    .stButton>button:hover { background: #00cc00; transform: scale(1.05); }
    </style>
    """, unsafe_allow_html=True)

# 2. FONCTIONS DE GESTION DE DONNÉES
def init_data(file, cols):
    try:
        df = pd.read_csv(file)
        for c in cols: 
            if c not in df.columns: df[c] = 0
        return df
    except: return pd.DataFrame(columns=cols)

df_ventes = init_data('ventes_pro.csv', ["Date", "Client", "Service", "Jeu", "Montant", "Statut", "Phone"])
df_stock = init_data('stock_pro.csv', ["Article", "Quantite", "Prix_Achat", "Seuil"])
df_depenses = init_data('depenses_pro.csv', ["Date", "Categorie", "Note", "Montant"])

# 3. SIDEBAR NAVIGATION
st.sidebar.title("🎮 ROTAGAMING HUB")
page = st.sidebar.radio("Navigation", ["📊 Dashboard", "💰 Caisse", "📦 Stock & Magasin", "🕵️ Clients & Dettes", "📱 WhatsApp Marketing", "⚙️ Paramètres"])

# --- PAGE 1: DASHBOARD ---
if page == "📊 Dashboard":
    st.header("Statistiques Globales")
    
    # Calculs rapides
    df_ventes['Montant'] = pd.to_numeric(df_ventes['Montant'], errors='coerce').fillna(0)
    rev_total = df_ventes[df_ventes['Statut'] == "Payé"]['Montant'].sum()
    dette_total = df_ventes[df_ventes['Statut'] == "Dette"]['Montant'].sum()
    dep_total = pd.to_numeric(df_depenses['Montant']).sum()
    benef = rev_total - dep_total

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("REVENU RÉEL", f"{rev_total:,.0f} GNF")
    with c2: st.metric("EN ATTENTE (DETTES)", f"{dette_total:,.0f} GNF", delta_color="inverse")
    with c3: st.metric("CHARGES", f"{dep_total:,.0f} GNF", delta_color="inverse")
    with c4: st.metric("NET DANS LA POCHE", f"{benef:,.0f} GNF")

    # Graphique de Performance
    if not df_ventes.empty:
        fig = px.line(df_ventes, x='Date', y='Montant', title="Évolution des Ventes", color_discrete_sequence=['#00ff00'])
        st.plotly_chart(fig, use_container_width=True)

# --- PAGE 2: CAISSE ---
elif page == "💰 Caisse":
    tab1, tab2 = st.tabs(["🛒 Nouvelle Vente", "💸 Sortie d'argent"])
    
    with tab1:
        with st.form("vente"):
            c1, c2 = st.columns(2)
            date = c1.date_input("Date", datetime.now())
            client = c1.text_input("Nom Client")
            phone = c1.text_input("Numéro Client (WhatsApp)")
            serv = c2.selectbox("Prestation", ["PES 26 Installation", "Patch Update", "Full Pack PC", "Réparation Manette"])
            jeu = c2.text_input("Nom du Jeu / Objet")
            prix = c2.number_input("Prix (GNF)", step=5000)
            statut = c2.radio("Statut", ["Payé", "Dette"])
            if st.form_submit_button("Enregistrer la Transaction"):
                new_v = pd.DataFrame([{"Date":str(date), "Client":client, "Service":serv, "Jeu":jeu, "Montant":prix, "Statut":statut, "Phone":phone}])
                df_ventes = pd.concat([df_ventes, new_v], ignore_index=True)
                df_ventes.to_csv('ventes_pro.csv', index=False)
                st.success("Transaction validée !")

    with tab2:
        with st.form("depense"):
            d_date = st.date_input("Date", datetime.now())
            cat = st.selectbox("Catégorie", ["Loyer", "EDG", "Internet", "Achat Stock", "Transport"])
            note = st.text_input("Détails")
            montant = st.number_input("Montant (GNF)", step=1000)
            if st.form_submit_button("Valider la Dépense"):
                new_d = pd.DataFrame([{"Date":str(d_date), "Categorie":cat, "Note":note, "Montant":montant}])
                df_depenses = pd.concat([df_depenses, new_d], ignore_index=True)
                df_depenses.to_csv('depenses_pro.csv', index=False)
                st.warning("Dépense enregistrée.")

# --- PAGE 3: STOCK ---
elif page == "📦 Stock & Magasin":
    st.subheader("Gestion des Articles")
    with st.expander("➕ Ajouter un article en stock"):
        with st.form("stock"):
            art = st.text_input("Nom de l'article (ex: Manette PS4)")
            qte = st.number_input("Quantité", min_value=1)
            p_a = st.number_input("Prix d'achat Unitaire", min_value=0)
            seuil = st.number_input("Alerte Stock Bas (Seuil)", min_value=1)
            if st.form_submit_button("Ajouter au Magasin"):
                new_s = pd.DataFrame([{"Article":art, "Quantite":qte, "Prix_Achat":p_a, "Seuil":seuil}])
                df_stock = pd.concat([df_stock, new_s], ignore_index=True)
                df_stock.to_csv('stock_pro.csv', index=False)
    
    st.table(df_stock)

# --- PAGE 5: WHATSAPP ---
elif page == "📱 WhatsApp Marketing":
    st.subheader("Relance & Prospect")
    target = st.selectbox("Client à contacter", df_ventes['Client'].unique())
    client_info = df_ventes[df_ventes['Client'] == target].iloc[-1]
    
    msg = st.text_area("Message", f"Salut {target}, c'est ROTAGAMING ! Ton jeu est prêt. Passe au labo ! 🎮")
    
    if st.button("Envoyer via WhatsApp"):
        phone = str(client_info['Phone'])
        url = f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"
        st.markdown(f"[CLIQUEZ ICI POUR ENVOYER LE MESSAGE]( {url} )")
