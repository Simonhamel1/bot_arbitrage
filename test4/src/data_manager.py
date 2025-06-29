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
        Récupère les données BTC/USDT selon la configuration de dates
        
        Returns:
            pandas.DataFrame: Données avec indicateurs
        """
        try:
            print(f"📊 Récupération des données {SYMBOL}...")
            
            if USE_DATE_RANGE:
                # Utiliser les dates spécifiées
                print(f"� Période: {START_DATE} → {END_DATE}")
                
                # Convertir les dates en timestamps
                start_ts = int(pd.to_datetime(START_DATE).timestamp() * 1000)
                end_ts = int(pd.to_datetime(END_DATE).timestamp() * 1000)
                
                # Récupérer toutes les données pour la période
                all_data = []
                current_ts = start_ts
                
                while current_ts < end_ts:
                    # Récupérer par chunks de 1000 (limite API)
                    data_chunk = self.exchange.fetch_ohlcv(
                        SYMBOL, TIMEFRAME, since=current_ts, limit=1000
                    )
                    
                    if not data_chunk:
                        break
                        
                    all_data.extend(data_chunk)
                    current_ts = data_chunk[-1][0] + 1
                    
                    # Protection contre les boucles infinies
                    if len(all_data) > 50000:  # Limite de sécurité
                        break
                
                data = all_data
            else:
                # Utiliser les X derniers jours
                print(f"📅 Récupération des {DAYS_OF_DATA} derniers jours")
                data = self.exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=DAYS_OF_DATA * 24)
            
            # Conversion en DataFrame
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Filtrer exactement la période demandée si USE_DATE_RANGE
            if USE_DATE_RANGE:
                df = df[(df.index >= START_DATE) & (df.index < END_DATE)]
            
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
