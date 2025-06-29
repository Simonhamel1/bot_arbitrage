# Test rapide avec configuration test4
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

print("🚀 TEST AVEC CONFIGURATION TEST4")
print("=" * 40)

try:
    from src.config import *
    from src.data_manager import DataManager
    from src.straddle_strategy import StraddleStrategy
    
    print(f"✅ Configuration chargée:")
    print(f"   📊 Timeframe: {TIMEFRAME}")
    print(f"   🎯 Volatility Threshold: {VOLATILITY_THRESHOLD}")
    print(f"   📅 Période backtest: {BACKTEST_START_DATE} → {BACKTEST_END_DATE}")
    print(f"   💰 Capital: ${INITIAL_CAPITAL:,}")
    print(f"   🎯 Risque par trade: {RISK_PER_TRADE:.1%}")
    print()
    
    print("📊 Récupération données...")
    data_manager = DataManager()
    backtest_data = data_manager.get_backtest_data()
    
    if backtest_data.empty:
        print("❌ Aucune donnée récupérée")
    else:
        print(f"✅ {len(backtest_data)} barres récupérées")
        
        # Statistiques de volatilité
        vol_stats = backtest_data['volatility'].describe()
        print(f"📈 Volatilité - Min: {vol_stats['min']:.2%}, Max: {vol_stats['max']:.2%}")
        
        # Test de la stratégie
        print("\n🎯 Test de la stratégie...")
        strategy = StraddleStrategy()
        
        # Test sur un échantillon pour voir s'il trouve des signaux
        sample_data = backtest_data.head(1000)  # Premier millier de barres
        
        signal_count = 0
        for i in range(100, len(sample_data)):
            current_data = sample_data.iloc[:i+1]
            should_enter, signal_info = strategy.calculate_signal_quality(current_data)
            if should_enter:
                signal_count += 1
        
        print(f"✅ Signaux trouvés: {signal_count}/{len(sample_data)-100} ({signal_count/(len(sample_data)-100)*100:.1f}%)")
        
        if signal_count > 0:
            print("🎉 Configuration optimisée ! Des signaux sont détectés.")
        else:
            print("⚠️ Aucun signal détecté avec cette configuration.")
            print("💡 Essayons d'assouplir encore...")
            
            # Test avec seuils assouplis
            original_threshold = VOLATILITY_THRESHOLD
            import src.config as config
            config.VOLATILITY_THRESHOLD = 45  # Plus permissif
            
            signal_count_relaxed = 0
            for i in range(100, len(sample_data)):
                current_data = sample_data.iloc[:i+1]
                should_enter, signal_info = strategy.calculate_signal_quality(current_data)
                if should_enter:
                    signal_count_relaxed += 1
            
            print(f"🔧 Avec seuil à 45%: {signal_count_relaxed} signaux")
            
            # Restaurer
            config.VOLATILITY_THRESHOLD = original_threshold

except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
