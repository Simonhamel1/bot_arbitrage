# Configuration simple pour la stratégie de straddle BTC

# Paramètres de base
EXCHANGE_ID = 'binance'
SYMBOL = 'BTC/USDT'
TIMEFRAME = '1h'

# Période de données (modifiez ces dates selon vos besoins)
START_DATE = '2024-01-01'      # Date de début (YYYY-MM-DD)
END_DATE = '2025-01-01'        # Date de fin (YYYY-MM-DD)
# OU utilisez DAYS_OF_DATA pour les X derniers jours
USE_DATE_RANGE = True          # True = utiliser START_DATE/END_DATE, False = utiliser DAYS_OF_DATA
DAYS_OF_DATA = 365             # Nombre de jours de données (si USE_DATE_RANGE = False)

# Paramètres de la stratégie (modifiez ces valeurs selon vos besoins)
VOLATILITY_THRESHOLD = 75       # Seuil de volatilité (percentile)
TAKE_PROFIT_MULTIPLIER = 2.0    # Multiplicateur pour take profit
STOP_LOSS_MULTIPLIER = 1.0      # Multiplicateur pour stop loss
TRADE_TIMEOUT_HOURS = 24        # Fermeture forcée après X heures

# Capital et risque
INITIAL_CAPITAL = 10000         # Capital de départ
RISK_PER_TRADE = 0.02          # 2% de risque par trade
COMMISSION_RATE = 0.001        # 0.1% de commission

# Paramètres de backtest
BACKTEST_START_DATE = '2022-01-01'  # Date de début du backtest
BACKTEST_END_DATE = '2024-12-31'    # Date de fin du backtest
MAX_POSITIONS = 3                  # Nombre maximum de positions simultanées
MAX_SPREAD = 0.005                 # Spread maximum acceptable (0.5%)
MIN_PRICE_MOVEMENT = 0.0001        # Mouvement minimum de prix significatif
RISK_FREE_RATE = 0.02              # Taux sans risque annuel pour calculs de performance
OPTIMIZE_PARAMETERS = False        # Activation de l'optimisation des paramètres

