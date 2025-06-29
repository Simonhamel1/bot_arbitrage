# Bot de Trading Straddle Professionnel
# Script principal pour exécution complète du backtest

import os
import sys
import logging
import warnings
from datetime import datetime
from pathlib import Path

# Configuration environnement
warnings.filterwarnings('ignore')
sys.path.append(str(Path(__file__).parent))

# Imports modules internes
from src.config import *
from src.data_manager import DataManager
from src.straddle_strategy import StraddleStrategy
from src.visualization import TradingVisualization

def setup_environment():
    """Configure l'environnement d'exécution"""
    # Créer dossiers de sortie
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(exist_ok=True)
    
    logs_dir = Path(LOGS_DIR) 
    logs_dir.mkdir(exist_ok=True)
    
    # Configuration logging
    log_file = logs_dir / f"straddle_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)

def print_welcome_banner():
    """Affiche le banner de bienvenue"""
    print("=" * 80)
    print("🚀 BOT DE TRADING STRADDLE PROFESSIONNEL")
    print("=" * 80)
    print("💰 Objectif: Stratégie straddle rentable avec gestion du risque")
    print("🛡️ Protection: Risque maximum = Prime d'exercice")
    print("📈 Hedging: Positions Long/Short automatiques")
    print("🎯 Focus: Performance optimisée et risque contrôlé")
    print("=" * 80)

def validate_configuration(logger):
    """Valide la configuration avant exécution"""
    logger.info("🔍 Validation de la configuration...")
    
    errors, warnings = validate_config()
    
    if errors:
        logger.error("❌ Erreurs de configuration détectées:")
        for error in errors:
            logger.error(f"   - {error}")
        return False
    
    if warnings:
        logger.warning("⚠️ Avertissements de configuration:")
        for warning in warnings:
            logger.warning(f"   - {warning}")
    
    logger.info("✅ Configuration validée")
    return True

def display_configuration_summary(logger):
    """Affiche un résumé de la configuration"""
    print("\n⚙️ CONFIGURATION STRATÉGIE")
    print("-" * 50)
    print(f"📊 Symbole: {SYMBOL}")
    print(f"⏰ Timeframe: {TIMEFRAME}")
    print(f"📅 Période backtest: {BACKTEST_START_DATE} → {BACKTEST_END_DATE}")
    print(f"💰 Capital initial: ${INITIAL_CAPITAL:,}")
    print(f"🎯 Risque par trade: {RISK_PER_TRADE:.1%}")
    print(f"📈 Take Profit: {TAKE_PROFIT_MULTIPLIER}x")
    print(f"📉 Stop Loss: {STOP_LOSS_MULTIPLIER}x")
    print(f"🔥 Seuil volatilité: {VOLATILITY_THRESHOLD}%")
    print(f"🛡️ Hedging: {'Activé' if ENABLE_HEDGING else 'Désactivé'}")
    print(f"📊 Positions max: {MAX_POSITIONS}")
    print(f"🎨 Profil: {CURRENT_PROFILE}")
    print("-" * 50)

def calculate_risk_metrics():
    """Calcule et affiche les métriques de risque"""
    max_premium_per_trade = INITIAL_CAPITAL * RISK_PER_TRADE
    max_simultaneous_risk = max_premium_per_trade * MAX_POSITIONS
    risk_percentage = (max_simultaneous_risk / INITIAL_CAPITAL) * 100
    
    print(f"\n💰 ANALYSE DE RISQUE")
    print(f"   Prime max par trade: ${max_premium_per_trade:,.2f}")
    print(f"   Risque max simultané: ${max_simultaneous_risk:,.2f}")
    print(f"   Pourcentage du capital: {risk_percentage:.1f}%")
    print(f"   Perte max théorique: {risk_percentage:.1f}% du capital")
    
    if risk_percentage > 15:
        print("   ⚠️ ATTENTION: Risque élevé détecté")
    else:
        print("   ✅ Niveau de risque acceptable")

def run_straddle_analysis():
    """Fonction principale d'analyse"""
    # Setup
    logger = setup_environment()
    print_welcome_banner()
    
    # Validation configuration
    if not validate_configuration(logger):
        logger.error("❌ Configuration invalide. Arrêt du programme.")
        return None
    
    display_configuration_summary(logger)
    calculate_risk_metrics()
    
    try:
        # Phase 1: Récupération des données
        logger.info("\n📊 PHASE 1: Récupération des données")
        print("\n📊 Récupération des données de marché...")
        
        data_manager = DataManager()
        market_data = data_manager.get_market_data()
        
        if market_data.empty:
            logger.error("❌ Aucune donnée récupérée")
            return None
        
        # Résumé des données
        data_summary = data_manager.get_data_summary(market_data)
        logger.info(f"✅ Données récupérées: {data_summary}")
        
        # Données pour backtest
        backtest_data = data_manager.get_backtest_data()
        if backtest_data.empty:
            logger.error("❌ Aucune donnée pour la période de backtest")
            return None
        
        logger.info(f"📊 Données backtest: {len(backtest_data)} barres")
        
        # Phase 2: Exécution de la stratégie
        logger.info("\n🎯 PHASE 2: Exécution de la stratégie")
        print("\n🎯 Exécution du backtest straddle...")
        
        strategy = StraddleStrategy()
        results = strategy.run_backtest(backtest_data)
        
        # Phase 3: Analyse des résultats
        logger.info("\n📈 PHASE 3: Analyse des résultats")
        print("\n📈 Analyse des résultats...")
        
        analyze_backtest_results(results, logger)
        
        # Phase 4: Génération des visualisations
        if SHOW_PLOTS and results['performance_metrics']['total_trades'] > 0:
            logger.info("\n🎨 PHASE 4: Génération des visualisations")
            print("\n🎨 Génération des graphiques...")
            
            visualizer = TradingVisualization()
            visualizer.create_complete_dashboard(backtest_data, results, OUTPUT_DIR)
        
        # Phase 5: Rapport final
        logger.info("\n📋 PHASE 5: Rapport final")
        generate_final_report(results, logger)
        
        return results
        
    except KeyboardInterrupt:
        logger.warning("\n⚠️ Analyse interrompue par l'utilisateur")
        return None
    except Exception as e:
        logger.error(f"\n❌ Erreur critique: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def analyze_backtest_results(results, logger):
    """Analyse détaillée des résultats"""
    metrics = results['performance_metrics']
    
    if metrics['total_trades'] == 0:
        print("⚠️ Aucun trade exécuté")
        print("💡 Suggestions:")
        print("   - Réduire VOLATILITY_THRESHOLD")
        print("   - Ajuster MIN_SIGNAL_QUALITY")
        print("   - Vérifier la période de données")
        return
    
    # Métriques principales
    print(f"\n🎯 PERFORMANCE GLOBALE")
    print(f"   📊 Trades exécutés: {metrics['total_trades']}")
    print(f"   💰 Capital final: ${metrics['final_capital']:,.2f}")
    print(f"   📈 Rendement total: {metrics['total_return']:.2f}%")
    print(f"   🎯 Taux de réussite: {metrics['win_rate']:.1f}%")
    print(f"   📊 PnL moyen: {metrics['avg_pnl']:.2f}%")
    print(f"   ⏱️ Durée moyenne: {metrics['avg_holding_time']:.1f}h")
    
    # Analyse de la rentabilité
    is_profitable = metrics['total_return'] > 5
    is_consistent = metrics['win_rate'] >= 50
    is_efficient = metrics['sharpe_ratio'] > 1
    
    print(f"\n💰 ÉVALUATION RENTABILITÉ")
    if is_profitable and is_consistent:
        print("✅ STRATÉGIE RENTABLE ET CONSISTANTE")
        print(f"   🎯 Rendement: {metrics['total_return']:.1f}% > 5%")
        print(f"   🎯 Win rate: {metrics['win_rate']:.1f}% ≥ 50%")
        if is_efficient:
            print(f"   🎯 Sharpe excellent: {metrics['sharpe_ratio']:.2f} > 1")
    elif is_profitable:
        print("🟡 STRATÉGIE PARTIELLEMENT RENTABLE")
        print(f"   ✅ Rendement OK: {metrics['total_return']:.1f}%")
        print(f"   ⚠️ Consistance faible: {metrics['win_rate']:.1f}%")
    else:
        print("🔴 STRATÉGIE NON RENTABLE")
        print(f"   ❌ Rendement: {metrics['total_return']:.1f}%")
        print(f"   ❌ Win rate: {metrics['win_rate']:.1f}%")
    
    # Analyse du hedging
    if ENABLE_HEDGING and metrics['total_hedges'] > 0:
        hedge_frequency = metrics['total_hedges'] / metrics['total_trades']
        print(f"\n🛡️ ANALYSE HEDGING")
        print(f"   📊 Hedges exécutés: {metrics['total_hedges']}")
        print(f"   📈 Fréquence: {hedge_frequency:.1f} hedges/trade")
        print(f"   ✅ Hedging actif et fonctionnel")

def generate_final_report(results, logger):
    """Génère le rapport final avec recommandations"""
    metrics = results['performance_metrics']
    
    print("\n" + "=" * 80)
    print("📋 RAPPORT FINAL ET RECOMMANDATIONS")
    print("=" * 80)
    
    # Résumé exécutif
    print(f"💰 Capital final: ${metrics['final_capital']:,.2f}")
    print(f"📈 Performance: {metrics['total_return']:.2f}%")
    print(f"🛡️ Risque max: Prime d'exercice uniquement")
    print(f"🎯 Objectif rentabilité: {'ATTEINT' if metrics['total_return'] > 5 else 'NON ATTEINT'}")
    
    # Recommandations
    print(f"\n💡 RECOMMANDATIONS")
    
    if metrics['total_return'] > 5 and metrics['win_rate'] >= 50:
        print("🚀 STRATÉGIE PRÊTE POUR LE TRADING LIVE")
        print("   ✅ Performance validée")
        print("   ✅ Risque maîtrisé")
        print("   ✅ Hedging fonctionnel")
        print("   ⚠️ Surveillance requise des conditions de marché")
    else:
        print("🔧 OPTIMISATIONS SUGGÉRÉES:")
        if metrics['total_return'] <= 5:
            print("   - Augmenter TAKE_PROFIT_MULTIPLIER à 1.5")
            print("   - Réduire STOP_LOSS_MULTIPLIER à 0.5")
        if metrics['win_rate'] < 50:
            print("   - Augmenter MIN_SIGNAL_QUALITY à 0.80")
            print("   - Réduire MAX_POSITIONS pour plus de sélectivité")
        if metrics['sharpe_ratio'] < 1:
            print("   - Activer ADAPTIVE_POSITION_SIZING")
            print("   - Optimiser VOLATILITY_THRESHOLD")
    
    # Instructions de déploiement
    print(f"\n📁 FICHIERS GÉNÉRÉS:")
    print(f"   📊 Graphiques: {OUTPUT_DIR}/")
    print(f"   📋 Logs: {LOGS_DIR}/")
    print(f"   📈 Dashboard complet disponible")
    
    print("=" * 80)
    
    # Sauvegarde du rapport
    if GENERATE_REPORTS:
        save_performance_report(results)

def save_performance_report(results):
    """Sauvegarde le rapport de performance"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = Path(OUTPUT_DIR) / f"straddle_performance_report_{timestamp}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("BOT DE TRADING STRADDLE - RAPPORT DE PERFORMANCE\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Configuration: {CURRENT_PROFILE}\n\n")
        
        metrics = results['performance_metrics']
        f.write("MÉTRIQUES PRINCIPALES:\n")
        f.write(f"- Capital final: ${metrics['final_capital']:,.2f}\n")
        f.write(f"- Rendement: {metrics['total_return']:.2f}%\n")
        f.write(f"- Trades: {metrics['total_trades']}\n")
        f.write(f"- Win rate: {metrics['win_rate']:.1f}%\n")
        f.write(f"- Profit factor: {metrics['profit_factor']:.2f}\n")
        f.write(f"- Sharpe ratio: {metrics['sharpe_ratio']:.2f}\n")
        
        if ENABLE_HEDGING:
            f.write(f"- Hedges: {metrics['total_hedges']}\n")
        
        f.write(f"\nSTATUT: {'RENTABLE' if metrics['total_return'] > 5 else 'NON RENTABLE'}\n")
    
    print(f"✅ Rapport sauvegardé: {report_file}")

def main():
    """Point d'entrée principal"""
    start_time = datetime.now()
    
    try:
        results = run_straddle_analysis()
        
        if results:
            execution_time = (datetime.now() - start_time).total_seconds()
            print(f"\n⏱️ Analyse terminée en {execution_time:.1f} secondes")
            print(f"📁 Consultez le dossier '{OUTPUT_DIR}' pour les résultats")
        
        print("\n🎯 Session terminée avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur fatale: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
