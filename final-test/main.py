# Backtesting simple d'une stratégie straddle sur BTC/USDT

import os
import warnings
warnings.filterwarnings('ignore')

from config import *
from data_manager import DataManager
from straddle_strategy import StraddleStrategy
from visualization import create_simple_charts, print_simple_results

def main():
    """Fonction principale - backtesting simple"""
    print("🚀 Backtesting Stratégie Straddle - BTC/USDT")
    print("=" * 50)
    
    # Afficher la configuration actuelle
    if USE_DATE_RANGE:
        print(f"📅 Période d'analyse: {START_DATE} → {END_DATE}")
    else:
        print(f"📅 Analyse des {DAYS_OF_DATA} derniers jours")
    
    print(f"🎯 Seuil volatilité: {VOLATILITY_THRESHOLD}e percentile")
    print(f"💰 Capital initial: ${INITIAL_CAPITAL:,}")
    print("-" * 50)
    
    # Créer le dossier de sortie
    os.makedirs("output", exist_ok=True)
    
    # 1. Chargement des données
    print("📊 Chargement des données BTC/USDT...")
    data_manager = DataManager()
    df = data_manager.get_data()
    
    if df is None or df.empty:
        print("❌ Erreur lors du chargement des données")
        return
    
    print(f"✅ {len(df)} bougies chargées ({df.index[0].strftime('%Y-%m-%d')} → {df.index[-1].strftime('%Y-%m-%d')})")
    
    # 2. Détection des signaux de trading
    print("🎯 Détection des signaux...")
    strategy = StraddleStrategy()
    df = strategy.detect_signals(df)
    
    # 3. Exécution du backtest
    print("⚡ Backtesting en cours...")
    results = strategy.backtest(df)
    
    # 4. Affichage des résultats
    print_simple_results(results)
    
    # 5. Génération des graphiques
    print("\n🎨 Génération des graphiques...")
    create_simple_charts(df, results)
    
    print("\n✅ Backtest terminé ! Graphiques sauvegardés dans le dossier 'output/'")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Interruption par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
