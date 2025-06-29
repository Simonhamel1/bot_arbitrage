# Script de test avec paramètres optimisés pour plus d'activité
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

print("🚀 TEST AVEC PARAMÈTRES OPTIMISÉS")
print("=" * 50)

# Modifier temporairement les paramètres pour ce test
import src.config as config

# Sauvegarder les valeurs originales
original_vol_threshold = config.VOLATILITY_THRESHOLD
original_signal_quality = config.MIN_SIGNAL_QUALITY
original_profile = config.CURRENT_PROFILE

# Appliquer des paramètres plus agressifs
config.VOLATILITY_THRESHOLD = 35  # Encore plus permissif
config.MIN_SIGNAL_QUALITY = 0.60  # Moins sélectif
config.MAX_POSITIONS = 5  # Plus de positions simultanées

print(f"🎯 Seuil de volatilité: {config.VOLATILITY_THRESHOLD}% (vs {original_vol_threshold}% avant)")
print(f"🎯 Qualité signal minimum: {config.MIN_SIGNAL_QUALITY} (vs {original_signal_quality} avant)")
print(f"🎯 Profil: AGRESSIF")
print()

try:
    from src.data_manager import DataManager
    from src.straddle_strategy import StraddleStrategy
    
    print("📊 Récupération des données...")
    data_manager = DataManager()
    
    # Prendre une période plus récente et volatile
    backtest_data = data_manager.get_backtest_data()
    print(f"✅ Données récupérées: {len(backtest_data)} barres")
    
    # Afficher quelques statistiques sur la volatilité
    vol_stats = backtest_data['volatility'].describe()
    print(f"📈 Volatilité - Min: {vol_stats['min']:.2%}, Max: {vol_stats['max']:.2%}, Moyenne: {vol_stats['mean']:.2%}")
    
    high_vol_count = (backtest_data['volatility'] > config.VOLATILITY_THRESHOLD/100).sum()
    print(f"🔥 Périodes de haute volatilité (>{config.VOLATILITY_THRESHOLD}%): {high_vol_count}/{len(backtest_data)} ({high_vol_count/len(backtest_data)*100:.1f}%)")
    
    if high_vol_count == 0:
        print("⚠️ AUCUNE période ne dépasse le seuil ! Réduisons encore...")
        config.VOLATILITY_THRESHOLD = 25
        high_vol_count = (backtest_data['volatility'] > config.VOLATILITY_THRESHOLD/100).sum()
        print(f"🔥 Avec seuil à {config.VOLATILITY_THRESHOLD}%: {high_vol_count} périodes")
    
    print("\n🎯 Lancement du backtest optimisé...")
    strategy = StraddleStrategy()
    results = strategy.run_backtest(backtest_data)
    
    print("\n📊 RÉSULTATS:")
    if 'performance_metrics' in results:
        metrics = results['performance_metrics']
        print(f"   💼 Trades exécutés: {metrics.get('total_trades', 0)}")
        print(f"   💰 Capital final: ${metrics.get('final_capital', 0):,.2f}")
        print(f"   📈 Rendement: {metrics.get('total_return', 0):.2f}%")
        print(f"   🎯 Win rate: {metrics.get('win_rate', 0):.1f}%")
        
        if metrics.get('total_trades', 0) > 0:
            print("✅ SUCCÈS ! Des trades ont été exécutés")
        else:
            print("❌ Toujours aucun trade. Les conditions de marché sont très calmes.")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

finally:
    # Restaurer les valeurs originales
    config.VOLATILITY_THRESHOLD = original_vol_threshold
    config.MIN_SIGNAL_QUALITY = original_signal_quality
    config.CURRENT_PROFILE = original_profile
