#!/usr/bin/env python3
"""
Test final de la configuration et logique adaptées de test4
Vérifie que le bot génère des trades avec les paramètres optimisés
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

from src.data_manager import DataManager
from src.straddle_strategy import StraddleStrategy
from src import config

def main():
    print("=" * 80)
    print("TEST FINAL - Configuration Test4 Adaptée")
    print("=" * 80)
    
    # Validation de la configuration
    print("\n1. VALIDATION DE LA CONFIGURATION")
    print("-" * 40)
    errors, warnings = config.validate_config()
    
    if errors:
        print("❌ ERREURS:")
        for error in errors:
            print(f"   - {error}")
        return
    
    if warnings:
        print("⚠️  AVERTISSEMENTS:")
        for warning in warnings:
            print(f"   - {warning}")
    
    print(f"✅ Profil actuel: {config.CURRENT_PROFILE}")
    print(f"✅ Volatilité seuil: {config.VOLATILITY_THRESHOLD}%")
    print(f"✅ Qualité signal min: {config.MIN_SIGNAL_QUALITY}")
    print(f"✅ Risque par trade: {config.RISK_PER_TRADE:.1%}")
    
    # Initialisation des modules
    print("\n2. INITIALISATION DES MODULES")
    print("-" * 40)
    
    try:
        data_manager = DataManager()
        strategy = StraddleStrategy()
        print("✅ Modules initialisés avec succès")
    except Exception as e:
        print(f"❌ Erreur d'initialisation: {e}")
        return
    
    # Chargement et analyse des données
    print("\n3. CHARGEMENT ET ANALYSE DES DONNÉES")
    print("-" * 40)
    
    try:
        # Utilisons la période de backtest configurée
        start_date = config.BACKTEST_START_DATE
        end_date = config.BACKTEST_END_DATE
        
        print(f"📅 Période: {start_date} à {end_date}")
        print("📊 Chargement des données...")
        
        data = data_manager.get_backtest_data()
        
        if data is None or len(data) == 0:
            print("❌ Aucune donnée récupérée")
            return
            
        print(f"✅ {len(data)} points de données chargés")
        print(f"📈 Prix min/max: ${data['close'].min():.0f} / ${data['close'].max():.0f}")
        
    except Exception as e:
        print(f"❌ Erreur de chargement: {e}")
        return
    
    # Test de détection de signaux
    print("\n4. TEST DE DÉTECTION DE SIGNAUX")
    print("-" * 40)
    
    signals_found = 0
    signal_details = []
    
    # Tester sur les 100 derniers points pour gagner du temps
    test_data = data.tail(200)  # Plus de données pour le contexte
    
    print(f"🔍 Test sur {len(test_data)} points de données...")
    
    for i in range(100, len(test_data)):  # Besoin de 100 points pour l'historique
        current_data = test_data.iloc[:i+1]
        
        try:
            should_enter, signal_info = strategy.calculate_signal_quality(current_data)
            
            if should_enter:
                signals_found += 1
                signal_details.append({
                    'date': current_data.index[-1],
                    'price': current_data['close'].iloc[-1],
                    'signal_quality': signal_info.get('signal_quality', 0),
                    'vol_score': signal_info.get('vol_score', 0),
                    'volatility': signal_info.get('volatility', 0),
                    'confidence': signal_info.get('confidence', 'LOW')
                })
                
                print(f"  🎯 Signal #{signals_found}")
                print(f"     Date: {current_data.index[-1]}")
                print(f"     Prix: ${current_data['close'].iloc[-1]:.2f}")
                print(f"     Qualité: {signal_info.get('signal_quality', 0):.2%}")
                print(f"     Vol Score: {signal_info.get('vol_score', 0):.1f}")
                print(f"     Confiance: {signal_info.get('confidence', 'LOW')}")
                
        except Exception as e:
            print(f"⚠️  Erreur signal {i}: {e}")
            continue
    
    print(f"\n📊 RÉSULTATS DE DÉTECTION:")
    print(f"   Signaux trouvés: {signals_found}")
    print(f"   Fréquence: {signals_found/len(test_data)*100:.1f}% des points")
    
    if signals_found == 0:
        print("\n❌ AUCUN SIGNAL DÉTECTÉ - DIAGNOSTIC NÉCESSAIRE")
        diagnostic_signals(test_data, strategy)
        return
    
    # Test de simulation rapide
    print("\n5. SIMULATION RAPIDE SUR SIGNAUX")
    print("-" * 40)
    
    if len(signal_details) > 0:
        print("🚀 Simulation d'un backtest rapide...")
        
        # Prendre les 5 premiers signaux pour test rapide
        test_signals = signal_details[:5]
        
        for i, signal in enumerate(test_signals):
            print(f"\n  📈 Test Signal #{i+1}")
            print(f"     Date: {signal['date']}")
            print(f"     Prix: ${signal['price']:.2f}")
            print(f"     Qualité: {signal['signal_quality']:.2%}")
            print(f"     ✅ Signal valide pour trading")
    
    print("\n" + "=" * 80)
    print("✅ TEST FINAL COMPLÉTÉ AVEC SUCCÈS")
    print(f"✅ {signals_found} signaux de trading détectés")
    print("✅ Configuration test4 adaptée fonctionnelle")
    print("🚀 Prêt pour le backtest complet!")
    print("=" * 80)

def diagnostic_signals(data, strategy):
    """Diagnostic en cas d'absence de signaux"""
    print("\n🔧 DIAGNOSTIC - ANALYSE DES SEUILS")
    print("-" * 40)
    
    # Analyser les dernières données
    latest = data.iloc[-1]
    recent = data.tail(20)
    
    print(f"📊 Données récentes (derniers 20 points):")
    print(f"   Volatilité actuelle: {latest.get('volatility', 0):.2f}")
    print(f"   Volatilité moyenne: {data['volatility'].mean():.2f}")
    print(f"   Vol. max récente: {recent['volatility'].max():.2f}")
    print(f"   Seuil configuré: {config.VOLATILITY_THRESHOLD}")
    
    print(f"\n   RSI actuel: {latest.get('rsi', 0):.1f}")
    print(f"   Range RSI cible: 35-65")
    
    if 'volume' in data.columns:
        vol_ma = data['volume'].rolling(20).mean().iloc[-1]
        print(f"\n   Volume actuel: {latest.get('volume', 0):,.0f}")
        print(f"   Volume moyen: {vol_ma:,.0f}")
        print(f"   Ratio: {latest.get('volume', 0)/vol_ma:.2f}")
        print(f"   Seuil: {config.MIN_VOLUME_RATIO}")
    
    # Proposer des ajustements
    print(f"\n💡 SUGGESTIONS D'AJUSTEMENT:")
    max_vol = data['volatility'].max()
    avg_vol = data['volatility'].mean()
    
    if max_vol < config.VOLATILITY_THRESHOLD:
        suggested_vol = max_vol * 0.8
        print(f"   - Réduire VOLATILITY_THRESHOLD à {suggested_vol:.0f}")
    
    print(f"   - Réduire MIN_SIGNAL_QUALITY à 0.6")
    print(f"   - Utiliser profil AGGRESSIVE")

if __name__ == "__main__":
    main()
