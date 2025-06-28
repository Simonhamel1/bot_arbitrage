# Visualisation simple pour la stratégie straddle

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def create_simple_charts(df, results):
    """
    Crée 3 graphiques simples
    
    Args:
        df: DataFrame avec les données et signaux
        results: Résultats du backtest
    """
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # Graphique 1: Prix avec signaux
    axes[0].plot(df.index, df['close'], 'k-', linewidth=1, label='Prix BTC/USDT')
    
    # Marquer les signaux
    signals = df[df['signal'] == 1]
    if not signals.empty:
        axes[0].scatter(signals.index, signals['close'], 
                       color='red', marker='^', s=50, label='Signaux Straddle')
    
    axes[0].set_title('Prix BTC/USDT avec Signaux de Straddle')
    axes[0].set_ylabel('Prix ($)')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Graphique 2: Courbe d'équité
    equity = results['equity']
    axes[1].plot(equity.index, equity.values, 'b-', linewidth=2, label='Capital')
    axes[1].axhline(y=equity.iloc[0], color='gray', linestyle='--', alpha=0.5, label='Capital Initial')
    
    axes[1].set_title('Évolution du Capital')
    axes[1].set_ylabel('Capital ($)')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    # Graphique 3: Volatilité
    axes[2].plot(df.index, df['vol_percentile'], 'purple', linewidth=1, label='Volatilité (percentile)')
    axes[2].axhline(y=75, color='red', linestyle='--', label='Seuil (75e percentile)')
    
    # Zones de signaux
    if not signals.empty:
        axes[2].scatter(signals.index, signals['vol_percentile'], 
                       color='red', marker='o', s=30, label='Signaux')
    
    axes[2].set_title('Analyse de la Volatilité')
    axes[2].set_ylabel('Percentile de Volatilité')
    axes[2].set_xlabel('Date')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Sauvegarder
    plt.savefig('output/straddle_analysis.png', dpi=300, bbox_inches='tight')
    print("📊 Graphiques sauvegardés: output/straddle_analysis.png")
    
    plt.show()
    return fig

def print_simple_results(results):
    """
    Affiche les résultats de manière simple
    
    Args:
        results: Résultats du backtest
    """
    print("\n" + "="*60)
    print("📊 RÉSULTATS DU BACKTEST STRADDLE BTC")
    print("="*60)
    
    print(f"💰 Capital Initial: ${results['equity'].iloc[0]:,.2f}")
    print(f"💰 Capital Final: ${results['final_capital']:,.2f}")
    print(f"📈 Rendement Total: {results['total_return']:.2f}%")
    
    if not results['trades'].empty:
        trades = results['trades']
        winning_trades = len(trades[trades['pnl_pct'] > 0])
        total_trades = len(trades)
        win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0
        
        print(f"\n🔄 STATISTIQUES DE TRADING")
        print(f"📊 Nombre de Trades: {total_trades}")
        print(f"🏆 Trades Gagnants: {winning_trades}")
        print(f"📉 Trades Perdants: {total_trades - winning_trades}")
        print(f"🎯 Taux de Réussite: {win_rate:.1f}%")
        print(f"💰 Profit Moyen: {trades['pnl_pct'].mean():.2f}%")
        
        # Best et worst trade
        best_trade = trades['pnl_pct'].max()
        worst_trade = trades['pnl_pct'].min()
        print(f"🚀 Meilleur Trade: +{best_trade:.2f}%")
        print(f"💥 Pire Trade: {worst_trade:.2f}%")
    
    print("="*60)
