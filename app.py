import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from analyzer import DataAnalyzer, AnalysisResult

# Configuration
st.set_page_config(
    page_title="🤖 Agent d'Analyse de Données", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour l'apparence
st.markdown("""
<style>
    .urgent-box {
        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #feca57, #ff9f43);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .normal-box {
        background: linear-gradient(135deg, #1dd1a1, #10ac84);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #007bff;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("🤖 Agent Intelligent d'Analyse de Données")
st.markdown("*Analyse automatique avec détection d'anomalies et alertes visuelles*")
st.markdown("---")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration des Seuils")
    
    st.subheader("🚨 Seuils d'Alerte")
    critical_drop = st.slider("Chute Critique (%)", 10, 50, 30)
    warning_drop = st.slider("Chute Avertissement (%)", 5, 30, 15)
    anomaly_zscore = st.slider("Seuil Anomalie (Z-score)", 2.0, 5.0, 3.0)
    
    st.subheader("📊 Seuils Données")
    missing_critical = st.slider("% Manquant Critique", 20, 60, 40)
    missing_warning = st.slider("% Manquant Avertissement", 10, 40, 20)
    
    st.markdown("---")
    st.info("💡 **Conseil**: Ajustez les seuils selon votre domaine métier")

# Zone principale - Upload
st.header("📁 Charger vos Données")

col1, col2 = st.columns([2, 1])

with col1:
    uploaded_file = st.file_uploader(
        "Glissez-déposez votre fichier CSV ou Excel",
        type=['csv', 'xlsx', 'xls'],
        help="Formats supportés: CSV, Excel (.xlsx, .xls)"
    )

with col2:
    st.markdown("### ℹ️ Info")
    st.info("L'agent analysera automatiquement vos données et affichera les alertes visuelles ici.")

# Traitement des données
if uploaded_file:
    # Lecture
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Initialisation analyseur avec seuils personnalisés
        analyzer = DataAnalyzer()
        analyzer.thresholds.update({
            "critical_drop": critical_drop,
            "warning_drop": warning_drop,
            "anomaly_zscore": anomaly_zscore,
            "missing_critical": missing_critical,
            "missing_warning": missing_warning
        })
        
        # Analyse
        result = analyzer.analyze(df)
        
        # ==================== RÉSULTATS ====================
        
        st.markdown("---")
        
        # Bannière de statut
        if result.urgency_level == "critical":
            st.markdown(f"""
            <div class="urgent-box">
                <h2>🚨 ALERTE CRITIQUE</h2>
                <p>{result.summary}</p>
            </div>
            """, unsafe_allow_html=True)
        elif result.urgency_level == "warning":
            st.markdown(f"""
            <div class="warning-box">
                <h2>⚠️ AVERTISSEMENT</h2>
                <p>{result.summary}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="normal-box">
                <h2>✅ DONNÉES NORMALES</h2>
                <p>{result.summary}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Métriques clés
        st.subheader("📊 Vue d'Ensemble")
        col_met1, col_met2, col_met3, col_met4 = st.columns(4)
        
        with col_met1:
            st.metric("Lignes", result.stats["rows"])
        with col_met2:
            st.metric("Colonnes", result.stats["columns"])
        with col_met3:
            st.metric("Valeurs Manquantes", f"{result.stats['missing_percent']:.1f}%")
        with col_met4:
            st.metric("Anomalies", len(result.anomalies_detected))
        
        # Détail des problèmes
        if result.is_urgent:
            st.markdown("---")
            st.subheader("🚨 Problèmes Détectés")
            
            for i, reason in enumerate(result.urgency_reasons, 1):
                if "CRITIQUE" in reason:
                    st.error(f"{i}. {reason}")
                else:
                    st.warning(f"{i}. {reason}")
        
        # Recommandations
        st.markdown("---")
        st.subheader("💡 Recommandations")
        
        for rec in result.recommendations:
            if "URGENCE" in rec or "ARRÊT" in rec:
                st.error(f"🔴 {rec}")
            elif "surveiller" in rec.lower() or "Revoir" in rec:
                st.warning(f"🟡 {rec}")
            else:
                st.success(f"🟢 {rec}")
        
        # Visualisations
        st.markdown("---")
        st.subheader("📈 Visualisations")
        
        # Onglets pour organiser l'affichage
        tab1, tab2, tab3 = st.tabs(["📋 Données", "📊 Statistiques", "🔍 Anomalies"])
        
        with tab1:
            st.dataframe(df, use_container_width=True, height=400)
            
            # Info sur les colonnes
            st.markdown("### ℹ️ Information des Colonnes")
            col_info = pd.DataFrame({
                'Colonne': df.columns,
                'Type': df.dtypes.values,
                'Non-Nuls': df.count().values,
                'Nuls': df.isnull().sum().values,
                'Unique': df.nunique().values
            })
            st.dataframe(col_info, use_container_width=True)
        
        with tab2:
            # Statistiques descriptives
            numeric_df = df.select_dtypes(include=[np.number])
            
            if not numeric_df.empty:
                st.markdown("### 📊 Statistiques Descriptives")
                st.dataframe(numeric_df.describe(), use_container_width=True)
                
                # Graphiques de distribution
                st.markdown("### 📈 Distributions")
                selected_col = st.selectbox("Choisir une colonne à visualiser", numeric_df.columns)
                
                col_chart1, col_chart2 = st.columns(2)
                
                with col_chart1:
                    # Histogramme
                    fig = px.histogram(df, x=selected_col, title=f"Distribution de {selected_col}")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_chart2:
                    # Box plot pour voir les outliers
                    fig = px.box(df, y=selected_col, title=f"Box Plot de {selected_col}")
                    st.plotly_chart(fig, use_container_width=True)
                
                # Graphique de tendance temporelle (si index numérique)
                st.markdown("### 📉 Tendance")
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=df[selected_col].values,
                    mode='lines',
                    name=selected_col,
                    line=dict(color='blue', width=2)
                ))
                
                # Marquer les anomalies
                if result.anomalies_detected:
                    for anom in result.anomalies_detected:
                        if anom["column"] == selected_col:
                            # Trouver indices des anomalies
                            z_scores = abs((df[selected_col] - df[selected_col].mean()) / df[selected_col].std())
                            anomaly_indices = df[z_scores > 3].index
                            fig.add_trace(go.Scatter(
                                x=anomaly_indices,
                                y=df.loc[anomaly_indices, selected_col],
                                mode='markers',
                                name='Anomalies',
                                marker=dict(color='red', size=10, symbol='x')
                            ))
                
                fig.update_layout(title=f"Tendance de {selected_col} avec Anomalies")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Aucune colonne numérique trouvée pour les statistiques.")
        
        with tab3:
            if result.anomalies_detected:
                st.markdown("### 🔍 Détail des Anomalies")
                
                for anom in result.anomalies_detected:
                    with st.expander(f"📊 {anom['column']} - {anom['count']} anomalies ({anom['percentage']:.1f}%)"):
                        st.write(f"**Colonne:** {anom['column']}")
                        st.write(f"**Nombre d'anomalies:** {anom['count']}")
                        st.write(f"**Pourcentage:** {anom['percentage']:.2f}%")
                        st.write(f"**Z-score maximum:** {anom['max_zscore']:.2f}")
                        
                        # Afficher les valeurs anormales
                        z_scores = abs((df[anom['column']] - df[anom['column']].mean()) / df[anom['column']].std())
                        abnormal_values = df[z_scores > 3][anom['column']].tolist()
                        st.write(f"**Valeurs anormales:** {abnormal_values[:10]}...")  # Limiter l'affichage
            else:
                st.success("✅ Aucune anomalie statistique détectée")
        
        # Export des résultats
        st.markdown("---")
        st.subheader("💾 Export des Résultats")
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            # Export rapport texte
            report = f"""
RAPPORT D'ANALYSE - AGENT INTELLIGENT
=====================================
Date: {pd.Timestamp.now()}
Fichier: {uploaded_file.name}

STATUT: {result.urgency_level.upper()}
{result.summary}

PROBLÈMES DÉTECTÉS:
{chr(10).join(result.urgency_reasons) if result.urgency_reasons else "Aucun"}

RECOMMANDATIONS:
{chr(10).join(result.recommendations)}

STATISTIQUES:
- Lignes: {result.stats['rows']}
- Colonnes: {result.stats['columns']}
- Données manquantes: {result.stats['missing_percent']:.2f}%
- Anomalies: {len(result.anomalies_detected)}
            """
            
            st.download_button(
                label="📄 Télécharger le Rapport (TXT)",
                data=report,
                file_name=f"rapport_analyse_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            )
        
        with col_exp2:
            # Export données avec flag d'anomalie
            df_export = df.copy()
            for anom in result.anomalies_detected:
                col = anom['column']
                z_scores = abs((df[col] - df[col].mean()) / df[col].std())
                df_export[f"{col}_anomaly"] = z_scores > 3
            
            csv = df_export.to_csv(index=False)
            st.download_button(
                label="📊 Télécharger Données avec Flags (CSV)",
                data=csv,
                file_name=f"donnees_analysees_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        
    except Exception as e:
        st.error(f"❌ Erreur lors de l'analyse: {str(e)}")
        st.exception(e)

else:
    # Page d'accueil quand pas de fichier
    st.markdown("""
    ### 👋 Bienvenue dans l'Agent d'Analyse de Données
    
    **Comment utiliser cet outil:**
    
    1. **Chargez vos données** (CSV ou Excel) dans la zone ci-dessus
    2. **Ajustez les seuils** dans la barre latérale selon vos besoins
    3. **L'agent analyse automatiquement** et affiche:
       - 🚨 Alertes visuelles (rouge/jaune/vert)
       - 📊 Statistiques détaillées
       - 📈 Graphiques interactifs
       - 💡 Recommandations intelligentes
    
    **Types d'anomalies détectées:**
    - Chutes brutales de valeurs (>30%)
    - Valeurs statistiquement anormales (Z-score > 3)
    - Problèmes de qualité de données (valeurs manquantes)
    - Tendances suspectes dans les séries temporelles
    """)
    
    # Exemple visuel
    st.markdown("---")
    st.subheader("🖼️ Aperçu du Résultat")
    
    col_ex1, col_ex2, col_ex3 = st.columns(3)
    
    with col_ex1:
        st.markdown("""
        <div style="background: #ff6b6b; color: white; padding: 20px; border-radius: 10px; text-align: center;">
            <h3>🚨 CRITIQUE</h3>
            <p>Action immédiate requise</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_ex2:
        st.markdown("""
        <div style="background: #feca57; color: white; padding: 20px; border-radius: 10px; text-align: center;">
            <h3>⚠️ AVERTISSEMENT</h3>
            <p>Surveillance renforcée</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col_ex3:
        st.markdown("""
        <div style="background: #1dd1a1; color: white; padding: 20px; border-radius: 10px; text-align: center;">
            <h3>✅ NORMAL</h3>
            <p>Tous indicateurs bons</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("*Agent d'Analyse de Données v1.0 - Interface Web*")
