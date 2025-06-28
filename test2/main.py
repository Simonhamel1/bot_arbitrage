# Script principal pour la stratégie de straddle

import time
import pandas as pd
import numpy as np
import talib
from datetime import datetime

from config import (EXCHANGE_ID, ENABLE_RATE_LIMIT, SYMBOL, TIMEFRAME, DATA_LIMIT,
                  VOLATILITY_PERIOD, ENTRY_VOLATILITY_PERCENTILE)
from data_fetcher import initialize_exchange, fetch_ohlcv, prepare_data_for_straddle
from straddle_strategy import generate_straddle_signals, backtest_straddle_strategy
from straddle_visualization import plot_straddle_strategy, save_strategy_analysis

def main():
    """
    Fonction principale qui exécute la stratégie de straddle
    """
    print("Démarrage de la stratégie de straddle (strangle)...")
    
    # Initialisation de l'échange
    print(f"Connexion à l'échange {EXCHANGE_ID}...")
    exchange = initialize_exchange(EXCHANGE_ID, {'enableRateLimit': ENABLE_RATE_LIMIT})
    
    # Récupération des données historiques
    print(f"Récupération des données pour {SYMBOL} sur {TIMEFRAME}...")
    df = fetch_ohlcv(exchange, SYMBOL, timeframe=TIMEFRAME, limit=DATA_LIMIT)
    
    # Préparation des données
    print("Préparation des données et calcul des indicateurs...")
    df = prepare_data_for_straddle(df)
    
    # Génération des signaux de trading
    print("Génération des signaux de trading...")
    signals = generate_straddle_signals(
        df,
        volatility_col='volatility',
        price_col='close',
        entry_percentile=ENTRY_VOLATILITY_PERCENTILE,
        volatility_lookback=VOLATILITY_PERIOD * 5
    )
    
    # Backtesting de la stratégie
    print("Backtesting de la stratégie...")
    equity_curve, trades = backtest_straddle_strategy(signals)
    
    # Affichage des performances
    if len(trades) > 0:
        print("\nRésultats du backtest:")
        print(f"Nombre de trades: {len(trades)}")
        
        win_trades = trades[trades['pnl_pct'] > 0]
        loss_trades = trades[trades['pnl_pct'] <= 0]
        
        win_rate = len(win_trades) / len(trades) if len(trades) > 0 else 0
        print(f"Taux de réussite: {win_rate:.2%}")
        
        avg_win = win_trades['pnl_pct'].mean() if len(win_trades) > 0 else 0
        avg_loss = loss_trades['pnl_pct'].mean() if len(loss_trades) > 0 else 0
        print(f"Gain moyen: {avg_win:.2f}%")
        print(f"Perte moyenne: {avg_loss:.2f}%")
        
        total_return = equity_curve.iloc[-1] / equity_curve.iloc[0] - 1
        print(f"Rendement total: {total_return:.2%}")
        
        # Calcul du drawdown maximum
        peak = equity_curve.expanding().max()
        drawdown = (equity_curve / peak - 1)
        max_drawdown = drawdown.min()
        print(f"Drawdown maximum: {max_drawdown:.2%}")
        
        # Ratio de Sharpe annualisé (en supposant que les rendements sont quotidiens)
        returns = equity_curve.pct_change().dropna()
        sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std() if returns.std() > 0 else 0
        print(f"Ratio de Sharpe: {sharpe_ratio:.2f}")
    else:
        print("Aucun trade n'a été généré pendant le backtest.")
    
    # Visualisation des résultats
    print("Création des graphiques...")
    fig = plot_straddle_strategy(df, signals, equity_curve, trades)
    
    # Sauvegarde de l'analyse
    print("Sauvegarde de l'analyse...")
    save_strategy_analysis(df, signals, equity_curve, trades)
    
    print("Analyse terminée et sauvegardée. Affichage des graphiques...")
    fig.tight_layout()
    fig.show()
    
if __name__ == '__main__':
    main()
