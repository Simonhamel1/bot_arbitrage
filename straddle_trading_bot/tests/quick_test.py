# Test Rapide et Validation du Bot Straddle
# Script de diagnostic pour vérifier le bon fonctionnement

import sys
import traceback
from pathlib import Path

# Ajouter le dossier src au path
sys.path.append(str(Path(__file__).parent / 'src'))

def test_imports():
    """Test des imports essentiels"""
    print("🔍 Test des imports...")
    
    try:
        # Test import configuration
        from src import config
        print("✅ Configuration importée")
        
        # Test import data manager
        from src.data_manager import DataManager
        print("✅ DataManager importé")
        
        # Test import stratégie
        from src.straddle_strategy import StraddleStrategy
        print("✅ StraddleStrategy importée")
        
        # Test import visualisation
        from src.visualization import TradingVisualization
        print("✅ TradingVisualization importée")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

def test_configuration():
    """Test de la configuration"""
    print("\n⚙️ Test de la configuration...")
    
    try:
        from src.config import validate_config, CURRENT_PROFILE
        
        errors, warnings = validate_config()
        
        if errors:
            print("❌ Erreurs de configuration:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        if warnings:
            print("⚠️ Avertissements:")
            for warning in warnings:
                print(f"   - {warning}")
        
        print(f"✅ Configuration valide (Profil: {CURRENT_PROFILE})")
        return True
        
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        return False

def test_data_manager():
    """Test du gestionnaire de données"""
    print("\n📊 Test du DataManager...")
    
    try:
        from src.data_manager import DataManager
        
        # Initialisation
        dm = DataManager()
        print("✅ DataManager initialisé")
        
        # Test de connexion exchange (sans récupération réelle)
        if dm.exchange:
            print("✅ Connexion exchange OK")
        else:
            print("⚠️ Connexion exchange échouée (normal en mode test)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur DataManager: {e}")
        traceback.print_exc()
        return False

def test_strategy():
    """Test de la stratégie"""
    print("\n🎯 Test de la StraddleStrategy...")
    
    try:
        from src.straddle_strategy import StraddleStrategy
        from src.config import INITIAL_CAPITAL, RISK_PER_TRADE
        
        # Initialisation
        strategy = StraddleStrategy()
        print("✅ Stratégie initialisée")
        
        # Test Black-Scholes
        result = strategy.simulate_straddle_price(
            spot_price=50000,
            strike=50000,
            volatility=0.5,
            time_to_expiry=30/365
        )
        
        if result['straddle_price'] > 0:
            print(f"✅ Black-Scholes OK (Prix straddle: ${result['straddle_price']:.2f})")
        else:
            print("❌ Erreur Black-Scholes")
            return False
        
        # Test calcul taille position
        contracts = strategy.calculate_position_size(1000, 0.8)
        print(f"✅ Calcul position OK ({contracts} contrats)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur Stratégie: {e}")
        traceback.print_exc()
        return False

def test_visualization():
    """Test du module de visualisation"""
    print("\n🎨 Test de TradingVisualization...")
    
    try:
        from src.visualization import TradingVisualization
        
        # Initialisation
        viz = TradingVisualization()
        print("✅ TradingVisualization initialisée")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur Visualisation: {e}")
        traceback.print_exc()
        return False

def display_system_info():
    """Affiche les informations système"""
    print("\n💻 Informations système:")
    
    # Python version
    print(f"   Python: {sys.version}")
    
    # Dépendances
    dependencies = [
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'ccxt'
    ]
    
    for dep in dependencies:
        try:
            module = __import__(dep)
            version = getattr(module, '__version__', 'Version inconnue')
            print(f"   {dep}: {version}")
        except ImportError:
            print(f"   {dep}: ❌ Non installé")

def display_configuration_summary():
    """Affiche un résumé de la configuration"""
    print("\n📋 Résumé de la configuration:")
    
    try:
        from src import config
        
        print(f"   Symbole: {config.SYMBOL}")
        print(f"   Capital initial: ${config.INITIAL_CAPITAL:,}")
        print(f"   Risque par trade: {config.RISK_PER_TRADE:.1%}")
        print(f"   Positions max: {config.MAX_POSITIONS}")
        print(f"   Hedging: {'Activé' if config.ENABLE_HEDGING else 'Désactivé'}")
        print(f"   Profil: {config.CURRENT_PROFILE}")
        
    except Exception as e:
        print(f"   ❌ Erreur affichage config: {e}")

def main():
    """Fonction principale de test"""
    print("🚀 DIAGNOSTIC BOT STRADDLE")
    print("=" * 50)
    
    # Tests séquentiels
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("DataManager", test_data_manager),
        ("Stratégie", test_strategy),
        ("Visualisation", test_visualization)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Échec du test {test_name}: {e}")
            results.append(False)
    
    # Résumé des tests
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, _) in enumerate(tests):
        status = "✅" if results[i] else "❌"
        print(f"{status} {test_name}")
    
    print(f"\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT PASSÉS!")
        print("✅ Le bot est prêt à être utilisé")
        print("\n💡 Pour lancer l'analyse complète:")
        print("   python main.py")
    else:
        print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus")
        print("📋 Consultez la documentation pour l'installation")
    
    # Informations supplémentaires
    display_system_info()
    display_configuration_summary()
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
