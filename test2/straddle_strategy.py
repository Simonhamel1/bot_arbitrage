# Fonctions pour la stratégie de straddle (strangle)
import numpy as np
import pandas as pd
import talib

def calculate_volatility(prices, period=14, method='std'):
    """
    Calcule la volatilité des prix en utilisant différentes méthodes
    
    Args:
        prices (numpy.ndarray): Série temporelle des prix
        period (int): Période pour le calcul de la volatilité
        method (str): Méthode de calcul: 'std', 'atr', 'parkinson'
    
    Returns:
        numpy.ndarray: Mesure de volatilité
    """
    if method == 'std':
        # Écart-type des rendements
        returns = np.log(prices[1:] / prices[:-1])
        vol = np.zeros_like(prices)
        for i in range(period, len(prices)):
            vol[i] = np.std(returns[i-period:i]) * np.sqrt(period)
        return vol
    
    elif method == 'atr':
        # Average True Range (nécessite high, low, close)
        # Note: Dans ce cas, prices devrait être un DataFrame avec high, low, close
        high = prices['high'].values
        low = prices['low'].values
        close = prices['close'].values
        
        atr = talib.ATR(high, low, close, timeperiod=period)
        # Normaliser par le prix pour obtenir une volatilité relative
        return atr / close
    
    elif method == 'parkinson':
        # Formule de Parkinson (nécessite high et low)
        high = prices['high'].values
        low = prices['low'].values
        
        vol = np.zeros_like(high)
        const = 1.0 / (4.0 * np.log(2.0))
        
        for i in range(period, len(high)):
            sum_squares = 0
            for j in range(i-period, i):
                log_hl = np.log(high[j] / low[j])
                sum_squares += log_hl * log_hl
            
            vol[i] = np.sqrt(const * sum_squares / period)
        
        return vol
    
    else:
        raise ValueError(f"Méthode de calcul de volatilité '{method}' non reconnue")

def is_volatility_high(volatility, current_idx, percentile=75, lookback=100):
    """
    Détermine si la volatilité actuelle est élevée par rapport à l'historique récent
    
    Args:
        volatility (numpy.ndarray): Série temporelle de volatilité
        current_idx (int): Index actuel dans la série
        percentile (float): Percentile à utiliser comme seuil (0-100)
        lookback (int): Période historique à considérer
    
    Returns:
        bool: True si la volatilité est élevée, False sinon
    """
    if current_idx < lookback:
        return False
    
    historical_vol = volatility[current_idx-lookback:current_idx]
    threshold = np.percentile(historical_vol[~np.isnan(historical_vol)], percentile)
    
    return volatility[current_idx] > threshold

def calculate_straddle_levels(price, volatility, atr_multiplier=2.0):
    """
    Calcule les niveaux d'entrée, de take profit et de stop loss pour une stratégie de straddle
    
    Args:
        price (float): Prix actuel
        volatility (float): Mesure de volatilité (comme ATR)
        atr_multiplier (float): Multiplicateur pour l'ATR
    
    Returns:
        dict: Niveaux pour les positions longues et courtes
    """
    price_range = volatility * atr_multiplier
    
    return {
        'long': {
            'entry': price,
            'take_profit': price + price_range,
            'stop_loss': price - price_range * 0.5,
        },
        'short': {
            'entry': price,
            'take_profit': price - price_range,
            'stop_loss': price + price_range * 0.5,
        }
    }

def generate_straddle_signals(df, volatility_col='volatility', price_col='close', 
                             entry_percentile=75, volatility_lookback=100):
    """
    Génère des signaux pour une stratégie de straddle basée sur la volatilité
    
    Args:
        df (pandas.DataFrame): DataFrame avec les données de prix et volatilité
        volatility_col (str): Nom de la colonne de volatilité
        price_col (str): Nom de la colonne de prix
        entry_percentile (float): Percentile de volatilité pour entrer (0-100)
        volatility_lookback (int): Période historique pour évaluer la volatilité
    
    Returns:
        pandas.DataFrame: DataFrame avec les signaux ajoutés
    """
    signals = pd.DataFrame(index=df.index)
    signals['price'] = df[price_col]
    signals['volatility'] = df[volatility_col]
    signals['high_volatility'] = False
    signals['long_signal'] = 0
    signals['short_signal'] = 0
    signals['straddle_signal'] = 0  # 1 pour long et short simultanés
    signals['long_tp'] = np.nan
    signals['long_sl'] = np.nan
    signals['short_tp'] = np.nan
    signals['short_sl'] = np.nan
    
    for i in range(volatility_lookback, len(df)):
        signals.loc[df.index[i], 'high_volatility'] = is_volatility_high(
            df[volatility_col].values, i, entry_percentile, volatility_lookback)
        
        if signals.loc[df.index[i], 'high_volatility']:
            # En cas de forte volatilité, préparer pour un straddle
            price = df.loc[df.index[i], price_col]
            vol = df.loc[df.index[i], volatility_col]
            
            levels = calculate_straddle_levels(price, vol)
            
            signals.loc[df.index[i], 'straddle_signal'] = 1
            signals.loc[df.index[i], 'long_signal'] = 1
            signals.loc[df.index[i], 'short_signal'] = 1
            
            signals.loc[df.index[i], 'long_tp'] = levels['long']['take_profit']
            signals.loc[df.index[i], 'long_sl'] = levels['long']['stop_loss']
            signals.loc[df.index[i], 'short_tp'] = levels['short']['take_profit']
            signals.loc[df.index[i], 'short_sl'] = levels['short']['stop_loss']
    
    return signals

def calculate_position_size(capital, risk_per_trade, entry_price, stop_loss):
    """
    Calcule la taille de position basée sur le risque
    
    Args:
        capital (float): Capital disponible
        risk_per_trade (float): Pourcentage du capital à risquer (ex: 0.01 pour 1%)
        entry_price (float): Prix d'entrée
        stop_loss (float): Niveau de stop loss
    
    Returns:
        float: Quantité à acheter/vendre
    """
    risk_amount = capital * risk_per_trade
    price_risk = abs(entry_price - stop_loss)
    
    # Si price_risk est trop petit, limiter pour éviter les divisions par zéro
    if price_risk < entry_price * 0.001:
        price_risk = entry_price * 0.001
    
    position_size = risk_amount / price_risk
    return position_size

def backtest_straddle_strategy(signals, initial_capital=10000, position_size_pct=0.1, 
                              transaction_fee=0.001, max_position_duration=24):
    """
    Backteste la stratégie de straddle
    
    Args:
        signals (pandas.DataFrame): DataFrame avec les signaux générés
        initial_capital (float): Capital initial
        position_size_pct (float): Pourcentage du capital par position
        transaction_fee (float): Frais de transaction par ordre
        max_position_duration (int): Durée maximale d'une position en périodes
    
    Returns:
        tuple: (equity_curve, trades)
            - equity_curve: Courbe d'équité
            - trades: Détails des trades
    """
    capital = initial_capital
    equity_curve = [capital]
    trades = []
    
    long_position = None
    short_position = None
    long_entry_idx = -1
    short_entry_idx = -1
    
    for i in range(1, len(signals)):
        price = signals.iloc[i]['price']
        current_time = signals.index[i]
        
        # Vérifier si des positions ouvertes atteignent leur TP/SL
        if long_position is not None:
            # Vérifier TP/SL pour la position longue
            if price >= long_position['take_profit']:
                # Take profit atteint
                pnl = (price * (1 - transaction_fee)) / (long_position['entry_price'] * (1 + transaction_fee)) - 1
                capital *= (1 + pnl * long_position['size_pct'])
                
                trades.append({
                    'type': 'long',
                    'entry_time': signals.index[long_entry_idx],
                    'exit_time': current_time,
                    'entry_price': long_position['entry_price'],
                    'exit_price': price,
                    'pnl_pct': pnl * 100,
                    'exit_reason': 'take_profit'
                })
                
                long_position = None
                
            elif price <= long_position['stop_loss']:
                # Stop loss atteint
                pnl = (price * (1 - transaction_fee)) / (long_position['entry_price'] * (1 + transaction_fee)) - 1
                capital *= (1 + pnl * long_position['size_pct'])
                
                trades.append({
                    'type': 'long',
                    'entry_time': signals.index[long_entry_idx],
                    'exit_time': current_time,
                    'entry_price': long_position['entry_price'],
                    'exit_price': price,
                    'pnl_pct': pnl * 100,
                    'exit_reason': 'stop_loss'
                })
                
                long_position = None
                
            elif i - long_entry_idx >= max_position_duration:
                # Timeout de la position
                pnl = (price * (1 - transaction_fee)) / (long_position['entry_price'] * (1 + transaction_fee)) - 1
                capital *= (1 + pnl * long_position['size_pct'])
                
                trades.append({
                    'type': 'long',
                    'entry_time': signals.index[long_entry_idx],
                    'exit_time': current_time,
                    'entry_price': long_position['entry_price'],
                    'exit_price': price,
                    'pnl_pct': pnl * 100,
                    'exit_reason': 'timeout'
                })
                
                long_position = None
        
        if short_position is not None:
            # Vérifier TP/SL pour la position courte
            if price <= short_position['take_profit']:
                # Take profit atteint
                pnl = 1 - (price * (1 + transaction_fee)) / (short_position['entry_price'] * (1 - transaction_fee))
                capital *= (1 + pnl * short_position['size_pct'])
                
                trades.append({
                    'type': 'short',
                    'entry_time': signals.index[short_entry_idx],
                    'exit_time': current_time,
                    'entry_price': short_position['entry_price'],
                    'exit_price': price,
                    'pnl_pct': pnl * 100,
                    'exit_reason': 'take_profit'
                })
                
                short_position = None
                
            elif price >= short_position['stop_loss']:
                # Stop loss atteint
                pnl = 1 - (price * (1 + transaction_fee)) / (short_position['entry_price'] * (1 - transaction_fee))
                capital *= (1 + pnl * short_position['size_pct'])
                
                trades.append({
                    'type': 'short',
                    'entry_time': signals.index[short_entry_idx],
                    'exit_time': current_time,
                    'entry_price': short_position['entry_price'],
                    'exit_price': price,
                    'pnl_pct': pnl * 100,
                    'exit_reason': 'stop_loss'
                })
                
                short_position = None
                
            elif i - short_entry_idx >= max_position_duration:
                # Timeout de la position
                pnl = 1 - (price * (1 + transaction_fee)) / (short_position['entry_price'] * (1 - transaction_fee))
                capital *= (1 + pnl * short_position['size_pct'])
                
                trades.append({
                    'type': 'short',
                    'entry_time': signals.index[short_entry_idx],
                    'exit_time': current_time,
                    'entry_price': short_position['entry_price'],
                    'exit_price': price,
                    'pnl_pct': pnl * 100,
                    'exit_reason': 'timeout'
                })
                
                short_position = None
        
        # Entrée dans de nouvelles positions
        if long_position is None and signals.iloc[i]['long_signal'] == 1:
            long_position = {
                'entry_price': price,
                'take_profit': signals.iloc[i]['long_tp'],
                'stop_loss': signals.iloc[i]['long_sl'],
                'size_pct': position_size_pct / 2  # diviser par 2 si on fait un straddle complet
            }
            long_entry_idx = i
        
        if short_position is None and signals.iloc[i]['short_signal'] == 1:
            short_position = {
                'entry_price': price,
                'take_profit': signals.iloc[i]['short_tp'],
                'stop_loss': signals.iloc[i]['short_sl'],
                'size_pct': position_size_pct / 2  # diviser par 2 si on fait un straddle complet
            }
            short_entry_idx = i
        
        equity_curve.append(capital)
    
    # Fermer les positions restantes à la fin
    if long_position is not None:
        # Fermeture forcée de la position longue
        price = signals.iloc[-1]['price']
        pnl = (price * (1 - transaction_fee)) / (long_position['entry_price'] * (1 + transaction_fee)) - 1
        capital *= (1 + pnl * long_position['size_pct'])
        
        trades.append({
            'type': 'long',
            'entry_time': signals.index[long_entry_idx],
            'exit_time': signals.index[-1],
            'entry_price': long_position['entry_price'],
            'exit_price': price,
            'pnl_pct': pnl * 100,
            'exit_reason': 'end_of_data'
        })
    
    if short_position is not None:
        # Fermeture forcée de la position courte
        price = signals.iloc[-1]['price']
        pnl = 1 - (price * (1 + transaction_fee)) / (short_position['entry_price'] * (1 - transaction_fee))
        capital *= (1 + pnl * short_position['size_pct'])
        
        trades.append({
            'type': 'short',
            'entry_time': signals.index[short_entry_idx],
            'exit_time': signals.index[-1],
            'entry_price': short_position['entry_price'],
            'exit_price': price,
            'pnl_pct': pnl * 100,
            'exit_reason': 'end_of_data'
        })
    
    return pd.Series(equity_curve, index=signals.index), pd.DataFrame(trades)
