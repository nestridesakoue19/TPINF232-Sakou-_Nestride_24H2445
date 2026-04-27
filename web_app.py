import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from data_collector import DataCollector, DataAnalyzer
import os

# Configuration de la page
st.set_page_config(
    page_title="E-Commerce Insights",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS pour un look premium
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialisation des classes
@st.cache_resource
def get_tools():
    collector = DataCollector()
    analyzer = DataAnalyzer()
    return collector, analyzer

collector, analyzer = get_tools()

# Sidebar
st.sidebar.title("🛍️ E-Commerce Analytics")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Navigation",
    ["Tableau de Bord", "Collecte de Données", "Analyses Graphiques", "Export & Rapport"]
)

# --- PAGE 1: TABLEAU DE BORD ---
if menu == "Tableau de Bord":
    st.title("📊 Tableau de Bord Stratégique")
    
    stats = analyzer.descriptive_statistics()
    
    if not stats:
        st.warning("⚠️ Aucune donnée disponible. Allez dans 'Collecte de Données' pour commencer.")
    else:
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Produits", stats['total_produits'])
        with col2:
            st.metric("Prix Moyen", f"{stats['prix_moyen']:.2f} €")
        with col3:
            st.metric("Note Moyenne", f"{stats['note_moyenne']:.1f}/5")
        with col4:
            st.metric("Total Avis", f"{stats['total_avis']:,}")

        st.markdown("---")
        
        # Tableaux et Top produits
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.subheader("📦 Liste des Produits Récents")
            st.dataframe(analyzer.df.sort_values('collected_at', ascending=False).head(10), use_container_width=True)
            
        with col_right:
            st.subheader("🏆 Top 3 par Note")
            for prod in stats['top_produits']:
                st.info(f"**{prod['name']}**  \n⭐ {prod['rating']} | 💰 {prod['price']}€")

# --- PAGE 2: COLLECTE DE DONNÉES ---
elif menu == "Collecte de Données":
    st.title("📥 Collecte de Données")
    st.write("Lancez une nouvelle session de collecte pour mettre à jour la base de données.")
    
    if st.button("🚀 Lancer la Collecte (Simulation)"):
        with st.spinner("Collecte en cours..."):
            products = collector.scrape_products()
            collector.save_to_database(products)
            # Forcer le rechargement des données
            analyzer._load_data()
            st.success(f"✅ {len(products)} produits collectés et sauvegardés !")
            st.balloons()

# --- PAGE 3: ANALYSES GRAPHIQUES ---
elif menu == "Analyses Graphiques":
    st.title("📈 Analyses Visuelles")
    
    if analyzer.df.empty:
        st.warning("Veuillez d'abord collecter des données.")
    else:
        tab1, tab2, tab3 = st.tabs(["Distribution des Prix", "Analyse des Notes", "Corrélations"])
        
        with tab1:
            st.subheader("💰 Analyse des Prix")
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.histplot(analyzer.df['price'], bins=15, kde=True, color='skyblue', ax=ax)
            ax.set_title("Distribution des Prix")
            st.pyplot(fig)
            
            # Prix par catégorie
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            analyzer.df.groupby('category')['price'].mean().sort_values().plot(kind='barh', color='lightgreen', ax=ax2)
            ax2.set_title("Prix Moyen par Catégorie")
            st.pyplot(fig2)

        with tab2:
            st.subheader("⭐ Analyse des Notes et Avis")
            fig3, ax3 = plt.subplots(figsize=(10, 6))
            sns.scatterplot(data=analyzer.df, x='price', y='rating', size='reviews_count', alpha=0.6, ax=ax3)
            ax3.set_title("Relation Prix vs Note (Taille = Nb Avis)")
            st.pyplot(fig3)

        with tab3:
            st.subheader("🔗 Matrice de Corrélation")
            numeric_cols = ['price', 'rating', 'reviews_count']
            corr = analyzer.df[numeric_cols].corr()
            fig4, ax4 = plt.subplots()
            sns.heatmap(corr, annot=True, cmap='RdYlGn', ax=ax4)
            st.pyplot(fig4)

# --- PAGE 4: EXPORT & RAPPORT ---
elif menu == "Export & Rapport":
    st.title("💾 Exportation des Données")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Rapport Textuel")
        if st.button("Générer le Rapport"):
            analyzer.generate_report("temp_report.txt")
            with open("temp_report.txt", "r") as f:
                report_content = f.read()
            st.text_area("Aperçu du rapport", report_content, height=300)
            st.download_button("Télécharger le Rapport", report_content, "rapport_ecommerce.txt")

    with col2:
        st.subheader("📊 Données CSV")
        if not analyzer.df.empty:
            csv = analyzer.df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Télécharger le CSV complet",
                data=csv,
                file_name='donnees_ecommerce.csv',
                mime='text/csv',
            )

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Application propulsée par Streamlit 🚀")
