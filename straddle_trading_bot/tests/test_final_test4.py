#!/usr/bin/env python3
"""
Test de la logique test4 adaptée - Version finale
Vérifie que la configuration et la logique de test4 génèrent des signaux
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.config import *
from src.data_manager import DataManager
from src.straddle_strategy import StraddleStrategy

def main():
    print("🚀 TEST FINAL - LOGIQUE TEST4 ADAPTÉE")
    print("="*60)
    print(f"📊 Configuration: {CURRENT_PROFILE}")
    print(f"📈 Volatilité seuil: {VOLATILITY_THRESHOLD}")
    print(f"🎯 Qualité signal: {MIN_SIGNAL_QUALITY}")
    print(f"💰 Capital: ${INITIAL_CAPITAL:,}")
    
    try:
        print("\n1. Initialisation...")
        data_manager = DataManager()
        strategy = StraddleStrategy()
        print("✅ Modules initialisés")
        
        print("\n2. Chargement des données...")
        data = data_manager.get_backtest_data()
        print(f"✅ {len(data)} points chargés")
        print(f"📅 Période: {data.index[0]} → {data.index[-1]}")
        
        print("\n3. Test de détection de signaux...")
        signals_found = 0
        
        # Test sur une fenêtre réduite pour rapidité
        test_window = min(200, len(data))
        print(f"🔍 Test sur {test_window} derniers points...")
        
        for i in range(100, test_window):
            window_data = data.iloc[:i+1]
            should_enter, signal_info = strategy.calculate_signal_quality(window_data)
            
            if should_enter:
                signals_found += 1
                print(f"  🎯 Signal #{signals_found} détecté!")
                print(f"     Date: {window_data.index[-1]}")
                print(f"     Prix: ${window_data['close'].iloc[-1]:.2f}")
                print(f"     Qualité: {signal_info.get('signal_quality', 0):.2%}")
                print(f"     Confiance: {signal_info.get('confidence', 'LOW')}")
                
                if signals_found >= 5:  # Arrêter après 5 signaux
                    break
        
        print(f"\n📊 RÉSULTATS:")
        print(f"   Signaux trouvés: {signals_found}")
        frequency = (signals_found / (test_window - 100)) * 100
        print(f"   Fréquence: {frequency:.1f}% des points testés")
        
        if signals_found > 0:
            print("\n✅ SUCCÈS: Configuration test4 adaptée génère des signaux!")
            print("🚀 Prêt pour backtest complet")
        else:
            print("\n⚠️ Aucun signal détecté")
            print("💡 Suggestions:")
            print(f"   - Réduire VOLATILITY_THRESHOLD (actuel: {VOLATILITY_THRESHOLD})")
            print(f"   - Réduire MIN_SIGNAL_QUALITY (actuel: {MIN_SIGNAL_QUALITY})")
            
        # Test d'un backtest minimal si des signaux sont trouvés
        if signals_found > 0:
            print("\n4. Test de backtest minimal...")
            results = strategy.run_backtest(data)
            trades_count = len(results.get('trades', []))
            print(f"✅ Backtest exécuté: {trades_count} trades générés")
            
            if trades_count > 0:
                print("🎉 CONFIGURATION TEST4 PARFAITEMENT ADAPTÉE!")
            else:
                print("⚠️ Signaux détectés mais aucun trade exécuté")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
