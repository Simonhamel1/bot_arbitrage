# Script pour exécuter la stratégie de straddle en continu
import time
import traceback
import pandas as pd
import numpy as np
from datetime import datetime

from config import (EXCHANGE_ID, ENABLE_RATE_LIMIT, SYMBOL, TIMEFRAME, DATA_LIMIT,
                   VOLATILITY_PERIOD, ENTRY_VOLATILITY_PERCENTILE)
from data_fetcher import initialize_exchange, fetch_ohlcv, prepare_data_for_straddle, fetch_ticker
from straddle_strategy import calculate_straddle_levels, is_volatility_high
from straddle_trader import StraddleTrader
from straddle_visualization import save_strategy_analysis

def run_strategy_loop(interval_seconds=300, max_iterations=None, dry_run=True):
    """
    Exécute la stratégie de straddle en boucle
    
    Args:
        interval_seconds (int): Intervalle d'exécution en secondes
        max_iterations (int, optional): Nombre maximum d'itérations (None pour infini)
        dry_run (bool): Si True, ne pas exécuter réellement les ordres
    """
    print(f"Démarrage de la stratégie de straddle en continu sur {SYMBOL}")
    print(f"Mode: {'Simulation (dry run)' if dry_run else 'Trading réel'}")
    print(f"Intervalle: {interval_seconds} secondes")
    
    # Initialisation de l'échange
    exchange = initialize_exchange(EXCHANGE_ID, {'enableRateLimit': ENABLE_RATE_LIMIT})
    
    # Initialisation du trader
    trader = StraddleTrader(exchange, SYMBOL, dry_run=dry_run)
    
    # Historique des données
    all_data = pd.DataFrame()
    signals_history = []
    
    iteration = 0
    
    try:
        while max_iterations is None or iteration < max_iterations:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{current_time}] Itération {iteration + 1}")
            
            try:
                # Récupération des données historiques
                print(f"Récupération des données pour {SYMBOL}...")
                df = fetch_ohlcv(exchange, SYMBOL, timeframe=TIMEFRAME, limit=DATA_LIMIT)
                
                # Préparation des données
                df = prepare_data_for_straddle(df)
                
                # Dernières valeurs
                last_row = df.iloc[-1]
                current_price = last_row['close']
                current_volatility = last_row['volatility']
                current_atr = last_row['atr']
                
                print(f"Prix actuel: {current_price:.2f}")
                print(f"Volatilité: {current_volatility:.4f}")
                print(f"ATR: {current_atr:.4f}")
                
                # Vérifier si la volatilité est élevée
                high_vol = is_volatility_high(
                    df['volatility'].values, 
                    len(df) - 1, 
                    ENTRY_VOLATILITY_PERCENTILE, 
                    VOLATILITY_PERIOD * 5
                )
                
                # Vérifier les positions existantes
                current_time = datetime.now()
                trader.check_positions(current_price, current_time)
                
                # Décision de trading
                if high_vol:
                    print("Volatilité élevée détectée!")
                    
                    # Calculer les niveaux de straddle
                    levels = calculate_straddle_levels(current_price, current_atr)
                    
                    long_tp = levels['long']['take_profit']
                    long_sl = levels['long']['stop_loss']
                    short_tp = levels['short']['take_profit']
                    short_sl = levels['short']['stop_loss']
                    
                    print(f"Niveaux Long: Entrée={current_price:.2f}, TP={long_tp:.2f}, SL={long_sl:.2f}")
                    print(f"Niveaux Short: Entrée={current_price:.2f}, TP={short_tp:.2f}, SL={short_sl:.2f}")
                    
                    # Si aucune position n'est ouverte, ouvrir un straddle
                    if trader.long_position is None and trader.short_position is None:
                        print("Ouverture d'une position straddle...")
                        long_success, short_success = trader.open_straddle(current_price, current_volatility)
                        
                        if long_success and short_success:
                            print("Position straddle ouverte avec succès!")
                        elif long_success:
                            print("Seulement la position longue a été ouverte.")
                        elif short_success:
                            print("Seulement la position courte a été ouverte.")
                        else:
                            print("Échec de l'ouverture de la position straddle.")
                    else:
                        print("Des positions sont déjà ouvertes, pas de nouveau straddle.")
                else:
                    print("Volatilité normale, pas de signal d'entrée.")
                
                # Ajouter les données à l'historique
                all_data = pd.concat([all_data, df.tail(1)])
                
                # Enregistrer le statut actuel
                signal_entry = {
                    'timestamp': current_time,
                    'price': current_price,
                    'volatility': current_volatility,
                    'atr': current_atr,
                    'high_volatility': high_vol,
                    'long_position': trader.long_position is not None,
                    'short_position': trader.short_position is not None
                }
                signals_history.append(signal_entry)
                
                # Performance
                if iteration % 10 == 0:
                    performance = trader.get_performance_summary()
                    print("\nPerformance:")
                    print(f"Total des trades: {performance['total_trades']}")
                    print(f"Taux de réussite: {performance['win_rate']:.2%}")
                    print(f"Profit moyen: {performance['avg_profit']:.2f}%")
                    print(f"Perte moyenne: {performance['avg_loss']:.2f}%")
                    print(f"Total P&L: {performance['total_pnl_pct']:.2f}%")
                
                # Sauvegarder les trades périodiquement
                if iteration % 20 == 0 and trader.trades_history:
                    trader.save_trades_to_csv()
                
                iteration += 1
                
                if max_iterations is None or iteration < max_iterations:
                    print(f"En attente pour {interval_seconds} secondes avant la prochaine exécution...")
                    time.sleep(interval_seconds)
            
            except Exception as e:
                print(f"Erreur pendant l'itération {iteration}: {e}")
                traceback.print_exc()
                time.sleep(30)  # Attendre un peu avant de réessayer
    
    except KeyboardInterrupt:
        print("\nInterruption par l'utilisateur. Arrêt propre...")
    
    finally:
        # Fermeture des positions ouvertes
        current_price = fetch_ticker(exchange, SYMBOL)['last']
        
        if trader.long_position is not None:
            print("Fermeture de la position longue...")
            trader.close_long_position(current_price, 'END_OF_EXECUTION')
        
        if trader.short_position is not None:
            print("Fermeture de la position courte...")
            trader.close_short_position(current_price, 'END_OF_EXECUTION')
        
        # Sauvegarde des trades
        trader.save_trades_to_csv()
        
        # Sauvegarde des signaux
        signals_df = pd.DataFrame(signals_history)
        if not signals_df.empty:
            signals_df.to_csv('straddle_signals_history.csv', index=False)
        
        print(f"Stratégie arrêtée après {iteration} itérations.")
        
        # Afficher le résumé final
        performance = trader.get_performance_summary()
        print("\nRésumé final:")
        print(f"Total des trades: {performance['total_trades']}")
        print(f"Taux de réussite: {performance['win_rate']:.2%}")
        print(f"Profit moyen: {performance['avg_profit']:.2f}%")
        print(f"Perte moyenne: {performance['avg_loss']:.2f}%")
        print(f"Ratio profit/perte: {performance['profit_factor']:.2f}")
        print(f"Total P&L: {performance['total_pnl_pct']:.2f}%")

if __name__ == '__main__':
    run_strategy_loop(interval_seconds=300, dry_run=True)
