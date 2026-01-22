mport streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

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

st.title("🎮 ROTAGAMING : Expert Installation Jeux")

# Chargement sécurisé des données
def load_data():
    try:
        df = pd.read_csv('database_gaming.csv')
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Prestation", "Jeu", "Client", "Revenu", "Depense", "Profit"])

df = load_data()

# --- ESPACE SAISIE (LATÉRAL) ---
with st.sidebar:
    st.header("🛒 Enregistrer une Vente")
    date_v = st.date_input("Date", datetime.now())
    presta = st.selectbox("Type de Service", 
                          ["Installation Jeu Solo", "Installation Jeu Online", "Pack Complet (Setup)", "Mise à jour / Patch", "Vente Accessoire"])
    jeu = st.text_input("Nom du Jeu / Article")
    client = st.text_input("Nom du Client")
    
    col_a, col_b = st.columns(2)
    with col_a:
        rev = st.number_input("Prix (GNF)", min_value=0, step=5000)
    with col_b:
        dep = st.number_input("Coût (GNF)", min_value=0, step=1000) # Ex: Achat de clé, électricité, disque
    
    if st.button("Valider la Transaction"):
        new_entry = {
            "Date": date_v, "Prestation": presta, "Jeu": jeu, 
            "Client": client, "Revenu": rev, "Depense": dep, "Profit": rev - dep
        }
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv('database_gaming.csv', index=False)
        st.success("Enregistré avec succès !")
        st.rerun()

# --- TABLEAU DE BORD FINANCIER ---
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("CHIFFRE D'AFFAIRES", f"{df['Revenu'].sum():,.0f} GNF".replace(",", " "))
with c2:
    st.metric("DÉPENSES (COÛTS)", f"{df['Depense'].sum():,.0f} GNF".replace(",", " "), delta_color="inverse")
with c3:
    total_profit = df['Profit'].sum()
    st.metric("BÉNÉFICE NET", f"{total_profit:,.0f} GNF".replace(",", " "))

st.markdown("---")

# --- ANALYSE ET GRAPHIQUES ---
left, right = st.columns(2)

with left:
    st.subheader("📦 Revenus par Prestation")
    if not df.empty:
        fig_pie = px.sunburst(df, path=['Prestation', 'Jeu'], values='Revenu', color='Profit',
                              color_continuous_scale='RdYlGn')
        st.plotly_chart(fig_pie, use_container_width=True)

with right:
    st.subheader("📈 Évolution des Profits")
    if not df.empty:
        df_daily = df.groupby('Date')['Profit'].sum().reset_index()
        fig_line = px.line(df_daily, x='Date', y='Profit', markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

# --- JOURNAL PRO ---
st.subheader("📝 Historique Professionnel")
st.dataframe(df.sort_values(by="Date", ascending=False), use_container_width=True)
