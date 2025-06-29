# Gestionnaire de Données pour le Bot Straddle
# Récupération et préparation des données crypto avec indicateurs

import ccxt
import pandas as pd
import numpy as np
# import talib  # Remplacé par des calculs pandas/numpy
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple

from config import *

class DataManager:
    """
    Gestionnaire de données crypto optimisé pour la stratégie straddle
    
    Fonctionnalités:
    - Récupération données historiques
    - Calcul indicateurs techniques
    - Validation et nettoyage des données
    - Cache pour optimisation
    """
    
    def __init__(self):
        self._setup_logging()
        self.data_cache = {}
        self.exchange = self._initialize_exchange()
        
    def _setup_logging(self):
        """Configure le logging"""
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def _initialize_exchange(self) -> Optional[ccxt.Exchange]:
        """
        Initialise la connexion à l'exchange
        
        Returns:
            ccxt.Exchange: Instance de l'exchange ou None si erreur
        """
        try:
            exchange = ccxt.binance({
                'enableRateLimit': True,
                'timeout': 30000,
                'options': {
                    'defaultType': 'spot'
                }
            })
            self.logger.info(f"✅ Connexion {EXCHANGE_ID} initialisée")
            return exchange
        except Exception as e:
            self.logger.error(f"❌ Erreur connexion exchange: {e}")
            return None
    
    def get_market_data(self) -> pd.DataFrame:
        """
        Récupère les données de marché avec indicateurs
        
        Returns:
            pd.DataFrame: Données avec indicateurs techniques
        """
        try:
            self.logger.info(f"📊 Récupération données {SYMBOL} ({TIMEFRAME})")
            
            # Récupération des données brutes
            raw_data = self._fetch_ohlcv_data()
            if raw_data.empty:
                return pd.DataFrame()
            
            # Ajout des indicateurs
            data = self._add_technical_indicators(raw_data)
            
            # Validation et nettoyage
            data = self._validate_and_clean_data(data)
            
            self.logger.info(f"✅ {len(data)} barres récupérées et traitées")
            return data
            
        except Exception as e:
            self.logger.error(f"❌ Erreur récupération données: {e}")
            return pd.DataFrame()
    
    def _fetch_ohlcv_data(self) -> pd.DataFrame:
        """
        Récupère les données OHLCV brutes
        
        Returns:
            pd.DataFrame: Données OHLCV brutes
        """
        if not self.exchange:
            raise Exception("Exchange non initialisé")
        
        if USE_DATE_RANGE:
            return self._fetch_date_range_data()
        else:
            return self._fetch_recent_data()
    
    def _fetch_date_range_data(self) -> pd.DataFrame:
        """Récupère les données pour une période spécifique"""
        start_ts = int(pd.to_datetime(START_DATE).timestamp() * 1000)
        end_ts = int(pd.to_datetime(END_DATE).timestamp() * 1000)
        
        all_data = []
        current_ts = start_ts
        
        self.logger.info(f"📅 Récupération période: {START_DATE} → {END_DATE}")
        
        while current_ts < end_ts:
            try:
                chunk = self.exchange.fetch_ohlcv(
                    SYMBOL, TIMEFRAME, since=current_ts, limit=1000
                )
                
                if not chunk:
                    break
                
                all_data.extend(chunk)
                current_ts = chunk[-1][0] + 1
                
                # Protection contre boucles infinies
                if len(all_data) > 100000:
                    self.logger.warning("⚠️ Limite de sécurité atteinte (100k barres)")
                    break
                    
            except Exception as e:
                self.logger.error(f"❌ Erreur récupération chunk: {e}")
                break
        
        return self._convert_to_dataframe(all_data)
    
    def _fetch_recent_data(self) -> pd.DataFrame:
        """Récupère les données récentes"""
        limit = DAYS_OF_DATA * 24  # Pour timeframe 1h
        
        self.logger.info(f"📅 Récupération {DAYS_OF_DATA} derniers jours")
        
        data = self.exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, limit=limit)
        return self._convert_to_dataframe(data)
    
    def _convert_to_dataframe(self, data: list) -> pd.DataFrame:
        """
        Convertit les données en DataFrame
        
        Args:
            data: Liste des données OHLCV
            
        Returns:
            pd.DataFrame: DataFrame formaté
        """
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        # Filtrage pour période exacte si demandé
        if USE_DATE_RANGE:
            df = df[(df.index >= START_DATE) & (df.index < END_DATE)]
        
        return df
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Ajoute les indicateurs techniques
        
        Args:
            df: DataFrame avec données OHLCV
            
        Returns:
            pd.DataFrame: DataFrame avec indicateurs
        """
        if df.empty:
            return df
        
        self.logger.info("📊 Calcul des indicateurs techniques")
        
        # Conversion en arrays numpy pour les calculs
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        volume = df['volume'].values
        
        # 1. Volatilité et ATR (Average True Range) - version pandas
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = abs(df['high'] - df['close'].shift())
        df['tr3'] = abs(df['low'] - df['close'].shift())
        df['true_range'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
        df['atr'] = df['true_range'].rolling(14).mean()
        df.drop(['tr1', 'tr2', 'tr3', 'true_range'], axis=1, inplace=True)
        
        df['returns'] = df['close'].pct_change()
        df['volatility'] = df['returns'].rolling(20).std() * np.sqrt(365 * 24)
        df['vol_percentile'] = df['volatility'].rolling(100).rank(pct=True) * 100
        
        # 2. RSI (Relative Strength Index) - version pandas
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 3. MACD - version pandas
        df['ema_12'] = df['close'].ewm(span=12).mean()
        df['ema_26'] = df['close'].ewm(span=26).mean()
        df['macd'] = df['ema_12'] - df['ema_26']
        df['macd_signal'] = df['macd'].ewm(span=9).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # 4. Moyennes mobiles
        df['sma_20'] = df['close'].rolling(20).mean()
        df['sma_50'] = df['close'].rolling(50).mean()
        # EMA déjà calculé pour MACD
        
        # 5. Bandes de Bollinger - version pandas
        df['bb_middle'] = df['close'].rolling(20).mean()
        std = df['close'].rolling(20).std()
        df['bb_upper'] = df['bb_middle'] + (std * 2)
        df['bb_lower'] = df['bb_middle'] - (std * 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        # 5. Indicateurs de volume
        df['volume_sma'] = df['volume'].rolling(20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # 6. Support et résistance approchés
        df['support'] = df['low'].rolling(20).min()
        df['resistance'] = df['high'].rolling(20).max()
        df['price_position'] = (df['close'] - df['support']) / (df['resistance'] - df['support'])
        
        # 7. Indicateurs personnalisés pour straddle
        df['price_range_pct'] = (df['high'] - df['low']) / df['close']
        df['volatility_rank'] = df['volatility'].rolling(252).rank(pct=True) * 100
        
        return df
    
    def _validate_and_clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Valide et nettoie les données
        
        Args:
            df: DataFrame à valider
            
        Returns:
            pd.DataFrame: DataFrame nettoyé
        """
        if df.empty:
            return df
        
        initial_len = len(df)
        
        # Suppression des valeurs aberrantes
        df = self._remove_outliers(df)
        
        # Suppression des NaN
        df = df.dropna()
        
        # Validation de la cohérence
        df = self._validate_price_consistency(df)
        
        final_len = len(df)
        removed = initial_len - final_len
        
        if removed > 0:
            self.logger.info(f"🧹 {removed} barres supprimées lors du nettoyage")
        
        return df
    
    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Supprime les valeurs aberrantes"""
        # Filtrage des prix négatifs ou nuls
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            df = df[df[col] > 0]
        
        # Filtrage des mouvements extrêmes (>50% en une barre)
        df['price_change'] = df['close'].pct_change().abs()
        df = df[df['price_change'] < 0.5]
        df = df.drop('price_change', axis=1)
        
        return df
    
    def _validate_price_consistency(self, df: pd.DataFrame) -> pd.DataFrame:
        """Valide la cohérence des prix OHLC"""
        # High >= max(Open, Close) et Low <= min(Open, Close)
        valid_high = df['high'] >= df[['open', 'close']].max(axis=1)
        valid_low = df['low'] <= df[['open', 'close']].min(axis=1)
        
        return df[valid_high & valid_low]
    
    def get_backtest_data(self) -> pd.DataFrame:
        """
        Récupère les données spécifiquement pour le backtest
        
        Returns:
            pd.DataFrame: Données filtrées pour la période de backtest
        """
        full_data = self.get_market_data()
        
        if full_data.empty:
            return pd.DataFrame()
        
        # Filtrage pour la période de backtest
        backtest_data = full_data[
            (full_data.index >= BACKTEST_START_DATE) & 
            (full_data.index < BACKTEST_END_DATE)
        ]
        
        self.logger.info(f"📊 Données backtest: {len(backtest_data)} barres "
                        f"({BACKTEST_START_DATE} → {BACKTEST_END_DATE})")
        
        return backtest_data
    
    def get_data_summary(self, df: pd.DataFrame) -> dict:
        """
        Génère un résumé des données
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            dict: Résumé statistique
        """
        if df.empty:
            return {}
        
        return {
            'period': f"{df.index[0].strftime('%Y-%m-%d')} → {df.index[-1].strftime('%Y-%m-%d')}",
            'total_bars': len(df),
            'price_range': f"${df['close'].min():,.0f} - ${df['close'].max():,.0f}",
            'avg_volatility': f"{df['volatility'].mean():.2%}",
            'avg_volume': f"{df['volume'].mean():,.0f}",
            'missing_data': df.isnull().sum().sum(),
            'data_quality': 'Excellent' if df.isnull().sum().sum() == 0 else 'Bon'
        }
    
    def save_data_cache(self, df: pd.DataFrame, cache_key: str = 'default'):
        """Sauvegarde les données en cache"""
        self.data_cache[cache_key] = df.copy()
        self.logger.debug(f"💾 Données sauvegardées en cache: {cache_key}")
    
    def load_data_cache(self, cache_key: str = 'default') -> Optional[pd.DataFrame]:
        """Charge les données depuis le cache"""
        if cache_key in self.data_cache:
            self.logger.debug(f"📂 Données chargées depuis cache: {cache_key}")
            return self.data_cache[cache_key].copy()
        return None
