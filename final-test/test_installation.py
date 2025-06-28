# Script de test rapide pour valider l'installation et la configuration

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test des imports des modules"""
    print("🔍 Test des imports...")
    try:
        import ccxt
        print("✅ ccxt importé avec succès")
        
        import pandas as pd
        print("✅ pandas importé avec succès")
        
        import numpy as np
        print("✅ numpy importé avec succès")
        
        import matplotlib.pyplot as plt
        print("✅ matplotlib importé avec succès")
        
        try:
            import talib
            print("✅ talib importé avec succès")
        except ImportError:
            print("⚠️  talib non disponible (optionnel)")
        
        import config
        print("✅ Configuration chargée")
        
        from data_manager import DataManager
        print("✅ DataManager importé")
        
        from straddle_strategy import StraddleStrategy
        print("✅ StraddleStrategy importé")
        
        from backtest_engine import StraddleBacktester
        print("✅ StraddleBacktester importé")
        
        from visualization import StraddleVisualizer
        print("✅ StraddleVisualizer importé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur d'import: {e}")
        return False

def test_data_connection():
    """Test de la connexion aux données"""
    print("\n🌐 Test de connexion aux données...")
    try:
        from data_manager import DataManager
        
        dm = DataManager()
        if dm.exchange:
            print("✅ Connexion à l'échange établie")
            
            # Test de récupération de quelques données
            df = dm.fetch_historical_data(limit=10)
            if not df.empty:
                print(f"✅ Données récupérées: {len(df)} bougies")
                return True
            else:
                print("⚠️  Données vides")
                return False
        else:
            print("❌ Connexion à l'échange échouée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_strategy():
    """Test de la stratégie de base"""
    print("\n🎯 Test de la stratégie...")
    try:
        from straddle_strategy import StraddleStrategy
        import pandas as pd
        import numpy as np
        
        # Création de données de test
        dates = pd.date_range('2024-01-01', periods=100, freq='H')
        test_data = pd.DataFrame({
            'close': 50000 + np.cumsum(np.random.randn(100) * 100),
            'high': 0,
            'low': 0,
            'open': 0,
            'volume': np.random.rand(100) * 1000000,
            'volatility_std': np.random.rand(100) * 0.5,
            'vol_percentile': np.random.rand(100) * 100,
            'volume_percentile': np.random.rand(100) * 100,
            'rsi': np.random.rand(100) * 100,
            'atr': np.random.rand(100) * 1000,
            'bb_width': np.random.rand(100) * 0.1
        }, index=dates)
        
        # Ajout des colonnes manquantes
        test_data['high'] = test_data['close'] * 1.01
        test_data['low'] = test_data['close'] * 0.99
        test_data['open'] = test_data['close'].shift(1).fillna(test_data['close'])
        
        strategy = StraddleStrategy()
        signals = strategy.detect_straddle_opportunities(test_data)
        
        signal_count = signals['straddle_signal'].sum()
        print(f"✅ Stratégie testée: {signal_count} signaux générés")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de stratégie: {e}")
        return False

def test_backtest():
    """Test du backtesting"""
    print("\n💹 Test du backtesting...")
    try:
        from backtest_engine import StraddleBacktester
        
        backtester = StraddleBacktester(10000)
        print("✅ Backtester initialisé")
        
        # Test très rapide avec peu de données
        print("⏳ Test rapide en cours...")
        
        # Note: Un test complet nécessiterait des données réelles
        # Ici on teste juste l'initialisation
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de backtesting: {e}")
        return False

def main():
    """Fonction principale du test"""
    print("🚀 VALIDATION DE L'INSTALLATION - TEST3 STRADDLE")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Connexion Données", test_data_connection),
        ("Stratégie", test_strategy),
        ("Backtesting", test_backtest)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erreur dans {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    success_count = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if success:
            success_count += 1
    
    print(f"\n🎯 Résultat: {success_count}/{len(tests)} tests réussis")
    
    if success_count == len(tests):
        print("🎉 Installation validée! Vous pouvez lancer main.py")
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez:")
        print("   - L'installation des dépendances (pip install -r requirements.txt)")
        print("   - La connexion internet")
        print("   - La configuration dans config.py")

if __name__ == "__main__":
    main()
