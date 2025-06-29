# Moteur de backtesting avancé pour la stratégie de straddle

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from config import *
from data_manager import DataManager
from straddle_strategy import StraddleStrategy

class StraddleBacktester:
    """Moteur de backtesting pour la stratégie de straddle"""
    
    def __init__(self, initial_capital=INITIAL_CAPITAL):
        """
        Initialise le backtester
        
        Args:
            initial_capital (float): Capital initial
        """
        self.initial_capital = initial_capital
        self.data_manager = DataManager()
        self.strategy = StraddleStrategy()
        self.reset_backtest()
    
    def reset_backtest(self):
        """Remet à zéro l'état du backtest"""
        self.capital = self.initial_capital
        self.equity_curve = [self.initial_capital]
        self.timestamps = []
        self.trade_log = []
        self.daily_returns = []
        self.strategy.positions = []
        self.strategy.closed_positions = []
        
    def run_backtest(self, df=None, start_date=None, end_date=None):
        """
        Lance le backtesting sur une période donnée
        
        Args:
            df (pandas.DataFrame): Données à utiliser (optionnel)
            start_date (str): Date de début
            end_date (str): Date de fin
            
        Returns:
            dict: Résultats du backtest
        """
        print("🚀 Démarrage du backtesting de la stratégie straddle...")
        
        # Récupération des données si pas fournies
        if df is None:
            print("📊 Récupération des données historiques...")
            df = self.data_manager.fetch_historical_data(
                start_date=start_date or BACKTEST_START_DATE,
                end_date=end_date or BACKTEST_END_DATE
            )
            
            if df.empty:
                print("❌ Aucune donnée récupérée")
                return None
            
            print("🔧 Calcul des indicateurs techniques...")
            df = self.data_manager.calculate_technical_indicators(df)
        
        # Détection des signaux
        print("🎯 Détection des opportunités de straddle...")
        signals_df = self.strategy.detect_straddle_opportunities(df)
        
        # Simulation du trading
        print("💹 Simulation du trading...")
        results = self._simulate_trading(signals_df)
        
        print("✅ Backtesting terminé!")
        return results
    
    def _simulate_trading(self, df):
        """
        Simule le trading sur les données historiques
        
        Args:
            df (pandas.DataFrame): Données avec signaux
            
        Returns:
            dict: Résultats de simulation
        """
        self.reset_backtest()
        
        for i, (timestamp, row) in enumerate(df.iterrows()):
            current_price = row['close']
            current_time = timestamp
            
            # Mise à jour des trailing stops
            self.strategy.update_trailing_stops(current_price)
            
            # Vérification des conditions de sortie
            positions_to_close = self.strategy.check_exit_conditions(current_price, current_time)
            
            # Fermeture des positions
            for pos_idx in reversed(positions_to_close):  # Reverse pour éviter les problèmes d'index
                closed_position = self.strategy.positions.pop(pos_idx)
                self.strategy.closed_positions.append(closed_position)
                
                # Mise à jour du capital
                position_value = closed_position['size'] * closed_position['entry_price']
                pnl_amount = position_value * (closed_position['pnl_pct'] / 100)
                self.capital += pnl_amount
                
                # Log du trade
                self.trade_log.append({
                    'timestamp': current_time,
                    'type': closed_position['type'],
                    'entry_price': closed_position['entry_price'],
                    'exit_price': closed_position['exit_price'],
                    'size': closed_position['size'],
                    'pnl_pct': closed_position['pnl_pct'],
                    'pnl_amount': pnl_amount,
                    'exit_reason': closed_position['exit_reason'],
                    'duration_hours': (closed_position['exit_time'] - closed_position['entry_time']).total_seconds() / 3600
                })
            
            # Vérification des nouveaux signaux
            if (row['straddle_signal'] == 1 and 
                self.strategy.get_active_positions_count() < MAX_POSITIONS * 2):  # *2 car straddle = 2 positions
                
                # Vérification des conditions de marché
                if self._check_market_conditions(row):
                    entry_data = {
                        'price': current_price,
                        'atr': row['atr'],
                        'volatility': row['volatility_std'],
                        'timestamp': current_time,
                        'signal_strength': row['signal_strength']
                    }
                    
                    # Ouverture du straddle si capital suffisant
                    required_capital = self.capital * RISK_PER_TRADE * 2  # Pour les 2 positions
                    if self.capital >= required_capital:
                        long_pos, short_pos = self.strategy.open_straddle_position(entry_data, self.capital)
                        
                        print(f"📈 Straddle ouvert à {current_time}: Prix={current_price:.2f}, Force={row['signal_strength']:.0f}")
            
            # Mise à jour de la courbe d'équité
            self.equity_curve.append(self.capital)
            self.timestamps.append(current_time)
            
            # Calcul des rendements quotidiens
            if i > 0:
                daily_return = (self.capital / self.equity_curve[-2]) - 1
                self.daily_returns.append(daily_return)
        
        # Calcul des métriques finales
        return self._calculate_final_results(df)
    
    def _check_market_conditions(self, row):
        """
        Vérifie les conditions de marché avant d'ouvrir une position
        
        Args:
            row (pandas.Series): Données de la bougie actuelle
            
        Returns:
            bool: True si les conditions sont favorables
        """
        # Vérification du spread (si disponible)
        if hasattr(row, 'spread') and row['spread'] > MAX_SPREAD:
            return False
        
        # Vérification du mouvement de prix minimum
        if len(self.equity_curve) > 1:
            price_change = abs(row['close'] / row['open'] - 1)
            if price_change < MIN_PRICE_MOVEMENT:
                return False
        
        # Vérification que la volatilité n'est pas extrême (éviter les gaps)
        if row['volatility_std'] > 2.0:  # Plus de 200% de volatilité annualisée
            return False
        
        return True
    
    def _calculate_final_results(self, df):
        """
        Calcule les métriques finales du backtest
        
        Args:
            df (pandas.DataFrame): Données utilisées
            
        Returns:
            dict: Résultats complets
        """
        # Performances de base
        total_return = (self.capital / self.initial_capital) - 1
        annualized_return = ((self.capital / self.initial_capital) ** (365 / len(df))) - 1
        
        # Métriques de risque
        if len(self.daily_returns) > 1:
            volatility = np.std(self.daily_returns) * np.sqrt(365)
            sharpe_ratio = (annualized_return - RISK_FREE_RATE) / volatility if volatility > 0 else 0
        else:
            volatility = 0
            sharpe_ratio = 0
        
        # Drawdown
        equity_series = pd.Series(self.equity_curve)
        rolling_max = equity_series.expanding().max()
        drawdown = (equity_series / rolling_max) - 1
        max_drawdown = drawdown.min()
        
        # Statistiques des trades
        performance_summary = self.strategy.get_performance_summary()
        
        # Benchmark (Buy & Hold)
        buy_hold_return = (df['close'].iloc[-1] / df['close'].iloc[0]) - 1
        
        results = {
            'period': {
                'start': df.index[0],
                'end': df.index[-1],
                'duration_days': (df.index[-1] - df.index[0]).days
            },
            'performance': {
                'initial_capital': self.initial_capital,
                'final_capital': self.capital,
                'total_return': total_return,
                'annualized_return': annualized_return,
                'buy_hold_return': buy_hold_return,
                'excess_return': total_return - buy_hold_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown
            },
            'trades': {
                'total_signals': len(df[df['straddle_signal'] == 1]),
                'total_straddles': len(performance_summary) // 2 if performance_summary else 0,
                **performance_summary
            },
            'equity_curve': pd.Series(self.equity_curve, index=self.timestamps[:len(self.equity_curve)]),
            'trade_log': pd.DataFrame(self.trade_log),
            'signals_df': df
        }
        
        return results
    
    def optimize_parameters(self, df=None, param_grid=None):
        """
        Optimise les paramètres de la stratégie
        
        Args:
            df (pandas.DataFrame): Données pour l'optimisation
            param_grid (dict): Grille des paramètres à tester
            
        Returns:
            dict: Meilleurs paramètres et résultats
        """
        if param_grid is None:
            param_grid = OPTIMIZE_PARAMETERS
        
        if df is None:
            df = self.data_manager.fetch_historical_data()
            df = self.data_manager.calculate_technical_indicators(df)
        
        print("🔄 Optimisation des paramètres en cours...")
        
        # Split des données pour éviter l'overfitting
        train_df, test_df = self.data_manager.split_data(df)
        
        best_params = None
        best_score = -float('inf')
        optimization_results = []
        
        # Génération des combinaisons de paramètres
        param_combinations = self._generate_param_combinations(param_grid)
        
        for i, params in enumerate(param_combinations):
            print(f"Test {i+1}/{len(param_combinations)}: {params}")
            
            # Mise à jour temporaire des paramètres globaux
            original_params = self._backup_params()
            self._apply_params(params)
            
            try:
                # Test sur les données d'entraînement
                train_results = self.run_backtest(train_df)
                
                if train_results:
                    # Score basé sur le Sharpe ratio ajusté du drawdown
                    score = (train_results['performance']['sharpe_ratio'] * 
                            (1 + train_results['performance']['max_drawdown']))
                    
                    optimization_results.append({
                        'params': params.copy(),
                        'train_sharpe': train_results['performance']['sharpe_ratio'],
                        'train_return': train_results['performance']['total_return'],
                        'train_drawdown': train_results['performance']['max_drawdown'],
                        'score': score
                    })
                    
                    if score > best_score:
                        best_score = score
                        best_params = params.copy()
            
            except Exception as e:
                print(f"Erreur avec paramètres {params}: {e}")
            
            finally:
                # Restauration des paramètres originaux
                self._restore_params(original_params)
        
        # Test des meilleurs paramètres sur les données de test
        if best_params:
            print(f"\n🏆 Meilleurs paramètres: {best_params}")
            self._apply_params(best_params)
            test_results = self.run_backtest(test_df)
            
            return {
                'best_params': best_params,
                'optimization_results': optimization_results,
                'train_results': None,  # À remplir si nécessaire
                'test_results': test_results
            }
        
        return None
    
    def _generate_param_combinations(self, param_grid):
        """Génère toutes les combinaisons de paramètres"""
        import itertools
        
        keys = param_grid.keys()
        values = param_grid.values()
        combinations = []
        
        for combination in itertools.product(*values):
            combinations.append(dict(zip(keys, combination)))
        
        return combinations
    
    def _backup_params(self):
        """Sauvegarde les paramètres actuels"""
        return {
            'VOLATILITY_THRESHOLD': globals()['VOLATILITY_THRESHOLD'],
            'TAKE_PROFIT_MULTIPLIER': globals()['TAKE_PROFIT_MULTIPLIER'],
            'STOP_LOSS_MULTIPLIER': globals()['STOP_LOSS_MULTIPLIER'],
            'RISK_PER_TRADE': globals()['RISK_PER_TRADE']
        }
    
    def _apply_params(self, params):
        """Applique temporairement de nouveaux paramètres"""
        for key, value in params.items():
            globals()[key.upper()] = value
    
    def _restore_params(self, original_params):
        """Restaure les paramètres originaux"""
        for key, value in original_params.items():
            globals()[key] = value
