import pandas as pd
import numpy as np
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class AnalysisResult:
    is_urgent: bool
    urgency_level: str  # "critical", "warning", "normal"
    urgency_reasons: List[str]
    summary: str
    anomalies_detected: List[Dict]
    recommendations: List[str]
    stats: Dict

class DataAnalyzer:
    def __init__(self):
        self.thresholds = {
            "critical_drop": 30,      # -30% = critique
            "warning_drop": 15,       # -15% = avertissement
            "anomaly_zscore": 3,      # Z-score > 3 = anomalie
            "missing_critical": 40,   # 40% manquant = critique
            "missing_warning": 20,    # 20% manquant = avertissement
        }
    
    def analyze(self, df: pd.DataFrame) -> AnalysisResult:
        urgency_reasons = []
        anomalies = []
        recommendations = []
        urgency_level = "normal"
        
        # Statistiques de base
        stats = {
            "rows": df.shape[0],
            "columns": df.shape[1],
            "missing_total": df.isnull().sum().sum(),
            "missing_percent": (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        }
        
        # 1. Vérification données manquantes
        missing_percent = stats["missing_percent"]
        if missing_percent > self.thresholds["missing_critical"]:
            urgency_reasons.append(f"🚨 {missing_percent:.1f}% de données manquantes (CRITIQUE)")
            urgency_level = "critical"
            recommendations.append("ARRÊT IMMÉDIAT - Vérifier la source de données")
        elif missing_percent > self.thresholds["missing_warning"]:
            urgency_reasons.append(f"⚠️ {missing_percent:.1f}% de données manquantes")
            if urgency_level == "normal":
                urgency_level = "warning"
            recommendations.append("Vérifier la qualité des données")
        
        # 2. Analyse colonnes numériques
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        stats["numeric_columns"] = list(numeric_cols)
        
        for col in numeric_cols:
            col_data = {
                "name": col,
                "mean": df[col].mean(),
                "std": df[col].std(),
                "min": df[col].min(),
                "max": df[col].max(),
                "missing": df[col].isnull().sum()
            }
            
            # Détection anomalies (Z-score)
            if col_data["std"] > 0:
                z_scores = np.abs((df[col] - col_data["mean"]) / col_data["std"])
                outliers = df[z_scores > self.thresholds["anomaly_zscore"]]
                
                if len(outliers) > 0:
                    anomalies.append({
                        "column": col,
                        "count": len(outliers),
                        "percentage": (len(outliers) / len(df)) * 100,
                        "max_zscore": z_scores.max()
                    })
                    urgency_reasons.append(f"📊 {len(outliers)} anomalies dans '{col}' (Z-score max: {z_scores.max():.2f})")
                    if urgency_level == "normal":
                        urgency_level = "warning"
                    recommendations.append(f"Revoir les valeurs extrêmes dans '{col}'")
            
            # Détection tendances (si index temporel ou numérique)
            if len(df) > 5:
                recent = df[col].iloc[-5:].mean()
                previous = df[col].iloc[-10:-5].mean() if len(df) >= 10 else df[col].iloc[:5].mean()
                
                if previous != 0:
                    change_pct = ((recent - previous) / abs(previous)) * 100
                    col_data["trend_change"] = change_pct
                    
                    if abs(change_pct) > self.thresholds["critical_drop"]:
                        direction = "📉 CHUTE" if change_pct < 0 else "📈 PIC"
                        urgency_reasons.append(f"🚨 {direction} de {abs(change_pct):.1f}% dans '{col}' (CRITIQUE)")
                        urgency_level = "critical"
                        recommendations.append(f"URGENCE: Investigation immédiate sur '{col}'")
                    elif abs(change_pct) > self.thresholds["warning_drop"]:
                        direction = "📉 Baisse" if change_pct < 0 else "📈 Hausse"
                        urgency_reasons.append(f"⚠️ {direction} de {abs(change_pct):.1f}% dans '{col}'")
                        if urgency_level == "normal":
                            urgency_level = "warning"
                        recommendations.append(f"Surveiller attentivement '{col}'")
        
        # 3. Génération résumé
        if urgency_level == "critical":
            summary = f"🚨 ALERTE CRITIQUE: {len(urgency_reasons)} problème(s) majeur(s) détecté(s)"
        elif urgency_level == "warning":
            summary = f"⚠️ AVERTISSEMENT: {len(urgency_reasons)} anomalie(s) détectée(s)"
        else:
            summary = "✅ DONNÉES NORMALES: Aucun problème significatif"
            recommendations.append("Continuer la surveillance standard")
        
        stats["analyzed_columns"] = len(numeric_cols)
        
        return AnalysisResult(
            is_urgent=urgency_level != "normal",
            urgency_level=urgency_level,
            urgency_reasons=urgency_reasons,
            summary=summary,
            anomalies_detected=anomalies,
            recommendations=recommendations,
            stats=stats
        )
