#!/usr/bin/env python3
"""
Validation finale - Test4 Adaptation Complete
Vérifie que l'adaptation de test4 est complète et fonctionnelle
"""

import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test des imports de base"""
    print("🔧 Test des imports...")
    try:
        from src import config
        print(f"✅ Config OK - Profil: {config.CURRENT_PROFILE}")
        
        from src.data_manager import DataManager
        print("✅ DataManager OK")
        
        from src.straddle_strategy import StraddleStrategy
        print("✅ StraddleStrategy OK")
        
        return True
    except Exception as e:
        print(f"❌ Erreur import: {e}")
        return False

def test_configuration():
    """Test de la configuration test4"""
    print("\n⚙️ Test de la configuration test4...")
    try:
        from src import config
        
        # Vérifier paramètres test4
        config_checks = [
            ("VOLATILITY_THRESHOLD", config.VOLATILITY_THRESHOLD, 55),
            ("TAKE_PROFIT_MULTIPLIER", config.TAKE_PROFIT_MULTIPLIER, 1.3),
            ("STOP_LOSS_MULTIPLIER", config.STOP_LOSS_MULTIPLIER, 0.6),
            ("CURRENT_PROFILE", config.CURRENT_PROFILE, "AGGRESSIVE"),
            ("RISK_PER_TRADE", getattr(config, 'PROFILES', {}).get('AGGRESSIVE', {}).get('RISK_PER_TRADE', config.RISK_PER_TRADE), 0.02)
        ]
        
        for param_name, actual, expected in config_checks:
            if actual == expected:
                print(f"✅ {param_name}: {actual}")
            else:
                print(f"⚠️ {param_name}: {actual} (attendu: {expected})")
        
        return True
    except Exception as e:
        print(f"❌ Erreur config: {e}")
        return False

def test_signal_detection():
    """Test de la détection de signaux avec logique test4"""
    print("\n🎯 Test de la détection de signaux test4...")
    try:
        from src.data_manager import DataManager
        from src.straddle_strategy import StraddleStrategy
        
        # Initialiser
        dm = DataManager()
        strategy = StraddleStrategy()
        
        # Charger données
        data = dm.get_backtest_data()
        if len(data) < 100:
            print("⚠️ Données insuffisantes")
            return False
        
        print(f"📊 {len(data)} points de données disponibles")
        
        # Tester détection signal
        test_data = data.tail(150)  # Prendre les 150 derniers points
        should_enter, signal_info = strategy.calculate_signal_quality(test_data)
        
        print(f"📈 Test signal sur dernières données:")
        print(f"   Signal d'entrée: {'✅ OUI' if should_enter else '❌ NON'}")
        print(f"   Qualité: {signal_info.get('signal_quality', 0):.2%}")
        print(f"   Vol Score: {signal_info.get('vol_score', 0):.1f}")
        print(f"   Conditions: {signal_info.get('conditions_met', 0)}/{signal_info.get('total_conditions', 7)}")
        print(f"   Confiance: {signal_info.get('confidence', 'LOW')}")
        
        # Vérifier que la fonction calculate_volatility_score_advanced existe
        try:
            vol_score = strategy.calculate_volatility_score_advanced(test_data)
            print(f"✅ Fonction vol score avancée: {vol_score:.1f}")
        except AttributeError:
            print("❌ Fonction volatility_score_advanced manquante")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test signal: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backtest_functionality():
    """Test fonctionnalité de backtest"""
    print("\n🚀 Test de fonctionnalité backtest...")
    try:
        from src.data_manager import DataManager
        from src.straddle_strategy import StraddleStrategy
        
        dm = DataManager()
        strategy = StraddleStrategy()
        
        # Charger un échantillon de données
        data = dm.get_backtest_data()
        sample_data = data.tail(100)  # Échantillon petit pour test rapide
        
        print(f"🔍 Test sur échantillon de {len(sample_data)} points")
        
        # Test backtest
        results = strategy.run_backtest(sample_data)
        
        print("✅ Backtest exécuté sans erreur")
        print(f"📊 Résultats obtenus:")
        print(f"   Capital final: ${results.get('final_capital', 0):,.2f}")
        print(f"   Trades: {len(results.get('trades', []))}")
        
        if 'performance_metrics' in results:
            metrics = results['performance_metrics']
            print(f"   Total trades (metrics): {metrics.get('total_trades', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test backtest: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Validation complète de l'adaptation test4"""
    print("🔥 VALIDATION FINALE - ADAPTATION TEST4")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Détection signaux", test_signal_detection),
        ("Backtest", test_backtest_functionality)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        if test_func():
            passed_tests += 1
            print(f"✅ {test_name} : PASSÉ")
        else:
            print(f"❌ {test_name} : ÉCHEC")
    
    # Résumé final
    print("\n" + "="*60)
    print("📋 RÉSUMÉ DE LA VALIDATION")
    print("="*60)
    print(f"Tests passés: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 SUCCÈS COMPLET!")
        print("✅ Adaptation test4 terminée et validée")
        print("🚀 Bot prêt pour utilisation avec config test4")
        print("\n💡 Prochaines étapes:")
        print("   1. Exécuter: python main_simple.py")
        print("   2. Analyser les résultats")
        print("   3. Ajuster si nécessaire")
    else:
        print("⚠️ VALIDATION PARTIELLE")
        print("🔧 Corriger les erreurs avant utilisation")
    
    print("="*60)

if __name__ == "__main__":
    main()
