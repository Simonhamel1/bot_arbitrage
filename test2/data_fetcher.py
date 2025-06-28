import ccxt
import pandas as pd
import numpy as np
import talib
from config import TIMEFRAME, DATA_LIMIT, ATR_PERIOD, VOLATILITY_PERIOD

def initialize_exchange(exchange_id, params=None):
    """
    Initialise une connexion à une plateforme d'échange
    
    Args:
        exchange_id (str): ID de l'échange (ex: 'binance')
        params (dict): Paramètres additionnels pour l'échange
        
    Returns:
        ccxt.Exchange: Instance de l'échange
    """
    if params is None:
        params = {'enableRateLimit': True}
    
    exchange_class = getattr(ccxt, exchange_id)
    return exchange_class(params)

def fetch_ohlcv(exchange, symbol, timeframe=TIMEFRAME, limit=DATA_LIMIT):
    """
    Récupère les données OHLCV (Open, High, Low, Close, Volume)
    
    Args:
        exchange (ccxt.Exchange): Instance de l'échange
        symbol (str): Paire de trading (ex: 'BTC/USDT')
        timeframe (str): Intervalle de temps (ex: '1m', '1h', '1d')
        limit (int): Nombre de points de données à récupérer
    
    Returns:
        pandas.DataFrame: DataFrame avec les données OHLCV
    """
    data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def prepare_data_for_straddle(df):
    """
    Prépare les données pour la stratégie de straddle
    
    Args:
        df (pandas.DataFrame): DataFrame avec les données OHLCV
    
    Returns:
        pandas.DataFrame: DataFrame avec les indicateurs techniques ajoutés
    """
    # Assurer que le DataFrame est trié par horodatage
    df = df.sort_values('timestamp')
    
    # Calculer les rendements
    df['returns'] = df['close'].pct_change()
    
    # Calculer l'ATR (Average True Range)
    df['atr'] = talib.ATR(df['high'].values, df['low'].values, 
                           df['close'].values, timeperiod=ATR_PERIOD)
    
    # ATR relatif (ATR / prix)
    df['atr_pct'] = df['atr'] / df['close']
    
    # Volatilité historique (écart-type des rendements)
    df['volatility'] = df['returns'].rolling(window=VOLATILITY_PERIOD).std() * np.sqrt(VOLATILITY_PERIOD)
    
    # Volume relatif (comparé à la moyenne mobile)
    df['volume_ma'] = df['volume'].rolling(window=20).mean()
    df['relative_volume'] = df['volume'] / df['volume_ma']
    
    # Supprimer les valeurs NaN
    df = df.dropna()
    
    return df

def fetch_ticker(exchange, symbol):
    """
    Récupère les informations de ticker pour un symbole
    
    Args:
        exchange (ccxt.Exchange): Instance de l'échange
        symbol (str): Paire de trading (ex: 'BTC/USDT')
    
    Returns:
        dict: Informations de ticker
    """
    return exchange.fetch_ticker(symbol)

def fetch_market_info(exchange, symbol):
    """
    Récupère les informations de marché pour un symbole
    
    Args:
        exchange (ccxt.Exchange): Instance de l'échange
        symbol (str): Paire de trading (ex: 'BTC/USDT')
    
    Returns:
        dict: Informations de marché (limites, précision, etc.)
    """
    markets = exchange.load_markets()
    if symbol in markets:
        return markets[symbol]
    else:
        raise ValueError(f"Symbole '{symbol}' non trouvé sur l'échange")

def fetch_balance(exchange):
    """
    Récupère le solde du compte
    
    Args:
        exchange (ccxt.Exchange): Instance de l'échange
    
    Returns:
        dict: Solde du compte
    """
    return exchange.fetch_balance()
