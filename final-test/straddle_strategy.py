# Stratégie de straddle simple pour BTC

import pandas as pd
import numpy as np
from config import *

class StraddleStrategy:
    """Stratégie de straddle simplifiée"""
    
    def __init__(self):
        self.trades = []
        
    def detect_signals(self, df):
        """
        Détecte les signaux de straddle simples
        
        Args:
            df: DataFrame avec les données et indicateurs
            
        Returns:
            DataFrame avec signaux ajoutés
        """
        signals = df.copy()
        signals['signal'] = 0
        
        # Signal simple: volatilité au-dessus du seuil
        for i in range(len(signals)):
            if signals['vol_percentile'].iloc[i] >= VOLATILITY_THRESHOLD:
                signals.loc[signals.index[i], 'signal'] = 1
        
        return signals
    
    def calculate_levels(self, price, atr):
        """
        Calcule les niveaux de TP/SL
        
        Args:
            price: Prix d'entrée
            atr: Average True Range
            
        Returns:
            dict: Niveaux pour long et short
        """
        return {
            'long_tp': price + (atr * TAKE_PROFIT_MULTIPLIER),
            'long_sl': price - (atr * STOP_LOSS_MULTIPLIER),
            'short_tp': price - (atr * TAKE_PROFIT_MULTIPLIER),
            'short_sl': price + (atr * STOP_LOSS_MULTIPLIER)
        }
    
    def backtest(self, signals):
        """
        Backtesting simple
        
        Args:
            signals: DataFrame avec signaux
            
        Returns:
            dict: Résultats du backtest
        """
        capital = INITIAL_CAPITAL
        equity = [capital]
        trades = []
        
        position = None
        
        for i in range(1, len(signals)):
            current_price = signals['close'].iloc[i]
            current_time = signals.index[i]
            
            # Vérifier si on a une position ouverte
            if position:
                # Vérifier les conditions de sortie
                exit_reason = None
                
                if position['type'] == 'long':
                    if current_price >= position['tp']:
                        exit_reason = 'TP'
                    elif current_price <= position['sl']:
                        exit_reason = 'SL'
                elif position['type'] == 'short':
                    if current_price <= position['tp']:
                        exit_reason = 'TP'
                    elif current_price >= position['sl']:
                        exit_reason = 'SL'
                
                # Timeout après 48 heures
                if (current_time - position['entry_time']).total_seconds() / 3600 > 48:
                    exit_reason = 'Timeout'
                
                if exit_reason:
                    # Calculer le P&L
                    if position['type'] == 'long':
                        pnl = (current_price - position['entry_price']) / position['entry_price']
                    else:
                        pnl = (position['entry_price'] - current_price) / position['entry_price']
                    
                    pnl_after_fees = pnl - (2 * COMMISSION_RATE)
                    capital *= (1 + pnl_after_fees * position['size_pct'])
                    
                    trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': current_time,
                        'type': position['type'],
                        'entry_price': position['entry_price'],
                        'exit_price': current_price,
                        'pnl_pct': pnl_after_fees * 100,
                        'exit_reason': exit_reason
                    })
                    
                    position = None
            
            # Nouveau signal
            if signals['signal'].iloc[i] == 1 and position is None:
                atr = signals['atr'].iloc[i]
                levels = self.calculate_levels(current_price, atr)
                
                # Alternance entre long et short
                pos_type = 'long' if len(trades) % 2 == 0 else 'short'
                
                position = {
                    'type': pos_type,
                    'entry_time': current_time,
                    'entry_price': current_price,
                    'tp': levels[f'{pos_type}_tp'],
                    'sl': levels[f'{pos_type}_sl'],
                    'size_pct': RISK_PER_TRADE
                }
            
            equity.append(capital)
        
        return {
            'equity': pd.Series(equity, index=signals.index[:len(equity)]),
            'trades': pd.DataFrame(trades),
            'final_capital': capital,
            'total_return': (capital / INITIAL_CAPITAL - 1) * 100
        }
