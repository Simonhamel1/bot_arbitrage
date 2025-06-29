# Backtesting Stratégie Straddle Optimisée avec Gestion Long/Short

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

from config import *
from src.data_manager import DataManager
from src.straddle_strategy import AdvancedStraddleStrategy

def create_results_visualization(results, data):
    """Crée des graphiques améliorés pour analyser les résultats avec focus sur PnL"""
    
    # Configuration pour 6 graphiques
    fig = plt.figure(figsize=(20, 16))
    
    # 1. Prix BTC avec trades et signaux
    ax1 = plt.subplot(3, 2, 1)
    ax1.plot(data.index, data['close'], 'k-', linewidth=1, alpha=0.8, label='Prix BTC')
    
    if 'trades' in results and len(results['trades']) > 0:
        trades_df = pd.DataFrame(results['trades'])
        
        # Signaux d'entrée et de sortie
        if 'entry_time' in trades_df.columns and 'entry_price' in trades_df.columns:
            entries = trades_df.drop_duplicates('entry_time')
            ax1.scatter(entries['entry_time'], entries['entry_price'], 
                       color='green', marker='^', s=60, label='Entrées', zorder=5)
        
        if 'exit_time' in trades_df.columns and 'exit_price' in trades_df.columns:
            exits = trades_df.drop_duplicates('exit_time')
            ax1.scatter(exits['exit_time'], exits['exit_price'], 
                       color='red', marker='v', s=60, label='Sorties', zorder=5)
    
    ax1.set_title('💰 Prix BTC/USDT avec Signaux de Trading', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Prix ($)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Évolution du capital avec drawdown
    ax2 = plt.subplot(3, 2, 2)
    
    if 'daily_pnl' in results and len(results['daily_pnl']) > 0:
        pnl_df = pd.DataFrame(results['daily_pnl'])
        
        if 'capital' in pnl_df.columns:
            capital_values = pnl_df['capital']
            ax2.plot(pnl_df.index, capital_values, 'darkgreen', linewidth=2, label='Capital Total')
            
            # Calcul et affichage du drawdown
            peak = capital_values.expanding().max()
            drawdown = (capital_values - peak) / peak * 100
            ax2_dd = ax2.twinx()
            ax2_dd.fill_between(pnl_df.index, drawdown, 0, alpha=0.3, color='red', label='Drawdown')
            ax2_dd.set_ylabel('Drawdown (%)', color='red')
            ax2_dd.set_ylim(drawdown.min() * 1.1, 5)
            
    else:
        # Évolution simple
        final_capital = results.get('final_capital', INITIAL_CAPITAL)
        ax2.plot([0, 1], [INITIAL_CAPITAL, final_capital], 
                'darkgreen', linewidth=3, label='Évolution Capital')
    
    ax2.axhline(y=INITIAL_CAPITAL, color='blue', linestyle='--', alpha=0.7, label='Capital Initial')
    ax2.set_title('📈 Évolution du Capital avec Drawdown', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Capital ($)')
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    
    # 3. Distribution des PnL par trade
    ax3 = plt.subplot(3, 2, 3)
    
    if 'trades' in results and len(results['trades']) > 0:
        trades_df = pd.DataFrame(results['trades'])
        
        # Chercher la colonne PnL appropriée
        pnl_col = None
        for col in ['pnl_pct', 'pnl', 'return_pct', 'profit_pct']:
            if col in trades_df.columns:
                pnl_col = col
                break
        
        if pnl_col:
            pnl_values = trades_df[pnl_col]
            
            # Histogramme des PnL
            ax3.hist(pnl_values, bins=30, alpha=0.7, color='steelblue', edgecolor='black')
            ax3.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Seuil de rentabilité')
            ax3.axvline(x=pnl_values.mean(), color='orange', linestyle='-', linewidth=2, 
                       label=f'PnL Moyen: {pnl_values.mean():.2f}%')
            
            # Statistiques
            win_trades = len(pnl_values[pnl_values > 0])
            total_trades = len(pnl_values)
            win_rate = (win_trades / total_trades) * 100 if total_trades > 0 else 0
            
            ax3.text(0.02, 0.98, f'Trades gagnants: {win_trades}/{total_trades}\nTaux réussite: {win_rate:.1f}%', 
                    transform=ax3.transAxes, verticalalignment='top', 
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    else:
        ax3.text(0.5, 0.5, 'Aucune donnée de trade disponible', 
                ha='center', va='center', transform=ax3.transAxes, fontsize=12)
    
    ax3.set_title('📊 Distribution des PnL par Trade', fontsize=14, fontweight='bold')
    ax3.set_xlabel('PnL (%)')
    ax3.set_ylabel('Fréquence')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. PnL cumulé au fil du temps
    ax4 = plt.subplot(3, 2, 4)
    
    if 'trades' in results and len(results['trades']) > 0:
        trades_df = pd.DataFrame(results['trades'])
        
        if pnl_col and 'exit_time' in trades_df.columns:
            trades_sorted = trades_df.sort_values('exit_time')
            cumulative_pnl = trades_sorted[pnl_col].cumsum()
            
            ax4.plot(trades_sorted['exit_time'], cumulative_pnl, 'purple', linewidth=2, 
                    label='PnL Cumulé')
            ax4.axhline(y=0, color='red', linestyle='--', alpha=0.7, label='Seuil de rentabilité')
            
            # Colorer les zones positives et négatives
            ax4.fill_between(trades_sorted['exit_time'], cumulative_pnl, 0, 
                           where=(cumulative_pnl >= 0), color='green', alpha=0.3, label='Profits')
            ax4.fill_between(trades_sorted['exit_time'], cumulative_pnl, 0, 
                           where=(cumulative_pnl < 0), color='red', alpha=0.3, label='Pertes')
    else:
        total_return = results.get('total_return', 0)
        ax4.bar(['Résultat Final'], [total_return], 
               color='green' if total_return > 0 else 'red', alpha=0.7)
    
    ax4.set_title('📈 PnL Cumulé dans le Temps', fontsize=14, fontweight='bold')
    ax4.set_ylabel('PnL Cumulé (%)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Métriques de performance principales
    ax5 = plt.subplot(3, 2, 5)
    
    metrics = {
        'Rendement Total (%)': results.get('total_return', 0),
        'Sharpe Ratio': results.get('sharpe_ratio', 0),
        'Max Drawdown (%)': results.get('max_drawdown', 0),
        'Win Rate (%)': results.get('win_rate', 0)
    }
    
    metric_names = list(metrics.keys())
    metric_values = list(metrics.values())
    colors = ['green' if v > 0 else 'red' for v in metric_values]
    
    bars = ax5.barh(metric_names, metric_values, color=colors, alpha=0.7)
    ax5.set_title('📊 Métriques de Performance Clés', fontsize=14, fontweight='bold')
    ax5.set_xlabel('Valeur')
    ax5.grid(True, alpha=0.3, axis='x')
    
    # Ajouter les valeurs sur les barres
    for bar, value in zip(bars, metric_values):
        ax5.text(bar.get_width() + 0.1 if value >= 0 else bar.get_width() - 0.1, 
                bar.get_y() + bar.get_height()/2, f'{value:.2f}', 
                ha='left' if value >= 0 else 'right', va='center', fontweight='bold')
    
    # 6. Volatilité et signaux
    ax6 = plt.subplot(3, 2, 6)
    
    if 'volatility' in data.columns:
        ax6.plot(data.index, data['volatility'], 'purple', alpha=0.8, label='Volatilité')
        volatility_threshold = np.percentile(data['volatility'], VOLATILITY_THRESHOLD)
        ax6.axhline(y=volatility_threshold, color='red', linestyle='--', 
                   label=f'Seuil {VOLATILITY_THRESHOLD}%: {volatility_threshold:.4f}')
        
        # Zones de trading
        ax6.fill_between(data.index, 0, data['volatility'], 
                        where=(data['volatility'] >= volatility_threshold), 
                        alpha=0.3, color='green', label='Zones de trading')
    else:
        # Calcul approximatif de la volatilité
        returns = data['close'].pct_change()
        volatility = returns.rolling(20).std() * 100
        ax6.plot(data.index, volatility, 'purple', alpha=0.8, label='Volatilité (approx)')
        vol_threshold = np.percentile(volatility.dropna(), VOLATILITY_THRESHOLD)
        ax6.axhline(y=vol_threshold, color='red', linestyle='--', 
                   label=f'Seuil {VOLATILITY_THRESHOLD}%')
    
    ax6.set_title('🌊 Volatilité et Zones de Trading', fontsize=14, fontweight='bold')
    ax6.set_ylabel('Volatilité')
    ax6.legend()
    ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    
    # Sauvegarder
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'output/straddle_results_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"📊 Graphiques sauvegardés: {filename}")
    
    plt.show()

def print_detailed_results(results):
    """Affiche les résultats de manière sécurisée"""
    print("\n" + "="*80)
    print("📊 RÉSULTATS DÉTAILLÉS - STRATÉGIE STRADDLE OPTIMISÉE")
    print("="*80)
    
    # Métriques de base
    print(f"💰 Capital Initial: ${INITIAL_CAPITAL:,.2f}")
    print(f"💰 Capital Final: ${results.get('final_capital', INITIAL_CAPITAL):,.2f}")
    
    total_return = results.get('total_return', 0)
    print(f"📈 Rendement Total: {total_return:.2f}%")
    
    gain_loss = results.get('final_capital', INITIAL_CAPITAL) - INITIAL_CAPITAL
    print(f"💵 Gain/Perte: ${gain_loss:,.2f}")
    
    # Statistiques de trading
    if 'trades' in results and len(results['trades']) > 0:
        print(f"\n🎯 STATISTIQUES DE TRADING")
        print(f"📊 Nombre de Trades: {len(results['trades'])}")
        
        # Métriques sûres
        safe_metrics = ['win_rate', 'avg_pnl', 'max_win', 'max_loss', 'sharpe_ratio', 'max_drawdown']
        for metric in safe_metrics:
            if metric in results and results[metric] is not None:
                value = results[metric]
                if metric == 'win_rate':
                    print(f"🎯 Taux de Réussite: {value:.1f}%")
                elif metric == 'avg_pnl':
                    print(f"💰 PnL Moyen: {value:.2f}%")
                elif metric == 'max_win':
                    print(f"🚀 Meilleur Trade: +{value:.2f}%")
                elif metric == 'max_loss':
                    print(f"💥 Pire Trade: {value:.2f}%")
                elif metric == 'sharpe_ratio':
                    print(f"📊 Ratio de Sharpe: {value:.2f}")
                elif metric == 'max_drawdown':
                    print(f"📉 Drawdown Max: {value:.2f}%")
    else:
        print(f"\n⚠️ Aucun trade détecté dans les résultats")
    
    print("\n" + "="*80)

def main():
    """Fonction principale"""
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
    signals = strategy.generate_signals(data)
    results = strategy.backtest(signals)
    
    # 3. Analyser les résultats
    print("📊 Analyse des résultats...")
    print_detailed_results(results)
    
    # 4. Créer les visualisations
    print("📈 Création des graphiques...")
    create_results_visualization(results, data)
    
    # 5. Conclusion
    total_return = results.get('total_return', 0)
    if total_return > 5:
        print("🎉 Excellente performance! Stratégie très profitable.")
    elif total_return > 0:
        print("✅ Performance positive. Stratégie rentable.")
    else:
        print("⚠️ Performance négative sur cette période.")
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
