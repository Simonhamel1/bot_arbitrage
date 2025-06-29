# Stratégie Straddle Avancée avec Gestion Long/Short

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from config import *

class AdvancedStraddleStrategy:
    """
    Stratégie straddle avancée avec :
    - Gestion des positions longues/courtes pour limiter les pertes
    - Risque maximum = prime d'exercice 
    - Optimisation de la rentabilité
    """
    
    def __init__(self):
        self.positions = []  # Positions ouvertes
        self.trades_history = []  # Historique des trades
        self.capital = INITIAL_CAPITAL
        self.max_risk_per_trade = INITIAL_CAPITAL * RISK_PER_TRADE
        
    def simulate_straddle_price(self, spot_price, strike, volatility, time_to_expiry, interest_rate=0.02):
        """
        Simule le prix d'un straddle (call + put) selon Black-Scholes simplifié
        
        Args:
            spot_price: Prix actuel du sous-jacent
            strike: Prix d'exercice
            volatility: Volatilité implicite
            time_to_expiry: Temps jusqu'à expiration (en années)
            interest_rate: Taux d'intérêt sans risque
            
        Returns:
            dict: Prix du call, put et straddle total
        """
        if time_to_expiry <= 0:
            # À l'expiration, valeur intrinsèque seulement
            call_value = max(0, spot_price - strike)
            put_value = max(0, strike - spot_price)
            return {
                'call_price': call_value,
                'put_price': put_value,
                'straddle_price': call_value + put_value,
                'time_value': 0
            }
        
        # Calcul Black-Scholes simplifié
        d1 = (np.log(spot_price / strike) + (interest_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
        d2 = d1 - volatility * np.sqrt(time_to_expiry)
        
        # Fonction de répartition normale
        def norm_cdf(x):
            return 0.5 * (1 + np.sign(x) * np.sqrt(1 - np.exp(-2 * x**2 / np.pi)))
        
        # Prix du call
        call_price = spot_price * norm_cdf(d1) - strike * np.exp(-interest_rate * time_to_expiry) * norm_cdf(d2)
        
        # Prix du put (parité call-put)
        put_price = call_price - spot_price + strike * np.exp(-interest_rate * time_to_expiry)
        
        straddle_price = call_price + put_price
        intrinsic_value = max(0, abs(spot_price - strike))
        time_value = straddle_price - intrinsic_value
        
        return {
            'call_price': max(0.01, call_price),  # Prix minimum pour éviter 0
            'put_price': max(0.01, put_price),
            'straddle_price': max(0.02, straddle_price),
            'time_value': max(0, time_value),
            'intrinsic_value': intrinsic_value
        }
    
    def calculate_position_size(self, straddle_price):
        """
        Calcule la taille de position basée sur le risque maximal
        Le risque maximum = prime payée pour le straddle
        """
        max_loss = straddle_price  # Perte max = prime payée
        
        # Nombre de contrats basé sur le risque par trade
        contracts = int(self.max_risk_per_trade / max_loss)
        contracts = max(1, min(contracts, 10))  # Entre 1 et 10 contrats
        
        return contracts
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
