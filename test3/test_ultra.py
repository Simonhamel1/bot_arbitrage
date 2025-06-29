# Test simple de la stratégie ultra-optimisée

print("🚀 Test stratégie ultra-straddle...")

try:
    # Test imports
    from config import *
    print("✅ Config importée")
    
    from data_manager import DataManager
    print("✅ DataManager importé")
    
    from ultra_straddle_strategy import UltraStraddleStrategy
    print("✅ UltraStraddleStrategy importée")
    
    # Test rapide
    print("\n📊 Configuration actuelle:")
    print(f"   Volatilité seuil: {VOLATILITY_THRESHOLD}%")
    print(f"   Take Profit: {TAKE_PROFIT_MULTIPLIER}x")
    print(f"   Stop Loss: {STOP_LOSS_MULTIPLIER}x")
    print(f"   Risque/trade: {RISK_PER_TRADE:.1%}")
    print(f"   Hedging: {MOMENTUM_HEDGE}")
    
    print("\n✅ Tous les modules fonctionnent!")
    print("💡 Utilisez 'python ultra_main.py' pour lancer l'analyse complète")
    
except ImportError as e:
    print(f"❌ Erreur import: {e}")
except Exception as e:
    print(f"❌ Erreur: {e}")
