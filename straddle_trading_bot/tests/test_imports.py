#!/usr/bin/env python3
"""
Test minimal des imports et configuration
"""

print("🔧 Test des imports...")

try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    print("✅ Path configuré")
    
    from src import config
    print("✅ Config importée")
    print(f"   Symbol: {config.SYMBOL}")
    print(f"   Profil: {config.CURRENT_PROFILE}")
    print(f"   Volatilité seuil: {config.VOLATILITY_THRESHOLD}")
    
    from src.data_manager import DataManager
    print("✅ DataManager importé")
    
    from src.straddle_strategy import StraddleStrategy
    print("✅ StraddleStrategy importée")
    
    print("\n🎯 Test d'initialisation...")
    dm = DataManager()
    print("✅ DataManager créé")
    
    strategy = StraddleStrategy()
    print("✅ StraddleStrategy créée")
    
    print("\n🎉 TOUS LES TESTS PASSÉS!")
    print("La configuration test4 adaptée fonctionne")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
