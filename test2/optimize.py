# Script d'optimisation pour trouver les meilleurs paramètres de la stratégie
import numpy as np
import pandas as pd
import itertools
from multiprocessing import Pool, cpu_count

from data_fetcher import initialize_exchange, fetch_ohlcv
from model_builder import build_pair_regression_model, calculate_spread_statistics
from signal_generator import generate_trading_signals, calculate_strategy_returns
from config import EXCHANGE_ID, ENABLE_RATE_LIMIT, SYMBOLS

def run_strategy_with_params(params):
    """
    Exécute la stratégie avec un ensemble de paramètres spécifiques
    
    Args:
        params (tuple): Paramètres (threshold_multiplier, close_at_mean_ratio, use_stop_loss, stop_loss_multiplier)
        
    Returns:
        dict: Résultats de la stratégie
    """
    threshold_multiplier, close_at_mean_ratio, stop_loss_multiplier = params
    
    # Configuration temporaire des paramètres
    import config
    config.THRESHOLD_MULTIPLIER = threshold_multiplier
    config.CLOSE_AT_MEAN_RATIO = close_at_mean_ratio
    config.STOP_LOSS_MULTIPLIER = stop_loss_multiplier
    config.USE_STOP_LOSS = True if stop_loss_multiplier > 0 else False
    
    try:
        # Initialisation de l'échange
        exchange = initialize_exchange(EXCHANGE_ID, {'enableRateLimit': ENABLE_RATE_LIMIT})
        
        # Récupération des symboles
        symbol1 = SYMBOLS['asset1']
        symbol2 = SYMBOLS['asset2']
        
        # Récupération des données historiques
        df1 = fetch_ohlcv(exchange, symbol1)
        df2 = fetch_ohlcv(exchange, symbol2)
        
        # Extraction des prix de clôture
        price1 = df1['close'].values
        price2 = df2['close'].values
        
        # Construction du modèle de régression et calcul du spread
        beta, alpha, spread = build_pair_regression_model(price1, price2)
        
        # Calcul des statistiques du spread
        mu, sigma, upper_threshold, lower_threshold = calculate_spread_statistics(spread)
        
        # Génération des signaux de trading
        signals = generate_trading_signals(spread, mu, upper_threshold, lower_threshold)
        
        # Calcul des rendements
        returns, cumulative_returns = calculate_strategy_returns(signals, spread)
        
        # Calcul des métriques de performance
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252 * 24 * 60) if np.std(returns) > 0 else 0
        max_drawdown = np.max(np.maximum.accumulate(cumulative_returns) - cumulative_returns)
        total_return = cumulative_returns[-1] if len(cumulative_returns) > 0 else 0
        
        # Nombre de trades
        trades = np.sum(np.abs(np.diff(signals) != 0))
        
        return {
            'threshold_multiplier': threshold_multiplier,
            'close_at_mean_ratio': close_at_mean_ratio,
            'stop_loss_multiplier': stop_loss_multiplier,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_return': total_return,
            'trades': trades
        }
    
    except Exception as e:
        print(f"Erreur avec paramètres {params}: {e}")
        return {
            'threshold_multiplier': threshold_multiplier,
            'close_at_mean_ratio': close_at_mean_ratio,
            'stop_loss_multiplier': stop_loss_multiplier,
            'sharpe_ratio': -999,
            'max_drawdown': 999,
            'total_return': -999,
            'trades': 0
        }

def optimize_strategy():
    """
    Optimise les paramètres de la stratégie par grid search
    """
    print("Démarrage de l'optimisation des paramètres...")
    
    # Définition des paramètres à tester
    threshold_multipliers = [1.5, 2.0, 2.5, 3.0]
    close_at_mean_ratios = [0.0, 0.3, 0.5, 0.7]
    stop_loss_multipliers = [0, 2.0, 3.0, 4.0]  # 0 = pas de stop-loss
    
    # Génération de toutes les combinaisons de paramètres
    param_combinations = list(itertools.product(threshold_multipliers, close_at_mean_ratios, stop_loss_multipliers))
    
    print(f"Test de {len(param_combinations)} combinaisons de paramètres...")
    
    # Utilisation de multiprocessing pour accélérer l'optimisation
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(run_strategy_with_params, param_combinations)
    
    # Conversion des résultats en DataFrame
    results_df = pd.DataFrame(results)
    
    # Tri par ratio de Sharpe décroissant
    sorted_results = results_df.sort_values('sharpe_ratio', ascending=False)
    
    print("\nMeilleurs paramètres par ratio de Sharpe:")
    print(sorted_results.head(10))
    
    # Tri par rendement total décroissant
    sorted_by_return = results_df.sort_values('total_return', ascending=False)
    
    print("\nMeilleurs paramètres par rendement total:")
    print(sorted_by_return.head(10))
    
    # Meilleurs paramètres
    best_params = sorted_results.iloc[0]
    
    print("\nMeilleurs paramètres:")
    print(f"THRESHOLD_MULTIPLIER = {best_params['threshold_multiplier']}")
    print(f"CLOSE_AT_MEAN_RATIO = {best_params['close_at_mean_ratio']}")
    print(f"USE_STOP_LOSS = {best_params['stop_loss_multiplier'] > 0}")
    print(f"STOP_LOSS_MULTIPLIER = {best_params['stop_loss_multiplier']}")
    print(f"Ratio de Sharpe: {best_params['sharpe_ratio']:.4f}")
    print(f"Rendement total: {best_params['total_return']:.4f}")
    print(f"Drawdown maximum: {best_params['max_drawdown']:.4f}")
    print(f"Nombre de trades: {best_params['trades']}")
    
    # Sauvegarde des résultats
    sorted_results.to_csv('optimization_results.csv', index=False)
    print("Résultats sauvegardés dans 'optimization_results.csv'")

if __name__ == '__main__':
    optimize_strategy()
