# Configuration optimisée pour stratégie straddle rentable

# Paramètres de base
EXCHANGE_ID = 'binance'
SYMBOL = 'BTC/USDT'
TIMEFRAME = '1h'

# Période de données optimisée (périodes de forte volatilité)
START_DATE = '2023-01-01'      # Période récente avec bonnes données
END_DATE = '2024-12-31'        # Fin 2024
USE_DATE_RANGE = True          # Utiliser les dates spécifiées
DAYS_OF_DATA = 365             # Fallback si USE_DATE_RANGE = False

# Paramètres de stratégie ULTRA-OPTIMISÉS pour rentabilité maximale
VOLATILITY_THRESHOLD = 55       # Seuil encore plus bas = plus d'opportunités (optimisé)
TAKE_PROFIT_MULTIPLIER = 1.3    # TP plus agressif = saisir gains rapidement
STOP_LOSS_MULTIPLIER = 0.6      # SL très serré = limiter pertes drastiquement
TRADE_TIMEOUT_HOURS = 36        # Temps optimal pour développement

# Capital et risque ULTRA-OPTIMISÉS
INITIAL_CAPITAL = 10000         # Capital de base
RISK_PER_TRADE = 0.012         # 1.2% par trade (encore plus conservateur)
COMMISSION_RATE = 0.001        # Commission binance 0.1%
MAX_DAILY_LOSS = 0.05          # Perte max quotidienne 5%

# Paramètres backtest ULTRA-OPTIMISÉS
BACKTEST_START_DATE = '2023-03-01'  # Début mars 2023 (période explosive)
BACKTEST_END_DATE = '2024-11-30'    # Fin novembre 2024
MAX_POSITIONS = 3                   # Max 3 positions pour diversification
MAX_SPREAD = 0.002                  # Spread max 0.2% (plus strict)
MIN_PRICE_MOVEMENT = 0.00005        # Mouvement minimum très fin
RISK_FREE_RATE = 0.02              # Taux sans risque 2%
OPTIMIZE_PARAMETERS = True          # Activer optimisation

# PARAMÈTRES AVANCÉS pour gestion Long/Short optimale
HEDGE_THRESHOLD = 0.025             # Seuil mouvement pour hedge (2.5% - plus sensible)
MAX_HEDGE_RATIO = 0.4               # Max 40% de hedge (plus agressif)
DYNAMIC_STOP_LOSS = True            # Stop loss dynamique
VOLATILITY_FILTER = True            # Filtre de volatilité strict
MOMENTUM_HEDGE = True               # Hedge basé sur momentum
DELTA_NEUTRAL_TARGET = 0.1          # Cible delta neutre ±10%

# Gestion des pertes avancée
MAX_CONSECUTIVE_LOSSES = 3          # Max 3 pertes consécutives
LOSS_RECOVERY_MODE = True           # Mode récupération après pertes
ADAPTIVE_POSITION_SIZING = True     # Taille position adaptative

# Paramètres expiration options
DEFAULT_EXPIRY_DAYS = 21            # 3 semaines (optimal pour straddle)
MIN_TIME_TO_EXPIRY = 0.05          # Minimum 18 jours avant sortie forcée
MAX_TIME_TO_EXPIRY = 0.25          # Maximum 3 mois

# Paramètres Black-Scholes
INTEREST_RATE = 0.02               # Taux sans risque
MIN_VOLATILITY = 0.1               # Volatilité minimum 10%
MAX_VOLATILITY = 3.0               # Volatilité maximum 300%

