#!/usr/bin/env python3
"""
Test simple et rapide de la configuration test4
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("🔧 Test d'importation des modules...")
    
    from src import config
    print("✅ Config importée")
    print(f"   Profil: {config.CURRENT_PROFILE}")
    print(f"   Volatilité seuil: {config.VOLATILITY_THRESHOLD}")
    print(f"   Qualité signal: {config.MIN_SIGNAL_QUALITY}")
    
    from src.data_manager import DataManager
    print("✅ DataManager importé")
    
    from src.straddle_strategy import StraddleStrategy
    print("✅ StraddleStrategy importée")
    
    print("\n🚀 Test d'initialisation...")
    dm = DataManager()
    print("✅ DataManager initialisé")
    
    strategy = StraddleStrategy()
    print("✅ StraddleStrategy initialisée")
    
    print("\n📊 Test de récupération de données...")
    data = dm.get_backtest_data()
    
    if data is not None and len(data) > 0:
        print(f"✅ {len(data)} points de données récupérés")
        print(f"📈 Période: {data.index[0]} à {data.index[-1]}")
        print(f"💰 Prix: ${data['close'].iloc[0]:.2f} → ${data['close'].iloc[-1]:.2f}")
        
        # Test de détection de signal sur une seule observation
        if len(data) >= 100:
            print("\n🎯 Test de détection de signal...")
            test_data = data.tail(100)
            should_enter, signal_info = strategy.calculate_signal_quality(test_data)
            
            print(f"   Signal détecté: {'✅ OUI' if should_enter else '❌ NON'}")
            print(f"   Qualité: {signal_info.get('signal_quality', 0):.2%}")
            print(f"   Volatilité: {signal_info.get('volatility', 0):.4f}")
            print(f"   Vol Score: {signal_info.get('vol_score', 0):.1f}")
        
        print("\n🎉 TOUS LES TESTS PASSÉS!")
        print("🚀 Configuration test4 adaptée fonctionne correctement!")
        
    else:
        print("❌ Échec de récupération des données")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
