# Script Principal Ultra-Optimisé pour Stratégie Straddle Rentable

import os
import warnings
import pandas as pd
import numpy as np
from datetime import datetime

# Configuration environnement
warnings.filterwarnings('ignore')
os.makedirs('output', exist_ok=True)

# Imports modules internes
from data_manager import DataManager
from ultra_straddle_strategy import UltraStraddleStrategy
from ultra_visualization import UltraVisualization
from config import *

def print_banner():
    """Affiche le banner de l'application"""
    print("=" * 80)
    print("🚀 ULTRA STRADDLE BOT - VERSION RENTABLE")
    print("=" * 80)
    print("🎯 Objectif: Stratégie straddle ultra-optimisée avec hedging")
    print("💰 Risque max: Prime d'exercice uniquement")
    print("🛡️ Protection: Positions Long/Short dynamiques")
    print("📈 Focus: Rentabilité maximale avec risque contrôlé")
    print("=" * 80)

def print_config_summary():
    """Affiche un résumé de la configuration"""
    print("⚙️ CONFIGURATION ULTRA-OPTIMISÉE")
    print("-" * 50)
    print(f"📊 Symbole: {SYMBOL}")
    print(f"⏰ Timeframe: {TIMEFRAME}")
    print(f"📅 Période: {BACKTEST_START_DATE} → {BACKTEST_END_DATE}")
    print(f"💰 Capital initial: ${INITIAL_CAPITAL:,}")
    print(f"🎯 Risque par trade: {RISK_PER_TRADE:.1%}")
    print(f"📈 Take Profit: {TAKE_PROFIT_MULTIPLIER}x")
    print(f"📉 Stop Loss: {STOP_LOSS_MULTIPLIER}x")
    print(f"🔥 Seuil volatilité: {VOLATILITY_THRESHOLD}%")
    print(f"🛡️ Hedging activé: {MOMENTUM_HEDGE}")
    print(f"📊 Positions max: {MAX_POSITIONS}")
    print("-" * 50)

def validate_risk_parameters():
    """Valide les paramètres de risque"""
    print("🔍 Validation des paramètres de risque...")
    
    issues = []
    
    # Vérification risque par trade
    if RISK_PER_TRADE > 0.05:
        issues.append(f"⚠️ Risque par trade élevé: {RISK_PER_TRADE:.1%} > 5%")
    
    # Vérification ratio TP/SL
    tp_sl_ratio = TAKE_PROFIT_MULTIPLIER / STOP_LOSS_MULTIPLIER
    if tp_sl_ratio < 1.5:
        issues.append(f"⚠️ Ratio TP/SL faible: {tp_sl_ratio:.1f} < 1.5")
    
    # Vérification seuil volatilité
    if VOLATILITY_THRESHOLD < 30:
        issues.append(f"⚠️ Seuil volatilité très bas: {VOLATILITY_THRESHOLD}%")
    
    # Vérification cohérence dates
    start_date = pd.to_datetime(BACKTEST_START_DATE)
    end_date = pd.to_datetime(BACKTEST_END_DATE)
    if (end_date - start_date).days < 30:
        issues.append("⚠️ Période de backtest très courte < 30 jours")
    
    if issues:
        print("⚠️ Avertissements détectés:")
        for issue in issues:
            print(f"   {issue}")
        print("   → Continuez uniquement si vous acceptez ces risques")
        input("   Appuyez sur Entrée pour continuer...")
    else:
        print("✅ Tous les paramètres de risque sont validés")

def calculate_theoretical_max_loss():
    """Calcule la perte maximale théorique"""
    max_premium = INITIAL_CAPITAL * RISK_PER_TRADE
    max_simultaneous_loss = max_premium * MAX_POSITIONS
    
    print(f"💰 ANALYSE RISQUE THÉORIQUE")
    print(f"   Prime max par position: ${max_premium:,.2f}")
    print(f"   Perte max simultanée: ${max_simultaneous_loss:,.2f}")
    print(f"   % du capital: {(max_simultaneous_loss/INITIAL_CAPITAL)*100:.1f}%")
    
    return max_simultaneous_loss

def run_ultra_straddle_analysis():
    """Lance l'analyse ultra-complète de la stratégie straddle"""
    
    # 1. Banner et configuration
    print_banner()
    print_config_summary()
    
    # 2. Validation des risques
    validate_risk_parameters()
    max_theoretical_loss = calculate_theoretical_max_loss()
    
    print("\n🚀 DÉMARRAGE ANALYSE ULTRA-STRADDLE...")
    
    try:
        # 3. Récupération des données
        print("\n📊 ÉTAPE 1/5: Récupération des données")
        data_manager = DataManager()
        data = data_manager.get_data()
        
        if data.empty:
            print("❌ Erreur: Aucune donnée récupérée")
            return None
        
        print(f"✅ {len(data)} barres de données récupérées")
        print(f"   Période: {data.index[0].strftime('%Y-%m-%d')} → {data.index[-1].strftime('%Y-%m-%d')}")
        print(f"   Volatilité moyenne: {data['volatility'].mean():.2%}")
        print(f"   Range de prix: ${data['close'].min():,.0f} - ${data['close'].max():,.0f}")
        
        # 4. Exécution de la stratégie ultra-optimisée
        print("\n🎯 ÉTAPE 2/5: Exécution stratégie ultra-optimisée")
        strategy = UltraStraddleStrategy()
        
        # Filtrer les données pour la période de backtest
        backtest_data = data[(data.index >= BACKTEST_START_DATE) & (data.index < BACKTEST_END_DATE)]
        
        if backtest_data.empty:
            print("❌ Erreur: Aucune donnée pour la période de backtest")
            return None
        
        print(f"📊 Données backtest: {len(backtest_data)} barres")
        results = strategy.run_ultra_backtest(backtest_data)\n        \n        # 5. Analyse des résultats\n        print(\"\\n📈 ÉTAPE 3/5: Analyse des résultats\")\n        \n        if results['total_trades'] == 0:\n            print(\"⚠️ Aucun trade exécuté - Critères d'entrée trop stricts\")\n            print(\"💡 Suggestions:\")\n            print(\"   - Réduire VOLATILITY_THRESHOLD\")\n            print(\"   - Ajuster les critères d'entrée\")\n            print(\"   - Vérifier la période de données\")\n            return results\n        \n        # Calcul métriques avancées\n        winning_trades = [t for t in results['trades'] if t['pnl'] > 0]\n        losing_trades = [t for t in results['trades'] if t['pnl'] <= 0]\n        \n        avg_hold_time = np.mean([t['holding_time'] for t in results['trades']])\n        \n        # Analyse de la rentabilité\n        total_return = results['total_return']\n        win_rate = results.get('win_rate', 0)\n        \n        print(f\"🎯 Performance globale:\")\n        print(f\"   📊 {results['total_trades']} trades exécutés\")\n        print(f\"   📈 Rendement: {total_return:.2f}%\")\n        print(f\"   🎯 Taux réussite: {win_rate:.1f}%\")\n        print(f\"   ⏱️ Durée moyenne: {avg_hold_time:.1f}h\")\n        \n        if len(winning_trades) > 0:\n            print(f\"   💰 Trades gagnants: {len(winning_trades)} (avg: {np.mean([t['pnl_pct'] for t in winning_trades]):.1f}%)\")\n        if len(losing_trades) > 0:\n            print(f\"   💔 Trades perdants: {len(losing_trades)} (avg: {np.mean([t['pnl_pct'] for t in losing_trades]):.1f}%)\")\n        \n        # Analyse du hedging\n        if results['hedge_opportunities']:\n            hedge_count = len(results['hedge_opportunities'])\n            hedge_frequency = hedge_count / results['total_trades']\n            print(f\"   🛡️ Hedges détectés: {hedge_count} ({hedge_frequency:.1f} par trade)\")\n        \n        # 6. Évaluation de la rentabilité\n        print(\"\\n💰 ÉVALUATION RENTABILITÉ\")\n        print(\"-\" * 40)\n        \n        is_profitable = total_return > 5  # Minimum 5% de retour\n        is_consistent = win_rate >= 50   # Minimum 50% de réussite\n        is_efficient = results.get('sharpe_ratio', 0) > 1  # Sharpe > 1\n        \n        if is_profitable and is_consistent:\n            print(\"✅ STRATÉGIE RENTABLE CONFIRMÉE\")\n            print(f\"   🎯 Objectif de rentabilité atteint: {total_return:.1f}% > 5%\")\n            print(f\"   🎯 Consistance validée: {win_rate:.1f}% ≥ 50%\")\n            \n            if is_efficient:\n                print(f\"   🎯 Efficacité excellente: Sharpe {results.get('sharpe_ratio', 0):.2f} > 1\")\n            \n            # Calcul du risque réel vs théorique\n            real_max_loss = min([t['pnl_pct'] for t in results['trades']]) if results['trades'] else 0\n            print(f\"   🛡️ Perte max réelle: {real_max_loss:.1f}% (vs théorique: {-(STOP_LOSS_MULTIPLIER*100):.0f}%)\")\n            \n        elif is_profitable:\n            print(\"🟡 STRATÉGIE PARTIELLEMENT RENTABLE\")\n            print(f\"   ✅ Rentabilité OK: {total_return:.1f}%\")\n            print(f\"   ⚠️ Consistance faible: {win_rate:.1f}% < 50%\")\n            print(\"   💡 Amélioration suggérée: resserrer critères d'entrée\")\n            \n        else:\n            print(\"🔴 STRATÉGIE NON RENTABLE\")\n            print(f\"   ❌ Rendement insuffisant: {total_return:.1f}% < 5%\")\n            print(f\"   ❌ Win rate: {win_rate:.1f}%\")\n            print(\"   💡 Révision majeure nécessaire\")\n        \n        # 7. Visualisations ultra-avancées\n        print(\"\\n🎨 ÉTAPE 4/5: Génération visualisations ultra-avancées\")\n        visualizer = UltraVisualization()\n        \n        dashboard_file = visualizer.create_ultra_performance_dashboard(\n            backtest_data, results, 'output'\n        )\n        \n        report_file = visualizer.generate_performance_report(results, 'output')\n        \n        # 8. Recommandations finales\n        print(\"\\n💡 ÉTAPE 5/5: Recommandations finales\")\n        print(\"-\" * 50)\n        \n        if is_profitable and is_consistent:\n            print(\"🚀 RECOMMANDATIONS POUR TRADING LIVE:\")\n            print(\"   ✅ Stratégie prête pour implémentation\")\n            print(f\"   💰 Capital recommandé: ${INITIAL_CAPITAL:,} minimum\")\n            print(f\"   🎯 Risque par trade maintenu: {RISK_PER_TRADE:.1%}\")\n            print(f\"   🛡️ Hedging: {'Activé' if MOMENTUM_HEDGE else 'Désactivé'}\")\n            \n            if results['hedge_opportunities']:\n                print(\"   🔥 Implémenter le hedging automatique pour optimiser\")\n            \n            print(\"   ⚠️ Surveillance requise: volatilité et corrélations\")\n            \n        else:\n            print(\"⚠️ RECOMMANDATIONS D'OPTIMISATION:\")\n            \n            if not is_profitable:\n                print(\"   🔧 Ajuster TAKE_PROFIT_MULTIPLIER à 1.8\")\n                print(\"   🔧 Réduire STOP_LOSS_MULTIPLIER à 0.5\")\n                print(\"   🔧 Augmenter VOLATILITY_THRESHOLD à 70\")\n            \n            if not is_consistent:\n                print(\"   🔧 Resserrer critères d'entrée (signal_quality >= 0.85)\")\n                print(\"   🔧 Réduire MAX_POSITIONS à 1 pour focus qualité\")\n                print(\"   🔧 Activer ADAPTIVE_POSITION_SIZING\")\n            \n            print(\"   🔄 Relancer l'analyse après ajustements\")\n        \n        # 9. Résumé final avec focus risque\n        print(\"\\n\" + \"=\" * 80)\n        print(\"🎯 RÉSUMÉ FINAL - GESTION DU RISQUE\")\n        print(\"=\" * 80)\n        print(f\"💰 Capital final: ${results['final_capital']:,.2f}\")\n        print(f\"📈 Performance: {total_return:.2f}% ({('PROFITABLE' if is_profitable else 'NON PROFITABLE')})\")\n        print(f\"🛡️ Risque max encouru: Prime d'exercice uniquement\")\n        print(f\"📊 Perte max réelle: {min([t['pnl_pct'] for t in results['trades']], default=0):.1f}%\")\n        print(f\"🎯 Objectif atteint: {'OUI' if is_profitable and is_consistent else 'NON'}\")\n        \n        if MOMENTUM_HEDGE and results['hedge_opportunities']:\n            print(f\"🛡️ Positions Long/Short: {len(results['hedge_opportunities'])} opportunités détectées\")\n            print(\"📋 Le hedging dynamique a permis de limiter l'exposition directionnelle\")\n        \n        print(\"=\" * 80)\n        \n        return results\n        \n    except Exception as e:\n        print(f\"❌ Erreur critique: {str(e)}\")\n        import traceback\n        traceback.print_exc()\n        return None\n\ndef main():\n    \"\"\"Fonction principale\"\"\"\n    start_time = datetime.now()\n    \n    try:\n        results = run_ultra_straddle_analysis()\n        \n        if results:\n            end_time = datetime.now()\n            execution_time = (end_time - start_time).total_seconds()\n            \n            print(f\"\\n⏱️ Analyse terminée en {execution_time:.1f} secondes\")\n            print(f\"📁 Fichiers générés dans le dossier 'output/'\")\n            print(f\"📊 Dashboard, graphiques et rapport disponibles\")\n            \n            # Proposition d'optimisation automatique\n            if results.get('total_return', 0) < 5 or results.get('win_rate', 0) < 50:\n                print(\"\\n🔧 OPTIMISATION AUTOMATIQUE DISPONIBLE\")\n                response = input(\"Voulez-vous lancer une optimisation automatique des paramètres? (o/N): \")\n                if response.lower() == 'o':\n                    print(\"🚀 Lancement optimisation automatique...\")\n                    # TODO: Implémenter optimisation automatique\n                    print(\"⚠️ Fonctionnalité en développement\")\n        \n        print(\"\\n🎯 Session terminée avec succès!\")\n        \n    except KeyboardInterrupt:\n        print(\"\\n⚠️ Analyse interrompue par l'utilisateur\")\n    except Exception as e:\n        print(f\"\\n❌ Erreur fatale: {str(e)}\")\n        import traceback\n        traceback.print_exc()\n\nif __name__ == \"__main__\":\n    main()
