# Configuration simple pour la stratégie de straddle BTC

# Paramètres de base
EXCHANGE_ID = 'binance'
SYMBOL = 'BTC/USDT'
TIMEFRAME = '1h'
DAYS_OF_DATA = 365             # Nombre de jours de données à récupérer

# Paramètres de la stratégie (modifiez ces valeurs selon vos besoins)
VOLATILITY_THRESHOLD = 75       # Seuil de volatilité (percentile)
TAKE_PROFIT_MULTIPLIER = 2.0    # Multiplicateur pour take profit
STOP_LOSS_MULTIPLIER = 1.0      # Multiplicateur pour stop loss
TRADE_TIMEOUT_HOURS = 24        # Fermeture forcée après X heures

# Capital et risque
INITIAL_CAPITAL = 10000         # Capital de départ
RISK_PER_TRADE = 0.02          # 2% de risque par trade
COMMISSION_RATE = 0.001        # 0.1% de commission
