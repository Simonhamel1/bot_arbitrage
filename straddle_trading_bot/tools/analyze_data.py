# Analyse des données pour comprendre pourquoi aucun trade
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import pandas as pd
import numpy as np

print("🔍 ANALYSE DES DONNÉES - Pourquoi aucun trade ?")
print("=" * 60)

try:
    from src.data_manager import DataManager
    from src.config import *
    
    print("📊 Chargement des données...")
    data_manager = DataManager()
    data = data_manager.get_backtest_data()
    
    print(f"✅ {len(data)} barres chargées")
    print(f"📅 Période: {data.index[0]} → {data.index[-1]}")
    print()
    
    # Analyse de la volatilité
    print("📈 ANALYSE DE LA VOLATILITÉ")
    print("-" * 30)
    vol_stats = data['volatility'].describe()
    print(f"Min: {vol_stats['min']:.2%}")
    print(f"25%: {vol_stats['25%']:.2%}")
    print(f"50%: {vol_stats['50%']:.2%}")
    print(f"75%: {vol_stats['75%']:.2%}")
    print(f"Max: {vol_stats['max']:.2%}")
    print()
    
    # Calcul des percentiles de volatilité
    print("🎯 SEUILS DE VOLATILITÉ")
    print("-" * 25)
    percentiles = [20, 30, 40, 50, 60, 70, 80, 90]
    for p in percentiles:
        threshold = np.percentile(data['volatility'], p)
        count = (data['volatility'] >= threshold).sum()
        pct = count / len(data) * 100
        print(f"Percentile {p:2d}%: {threshold:.2%} → {count:4d} barres ({pct:4.1f}%)")
    
    print()
    
    # Analyse du signal quality
    if 'signal_quality' in data.columns:
        print("🎯 ANALYSE DE LA QUALITÉ DES SIGNAUX")
        print("-" * 35)
        sq_stats = data['signal_quality'].describe()
        print(f"Min: {sq_stats['min']:.3f}")
        print(f"Moyenne: {sq_stats['mean']:.3f}")
        print(f"Max: {sq_stats['max']:.3f}")
        
        high_quality = (data['signal_quality'] >= MIN_SIGNAL_QUALITY).sum()
        print(f"Signaux ≥ {MIN_SIGNAL_QUALITY}: {high_quality}/{len(data)} ({high_quality/len(data)*100:.1f}%)")
        print()
    
    # Analyse combinée
    print("🔥 ANALYSE COMBINÉE - Opportunités de trading")
    print("-" * 45)
    
    vol_threshold_value = np.percentile(data['volatility'], VOLATILITY_THRESHOLD)
    
    # Conditions d'entrée
    high_volatility = data['volatility'] >= vol_threshold_value
    if 'signal_quality' in data.columns:
        good_signals = data['signal_quality'] >= MIN_SIGNAL_QUALITY
        opportunities = high_volatility & good_signals
    else:
        opportunities = high_volatility
    
    print(f"Seuil volatilité {VOLATILITY_THRESHOLD}%: {vol_threshold_value:.2%}")
    print(f"Périodes volatiles: {high_volatility.sum()}/{len(data)} ({high_volatility.sum()/len(data)*100:.1f}%)")
    
    if 'signal_quality' in data.columns:
        print(f"Bons signaux: {good_signals.sum()}/{len(data)} ({good_signals.sum()/len(data)*100:.1f}%)")
        print(f"OPPORTUNITÉS TOTALES: {opportunities.sum()}/{len(data)} ({opportunities.sum()/len(data)*100:.1f}%)")
    else:
        print(f"OPPORTUNITÉS TOTALES: {opportunities.sum()}/{len(data)} ({opportunities.sum()/len(data)*100:.1f}%)")
    
    print()
    
    # Recommandations
    print("💡 RECOMMANDATIONS")
    print("-" * 20)
    
    if opportunities.sum() == 0:
        print("❌ AUCUNE opportunité détectée avec les paramètres actuels")
        print()
        print("🔧 Solutions suggérées:")
        new_vol_threshold = 30
        new_vol_value = np.percentile(data['volatility'], new_vol_threshold)
        new_opportunities = data['volatility'] >= new_vol_value
        print(f"   • Réduire VOLATILITY_THRESHOLD à {new_vol_threshold}% → {new_opportunities.sum()} opportunités")
        
        if 'signal_quality' in data.columns:
            new_signal_quality = 0.60
            new_good_signals = data['signal_quality'] >= new_signal_quality
            combined_new = new_opportunities & new_good_signals
            print(f"   • Réduire MIN_SIGNAL_QUALITY à {new_signal_quality} → {combined_new.sum()} opportunités")
    
    elif opportunities.sum() < 10:
        print(f"⚠️ Très peu d'opportunités ({opportunities.sum()})")
        print("🔧 Considérer d'assouplir les paramètres pour plus d'activité")
    
    else:
        print(f"✅ {opportunities.sum()} opportunités détectées - Configuration correcte")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
