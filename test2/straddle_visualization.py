# Fonctions de visualisation pour la stratégie de straddle
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime

def plot_straddle_strategy(df, signals, equity_curve=None, trades=None):
    """
    Affiche les graphiques pour la stratégie de straddle
    
    Args:
        df (pandas.DataFrame): DataFrame avec les données OHLCV
        signals (pandas.DataFrame): DataFrame avec les signaux générés
        equity_curve (pandas.Series, optional): Courbe d'équité
        trades (pandas.DataFrame, optional): Détails des trades
    """
    fig = plt.figure(figsize=(14, 12))
    
    # Graphique des prix avec bandes de volatilité
    ax1 = plt.subplot(4, 1, 1)
    ax1.plot(df.index, df['close'], label='Prix')
    
    # Ajouter les signaux d'entrée
    if signals is not None:
        entry_points = signals[signals['straddle_signal'] == 1].index
        for point in entry_points:
            if point in df.index:
                ax1.axvline(x=point, color='purple', linestyle='--', alpha=0.7)
    
    # Ajouter les trades si disponibles
    if trades is not None and not trades.empty:
        for _, trade in trades.iterrows():
            if trade['type'] == 'long':
                ax1.plot(trade['entry_time'], trade['entry_price'], '^', color='green', markersize=8)
                ax1.plot(trade['exit_time'], trade['exit_price'], 'v', color='red', markersize=8)
            elif trade['type'] == 'short':
                ax1.plot(trade['entry_time'], trade['entry_price'], 'v', color='red', markersize=8)
                ax1.plot(trade['exit_time'], trade['exit_price'], '^', color='green', markersize=8)
    
    ax1.set_title('Prix et Signaux de Trading')
    ax1.legend()
    
    # Graphique de la volatilité
    ax2 = plt.subplot(4, 1, 2, sharex=ax1)
    if 'volatility' in df.columns:
        ax2.plot(df.index, df['volatility'], label='Volatilité')
        ax2.axhline(y=df['volatility'].quantile(0.75), color='red', linestyle='--', 
                    label='Seuil 75%')
    if 'atr_pct' in df.columns:
        ax2.plot(df.index, df['atr_pct'], label='ATR (%)', color='orange')
    
    ax2.set_title('Indicateurs de Volatilité')
    ax2.legend()
    
    # Graphique des signaux
    ax3 = plt.subplot(4, 1, 3, sharex=ax1)
    if signals is not None:
        ax3.plot(signals.index, signals['long_signal'], label='Signal Long', color='green')
        ax3.plot(signals.index, -signals['short_signal'], label='Signal Short', color='red')
    
    ax3.set_title('Signaux de Trading')
    ax3.legend()
    
    # Graphique de la courbe d'équité
    ax4 = plt.subplot(4, 1, 4, sharex=ax1)
    if equity_curve is not None:
        ax4.plot(equity_curve.index, equity_curve, label='Équité')
    
    ax4.set_title('Courbe d\'Équité')
    ax4.legend()
    
    # Formater l'axe des x pour les dates
    for ax in [ax1, ax2, ax3, ax4]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    
    plt.tight_layout()
    plt.xticks(rotation=45)
    
    return fig

def plot_straddle_performance(trades_df, equity_curve):
    """
    Affiche les graphiques de performance pour la stratégie de straddle
    
    Args:
        trades_df (pandas.DataFrame): DataFrame avec les détails des trades
        equity_curve (pandas.Series): Courbe d'équité
    """
    if trades_df.empty:
        print("Pas de trades à analyser")
        return
    
    fig = plt.figure(figsize=(14, 12))
    
    # Graphique de la courbe d'équité
    ax1 = plt.subplot(3, 1, 1)
    ax1.plot(equity_curve.index, equity_curve, label='Équité')
    
    # Calculer le drawdown
    peak = equity_curve.expanding().max()
    drawdown = (equity_curve / peak - 1) * 100
    
    ax1.set_title('Courbe d\'Équité')
    ax1.legend()
    
    # Graphique du drawdown
    ax2 = plt.subplot(3, 1, 2, sharex=ax1)
    ax2.fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.3)
    ax2.set_title('Drawdown (%)')
    ax2.set_ylim(min(drawdown) * 1.1, 0)
    
    # Graphique des profits/pertes par trade
    ax3 = plt.subplot(3, 1, 3)
    profits = trades_df['pnl_pct'].values
    colors = ['green' if p > 0 else 'red' for p in profits]
    
    ax3.bar(range(len(profits)), profits, color=colors)
    ax3.axhline(y=0, color='black', linestyle='-')
    ax3.set_title('P&L par Trade (%)')
    ax3.set_xlabel('Numéro de Trade')
    
    plt.tight_layout()
    
    return fig

def plot_trades_distribution(trades_df):
    """
    Affiche la distribution des trades
    
    Args:
        trades_df (pandas.DataFrame): DataFrame avec les détails des trades
    """
    if trades_df.empty:
        print("Pas de trades à analyser")
        return
    
    fig = plt.figure(figsize=(14, 10))
    
    # Histogramme des profits/pertes
    ax1 = plt.subplot(2, 2, 1)
    ax1.hist(trades_df['pnl_pct'], bins=20, color='blue', alpha=0.7)
    ax1.axvline(x=0, color='red', linestyle='--')
    ax1.set_title('Distribution des Profits/Pertes (%)')
    
    # Répartition par type de trade
    ax2 = plt.subplot(2, 2, 2)
    trade_counts = trades_df['type'].value_counts()
    ax2.pie(trade_counts, labels=trade_counts.index, autopct='%1.1f%%', 
            colors=['green', 'red'])
    ax2.set_title('Répartition des Types de Trades')
    
    # Répartition par raison de sortie
    ax3 = plt.subplot(2, 2, 3)
    reason_counts = trades_df['exit_reason'].value_counts()
    ax3.pie(reason_counts, labels=reason_counts.index, autopct='%1.1f%%', 
           colors=['lightgreen', 'lightcoral', 'lightskyblue', 'gold'])
    ax3.set_title('Répartition des Raisons de Sortie')
    
    # Statistiques des trades
    ax4 = plt.subplot(2, 2, 4)
    ax4.axis('off')
    
    win_trades = trades_df[trades_df['pnl_pct'] > 0]
    loss_trades = trades_df[trades_df['pnl_pct'] <= 0]
    
    stats_text = [
        f"Nombre total de trades: {len(trades_df)}",
        f"Trades gagnants: {len(win_trades)} ({len(win_trades)/len(trades_df)*100:.1f}%)",
        f"Trades perdants: {len(loss_trades)} ({len(loss_trades)/len(trades_df)*100:.1f}%)",
        f"Profit moyen: {win_trades['pnl_pct'].mean():.2f}%",
        f"Perte moyenne: {loss_trades['pnl_pct'].mean():.2f}%",
        f"Profit total: {trades_df['pnl_pct'].sum():.2f}%",
        f"Profit moyen par trade: {trades_df['pnl_pct'].mean():.2f}%",
        f"Meilleur trade: {trades_df['pnl_pct'].max():.2f}%",
        f"Pire trade: {trades_df['pnl_pct'].min():.2f}%"
    ]
    
    ax4.text(0.1, 0.5, '\n'.join(stats_text), fontsize=12)
    ax4.set_title('Statistiques des Trades')
    
    plt.tight_layout()
    
    return fig

def save_strategy_analysis(df, signals, equity_curve, trades, filename_prefix='straddle_analysis'):
    """
    Sauvegarde l'analyse complète de la stratégie en fichiers PNG
    
    Args:
        df (pandas.DataFrame): DataFrame avec les données OHLCV
        signals (pandas.DataFrame): DataFrame avec les signaux générés
        equity_curve (pandas.Series): Courbe d'équité
        trades (pandas.DataFrame): Détails des trades
        filename_prefix (str): Préfixe pour les noms de fichiers
    """
    # Créer le dossier output s'il n'existe pas
    import os
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Figure de la stratégie
    strategy_fig = plot_straddle_strategy(df, signals, equity_curve, trades)
    strategy_fig.savefig(os.path.join(output_dir, f"{filename_prefix}_strategy_{timestamp}.png"))
    
    if not trades.empty:
        # Figure de performance
        performance_fig = plot_straddle_performance(trades, equity_curve)
        performance_fig.savefig(os.path.join(output_dir, f"{filename_prefix}_performance_{timestamp}.png"))
          # Figure de distribution des trades
        distribution_fig = plot_trades_distribution(trades)
        distribution_fig.savefig(os.path.join(output_dir, f"{filename_prefix}_distribution_{timestamp}.png"))
    
    # Sauvegarder les données
    if df is not None:
        df.to_csv(os.path.join(output_dir, f"{filename_prefix}_data_{timestamp}.csv"))
    if signals is not None:
        signals.to_csv(os.path.join(output_dir, f"{filename_prefix}_signals_{timestamp}.csv"))
    if trades is not None and not trades.empty:
        trades.to_csv(os.path.join(output_dir, f"{filename_prefix}_trades_{timestamp}.csv"))
    if equity_curve is not None:
        equity_curve.to_csv(os.path.join(output_dir, f"{filename_prefix}_equity_{timestamp}.csv"))
    
    print(f"Analyse sauvegardée dans le dossier 'output' avec préfixe {filename_prefix}_{timestamp}")
