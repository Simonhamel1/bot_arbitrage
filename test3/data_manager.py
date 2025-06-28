# Module simple de récupération des données pour BTC

import ccxt
import pandas as pd
import numpy as np
import talib

from config import *

class DataManager:
    """Gestionnaire simple des données pour BTC"""
    
    def __init__(self):
        self.exchange = self._initialize_exchange()
        
    def _initialize_exchange(self):
        """Initialise la connexion à Binance"""
        try:
            return ccxt.binance({'enableRateLimit': True})
        except Exception as e:
            print(f"Erreur connexion échange: {e}")
            return None
    
    def get_data(self):
        """
        Récupère les données BTC/USDT et calcule les indicateurs
        
        Returns:
            pandas.DataFrame: Données avec indicateurs
        """
        try:
            # Récupération des données
            print(f"📊 Récupération des données {SYMBOL}...")
            data = self.exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=DAYS_OF_DATA * 24)
            
            # Conversion en DataFrame
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Calcul des indicateurs simples
            df = self._add_indicators(df)
            
            print(f"✅ {len(df)} bougies récupérées")
            return df
            
        except Exception as e:
            print(f"❌ Erreur récupération données: {e}")
            return pd.DataFrame()
    
    def _add_indicators(self, df):
        """Ajoute les indicateurs techniques de base"""
        
        # ATR pour la volatilité
        df['atr'] = talib.ATR(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)
        
        # Volatilité historique
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(20).std() * np.sqrt(365 * 24)
        
        # Percentile de volatilité sur 100 périodes
        df['vol_percentile'] = df['volatility'].rolling(100).rank(pct=True) * 100
        
        # RSI
        df['rsi'] = talib.RSI(df['close'].values, timeperiod=14)
        
        # Suppression des NaN
        df = df.dropna()
        
        return df
