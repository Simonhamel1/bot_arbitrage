# Configuration de la stratégie de straddle (strangle)

# Paramètres des échanges
EXCHANGE_ID = 'binance'
ENABLE_RATE_LIMIT = True

# Symboles de trading
SYMBOL = 'BTC/USDT'  # Actif principal pour la stratégie de straddle

# Paramètres de récupération des données
TIMEFRAME = '5m'     # Timeframe plus long pour mieux capturer la volatilité
DATA_LIMIT = 500

# Paramètres de la stratégie de straddle
VOLATILITY_PERIOD = 20       # Période pour calculer la volatilité
ENTRY_VOLATILITY_PERCENTILE = 75  # Percentile de volatilité pour entrer (0-100)
TAKE_PROFIT_PCT = 0.03       # Pourcentage de prise de profit (3%)
STOP_LOSS_PCT = 0.02         # Pourcentage de stop loss (2%)
POSITION_SIZE_PCT = 0.1      # Pourcentage du capital à risquer par position (10%)
MAX_POSITION_DURATION = 24   # Durée maximale d'une position en périodes
TRANSACTION_FEE = 0.001      # Frais de transaction (0.1%)

# Paramètres avancés
USE_ATR = True                # Utiliser l'ATR (Average True Range) pour mesurer la volatilité
ATR_PERIOD = 14               # Période pour le calcul de l'ATR
ATR_MULTIPLIER = 2.0          # Multiplicateur pour l'ATR (niveaux de prise de profit/stop loss)
MIN_VOLUME_PERCENTILE = 50    # Percentile minimum de volume pour trader (0-100)
