# Script d'analyse de performance de la stratégie
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from config import EXCHANGE_ID, ENABLE_RATE_LIMIT, SYMBOLS
from data_fetcher import initialize_exchange, fetch_ohlcv
from model_builder import build_pair_regression_model, calculate_spread_statistics
from signal_generator import generate_trading_signals, calculate_strategy_returns

def analyze_performance():
    """
    Analyse détaillée de la performance de la stratégie
    """
    print("Analyse de performance de la stratégie...")
    
    # Initialisation de l'échange
    exchange = initialize_exchange(EXCHANGE_ID, {'enableRateLimit': ENABLE_RATE_LIMIT})
    
    # Récupération des symboles
    symbol1 = SYMBOLS['asset1']
    symbol2 = SYMBOLS['asset2']
    
    # Récupération des données historiques
    print(f"Récupération des données pour {symbol1} et {symbol2}...")
    df1 = fetch_ohlcv(exchange, symbol1)
    df2 = fetch_ohlcv(exchange, symbol2)
    
    # Extraction des prix de clôture
    price1 = df1['close'].values
    price2 = df2['close'].values
    
    # Construction du modèle de régression et calcul du spread
    beta, alpha, spread = build_pair_regression_model(price1, price2)
    print(f"Modèle: {symbol1} = {beta:.4f} * {symbol2} + {alpha:.4f}")
    
    # Calcul des statistiques du spread
    mu, sigma, upper_threshold, lower_threshold = calculate_spread_statistics(spread)
    
    # Génération des signaux de trading
    signals = generate_trading_signals(spread, mu, upper_threshold, lower_threshold)
    
    # Calcul des rendements
    returns, cumulative_returns = calculate_strategy_returns(signals, spread)
    
    # Création d'un DataFrame pour l'analyse
    analysis_df = pd.DataFrame({
        'timestamp': df1['timestamp'][1:],
        'price1': price1[1:],
        'price2': price2[1:],
        'spread': spread[1:],
        'signal': signals[1:],
        'return': returns,
        'cumulative_return': cumulative_returns
    })
    
    # Détection des trades (changements de signal)
    analysis_df['trade'] = analysis_df['signal'].diff() != 0
    
    # Statistiques des trades
    n_trades = analysis_df['trade'].sum()
    profitable_trades = ((analysis_df['trade'] & (analysis_df['return'] > 0)).sum())
    profit_rate = profitable_trades / n_trades if n_trades > 0 else 0
    
    # Statistiques de performance
    total_return = cumulative_returns[-1] if len(cumulative_returns) > 0 else 0
    annualized_return = (1 + total_return) ** (365.25 * 24 * 60 / len(returns)) - 1
    volatility = np.std(returns) * np.sqrt(365.25 * 24 * 60)
    sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(365.25 * 24 * 60) if np.std(returns) > 0 else 0
    
    # Drawdown
    max_drawdown = np.max(np.maximum.accumulate(cumulative_returns) - cumulative_returns)
    
    # Affichage des statistiques
    print("\nStatistiques de performance:")
    print(f"Période analysée: {analysis_df['timestamp'].iloc[0]} à {analysis_df['timestamp'].iloc[-1]}")
    print(f"Nombre de trades: {n_trades}")
    print(f"Taux de trades profitables: {profit_rate:.2%}")
    print(f"Rendement total: {total_return:.2%}")
    print(f"Rendement annualisé: {annualized_return:.2%}")
    print(f"Volatilité annualisée: {volatility:.2%}")
    print(f"Ratio de Sharpe: {sharpe_ratio:.4f}")
    print(f"Drawdown maximum: {max_drawdown:.2%}")
    
    # Visualisation avancée
    plt.figure(figsize=(14, 10))
    
    # Graphique des prix
    plt.subplot(4, 1, 1)
    plt.plot(analysis_df['timestamp'], analysis_df['price1'], label=symbol1)
    plt.plot(analysis_df['timestamp'], analysis_df['price2'], label=symbol2)
    plt.title('Prix des actifs')
    plt.legend()
    
    # Graphique du spread avec seuils
    plt.subplot(4, 1, 2)
    plt.plot(analysis_df['timestamp'], analysis_df['spread'], label='Spread')
    plt.axhline(mu, color='black', linestyle='--', label='Moyenne')
    plt.axhline(upper_threshold, color='red', linestyle='--', label='Seuil supérieur')
    plt.axhline(lower_threshold, color='green', linestyle='--', label='Seuil inférieur')
    plt.title('Spread et seuils')
    plt.legend()
    
    # Graphique des signaux
    plt.subplot(4, 1, 3)
    plt.plot(analysis_df['timestamp'], analysis_df['signal'])
    plt.title('Signaux de trading (1: long, -1: short, 0: neutre)')
    
    # Graphique des rendements cumulés
    plt.subplot(4, 1, 4)
    plt.plot(analysis_df['timestamp'], analysis_df['cumulative_return'])
    plt.title(f'Rendement cumulé (total: {total_return:.2%})')
    
    plt.tight_layout()
    
    # Sauvegarde du graphique
    filename = f"performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(filename)
    plt.show()
    print(f"Graphique sauvegardé dans {filename}")
    
    # Sauvegarde des données d'analyse
    analysis_df.to_csv(f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", index=False)

if __name__ == '__main__':
    analyze_performance()
