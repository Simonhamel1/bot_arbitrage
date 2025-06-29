# Backtesting Stratégie Straddle Optimisée avec Gestion Long/Short

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from config import *
from data_manager import DataManager
from advanced_straddle import AdvancedStraddleStrategy

def create_results_visualization(results, data):
    """Crée des graphiques pour analyser les résultats"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('📊 Résultats Stratégie Straddle Optimisée', fontsize=16, fontweight='bold')
    
    # 1. Prix BTC avec trades
    ax1.plot(data.index, data['close'], 'k-', linewidth=1, alpha=0.7, label='Prix BTC')
    
    if results['trades']:
        trades_df = pd.DataFrame(results['trades'])
        
        # Entrées
        entries = trades_df.drop_duplicates('entry_time')
        ax1.scatter(entries['entry_time'], entries['entry_price'], 
                   color='blue', marker='o', s=60, label='Entrées Straddle', zorder=5)
        
        # Sorties rentables vs perdantes
        profitable = trades_df[trades_df['pnl'] > 0]
        losing = trades_df[trades_df['pnl'] <= 0]
        
        if len(profitable) > 0:
            ax1.scatter(profitable['exit_time'], profitable['exit_price'], 
                       color='green', marker='^', s=80, label='Sorties Profit', zorder=5)
        
        if len(losing) > 0:
            ax1.scatter(losing['exit_time'], losing['exit_price'], 
                       color='red', marker='v', s=80, label='Sorties Perte', zorder=5)
    
    ax1.set_title('Prix BTC avec Trades Straddle')
    ax1.set_ylabel('Prix ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Évolution du capital
    if results['daily_pnl']:
        pnl_df = pd.DataFrame(results['daily_pnl'])
        total_value = pnl_df['capital'] + pnl_df['positions_value']
        
        ax2.plot(pnl_df['timestamp'], total_value, 'b-', linewidth=2, label='Capital Total')
        ax2.axhline(y=INITIAL_CAPITAL, color='gray', linestyle='--', alpha=0.5, label='Capital Initial')
        
        # Zones de profit/perte
        ax2.fill_between(pnl_df['timestamp'], INITIAL_CAPITAL, total_value, 
                        where=(total_value >= INITIAL_CAPITAL), alpha=0.3, color='green', label='Profit')
        ax2.fill_between(pnl_df['timestamp'], INITIAL_CAPITAL, total_value, 
                        where=(total_value < INITIAL_CAPITAL), alpha=0.3, color='red', label='Perte')
    
    ax2.set_title('Évolution du Capital')
    ax2.set_ylabel('Capital ($)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Distribution des PnL
    if results['trades']:
        trades_df = pd.DataFrame(results['trades'])
        pnl_pcts = trades_df['pnl_pct']
        
        ax3.hist(pnl_pcts, bins=20, alpha=0.7, color='steelblue', edgecolor='black')
        ax3.axvline(x=0, color='red', linestyle='--', label='Seuil de rentabilité')
        ax3.axvline(x=pnl_pcts.mean(), color='orange', linestyle='-', 
                   label=f'PnL Moyen: {pnl_pcts.mean():.1f}%')
        
        ax3.set_title('Distribution des PnL par Trade')
        ax3.set_xlabel('PnL (%)')
        ax3.set_ylabel('Nombre de Trades')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    
    # 4. Analyse des hedges
    if results['hedge_opportunities']:
        hedge_df = pd.DataFrame(results['hedge_opportunities'])
        hedge_counts = hedge_df.groupby(hedge_df['timestamp'].dt.date).size()
        
        ax4.bar(range(len(hedge_counts)), hedge_counts.values, 
               color='orange', alpha=0.7)
        ax4.set_title('Opportunités de Hedge par Jour')
        ax4.set_xlabel('Jours')
        ax4.set_ylabel('Nombre d\'Opportunités')
        ax4.grid(True, alpha=0.3)
    else:
        ax4.text(0.5, 0.5, 'Aucune opportunité de hedge détectée', 
                ha='center', va='center', transform=ax4.transAxes, fontsize=12)
        ax4.set_title('Opportunités de Hedge')
    
    plt.tight_layout()
    
    # Sauvegarder
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'output/straddle_results_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"📊 Graphiques sauvegardés: {filename}")
    
    plt.show()

def print_detailed_results(results):
    """Affiche les résultats détaillés"""
    
    print("\n" + "="*80)
    print("📊 RÉSULTATS DÉTAILLÉS - STRATÉGIE STRADDLE OPTIMISÉE")
    print("="*80)
    
    print(f"💰 Capital Initial: ${INITIAL_CAPITAL:,.2f}")
    print(f"💰 Capital Final: ${results['final_capital']:,.2f}")
    print(f"📈 Rendement Total: {results['total_return']:.2f}%")
    print(f"💵 Gain/Perte: ${results['final_capital'] - INITIAL_CAPITAL:,.2f}")
    
    if results['trades']:
        trades_df = pd.DataFrame(results['trades'])
        
        print(f"\n🎯 STATISTIQUES DE TRADING")
        print(f"📊 Nombre de Trades: {len(trades_df)}")
        print(f"🏆 Trades Gagnants: {len(trades_df[trades_df['pnl'] > 0])}")
        print(f"� Trades Perdants: {len(trades_df[trades_df['pnl'] <= 0])}")
        print(f"🎯 Taux de Réussite: {results['win_rate']:.1f}%")
        print(f"💰 PnL Moyen: {results['avg_pnl']:.2f}%")
        print(f"🚀 Meilleur Trade: +{results['max_win']:.2f}%")
        print(f"💥 Pire Trade: {results['max_loss']:.2f}%")
        
        # Analyse des raisons de sortie
        exit_reasons = trades_df['exit_reason'].value_counts()
        print(f"\n🚪 RAISONS DE SORTIE")
        for reason, count in exit_reasons.items():
            percentage = (count / len(trades_df)) * 100
            print(f"   {reason}: {count} ({percentage:.1f}%)")
        
        # Analyse temporelle
        holding_times = trades_df['holding_time']
        print(f"\n⏱️ DURÉES DES TRADES")
        print(f"   Durée moyenne: {holding_times.mean():.1f} heures")
        print(f"   Durée médiane: {holding_times.median():.1f} heures")
        print(f"   Durée min: {holding_times.min():.1f} heures")
        print(f"   Durée max: {holding_times.max():.1f} heures")
    
    # Opportunités de hedge
    if results['hedge_opportunities']:
        print(f"\n🛡️ OPPORTUNITÉS DE HEDGE")
        print(f"   Total détectées: {len(results['hedge_opportunities'])}")
        
        hedge_df = pd.DataFrame(results['hedge_opportunities'])
        hedge_types = hedge_df['hedge_info'].apply(lambda x: x.get('type', 'Unknown')).value_counts()
        
        print(f"   Types de hedge:")
        for hedge_type, count in hedge_types.items():
            print(f"     {hedge_type}: {count}")
    
    # Analyse du risque
    if results['trades'] and results['daily_pnl']:
        print(f"\n⚠️ ANALYSE DU RISQUE")
        
        pnl_df = pd.DataFrame(results['daily_pnl'])
        total_values = pnl_df['capital'] + pnl_df['positions_value']
        cumulative_max = total_values.expanding().max()
        drawdowns = (total_values - cumulative_max) / cumulative_max * 100
        max_drawdown = drawdowns.min()
        
        print(f"   Drawdown Maximum: {max_drawdown:.2f}%")
        print(f"   Risque par Trade: {RISK_PER_TRADE*100:.1f}%")

def main():
    """Fonction principale optimisée"""
    
    print("🚀 STRATÉGIE STRADDLE OPTIMISÉE AVEC GESTION LONG/SHORT")
    print("="*60)
    print(f"📅 Période: {START_DATE} → {END_DATE}")
    print(f"💰 Capital: ${INITIAL_CAPITAL:,.2f}")
    print(f"🎯 Risque par trade: {RISK_PER_TRADE*100:.1f}%")
    print(f"📊 Seuil volatilité: {VOLATILITY_THRESHOLD}e percentile")
    print(f"🎯 Take Profit: {TAKE_PROFIT_MULTIPLIER:.1f}x")
    print(f"🛑 Stop Loss: {STOP_LOSS_MULTIPLIER:.1f}x")
    
    # Créer le dossier de sortie
    os.makedirs("output", exist_ok=True)
    
    # 1. Charger les données
    print("📊 Chargement des données BTC/USDT...")
    data_manager = DataManager()
    data = data_manager.get_data()
    
    if data is None or data.empty:
        print("❌ Erreur lors du chargement des données")
        return
    
    print(f"✅ {len(data)} bougies chargées ({data.index[0].strftime('%Y-%m-%d')} → {data.index[-1].strftime('%Y-%m-%d')})")
    
    # 2. Lancer la stratégie optimisée
    print("🚀 Lancement de la stratégie straddle optimisée...")
    strategy = AdvancedStraddleStrategy()
    results = strategy.run_backtest(data)
    
    # 3. Analyser les résultats
    print("📊 Analyse des résultats...")
    print_detailed_results(results)
    
    # 4. Créer les visualisations
    print("🎨 Génération des graphiques...")
    create_results_visualization(results, data)
    
    # 5. Recommandations
    print("\n💡 RECOMMANDATIONS")
    print("="*50)
    
    if results['total_return'] > 0:
        print("✅ Stratégie profitable!")
        print("🎯 Points forts:")
        if results.get('win_rate', 0) > 50:
            print("   • Bon taux de réussite")
        if results['total_return'] > 10:
            print("   • Rendement attractif")
        
        print("🔧 Améliorations possibles:")
        print("   • Implémenter le hedging directionnel")
        print("   • Optimiser la gestion des positions")
        print("   • Utiliser des options réelles")
    else:
        print("⚠️ Stratégie non profitable sur cette période")
        print("🔧 Suggestions:")
        print("   • Ajuster le seuil de volatilité")
        print("   • Modifier les niveaux de TP/SL")
        print("   • Tester sur d'autres périodes")
    
    print("\n✅ Analyse terminée! Vérifiez les graphiques dans output/")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Interruption par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
