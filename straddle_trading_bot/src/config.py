# Configuration du Bot de Trading Straddle
# Paramètres optimisés pour rentabilité maximale avec risque contrôlé

# =====================================================================================
# PARAMÈTRES DE BASE
# =====================================================================================

# Exchange et symbole
EXCHANGE_ID = 'binance'
SYMBOL = 'BTC/USDT'
TIMEFRAME = '1h'

# =====================================================================================
# GESTION DES DONNÉES
# =====================================================================================

# Période de données (utiliser USE_DATE_RANGE=True pour dates spécifiques)
USE_DATE_RANGE = True
START_DATE = '2023-01-01'
END_DATE = '2024-12-31'
DAYS_OF_DATA = 365  # Utilisé si USE_DATE_RANGE=False

# Période de backtest (sous-ensemble des données)
BACKTEST_START_DATE = '2023-06-01'
BACKTEST_END_DATE = '2024-10-31'

# =====================================================================================
# PARAMÈTRES DE STRATÉGIE (OPTIMISÉS POUR RENTABILITÉ)
# =====================================================================================

# Critères d'entrée
VOLATILITY_THRESHOLD = 55          # Percentile de volatilité minimum (55% = plus d'opportunités)
MIN_SIGNAL_QUALITY = 0.75          # Qualité minimum du signal (75% = sélectif)
MIN_VOLUME_RATIO = 1.2              # Ratio volume minimum vs moyenne
MAX_PRICE_RANGE = 0.06              # Range de prix maximum pour consolidation

# Gestion des sorties
TAKE_PROFIT_MULTIPLIER = 1.3        # Take profit à 30% de gain
STOP_LOSS_MULTIPLIER = 0.6          # Stop loss à 60% de perte
TRADE_TIMEOUT_HOURS = 36            # Timeout à 36 heures
DYNAMIC_STOP_LOSS = True            # Stop loss adaptatif

# =====================================================================================
# GESTION DU CAPITAL ET RISQUE
# =====================================================================================

INITIAL_CAPITAL = 10000             # Capital initial
RISK_PER_TRADE = 0.012             # 1.2% de risque par trade (très conservateur)
MAX_POSITIONS = 3                   # Maximum 3 positions simultanées
MAX_DAILY_LOSS = 0.05              # Arrêt si perte quotidienne > 5%
MAX_CONSECUTIVE_LOSSES = 3          # Arrêt après 3 pertes consécutives

# Commissions et frais
COMMISSION_RATE = 0.001            # 0.1% par trade (Binance)

# =====================================================================================
# HEDGING ET PROTECTION DIRECTIONNELLE
# =====================================================================================

# Activation du hedging
ENABLE_HEDGING = True              # Activer positions Long/Short de protection
HEDGE_THRESHOLD = 0.025            # Hedger si mouvement > 2.5%
MAX_HEDGE_RATIO = 0.4              # Maximum 40% de hedge
DELTA_NEUTRAL_TARGET = 0.1         # Cible delta neutre ±10%

# Paramètres avancés de hedging
MOMENTUM_HEDGE = True              # Hedge basé sur momentum
VOLATILITY_HEDGE = True            # Hedge selon changement de volatilité

# =====================================================================================
# PARAMÈTRES D'OPTIONS (SIMULATION BLACK-SCHOLES)
# =====================================================================================

# Expiration et temps
DEFAULT_EXPIRY_DAYS = 30           # 30 jours d'expiration par défaut
MIN_TIME_TO_EXPIRY = 0.05          # Minimum 18 jours avant sortie forcée
MAX_TIME_TO_EXPIRY = 0.25          # Maximum 3 mois

# Paramètres Black-Scholes
RISK_FREE_RATE = 0.02              # Taux sans risque (2%)
MIN_VOLATILITY = 0.1               # Volatilité minimum (10%)
MAX_VOLATILITY = 3.0               # Volatilité maximum (300%)

# =====================================================================================
# OPTIMISATION ET PERFORMANCE
# =====================================================================================

# Taille de position adaptative
ADAPTIVE_POSITION_SIZING = True    # Ajuster taille selon performance récente
LOSS_RECOVERY_MODE = True          # Mode récupération après pertes

# Filtres de qualité
VOLATILITY_FILTER = True           # Filtre strict de volatilité
TREND_FILTER = True                # Éviter les tendances fortes
RSI_FILTER_MIN = 35                # RSI minimum
RSI_FILTER_MAX = 65                # RSI maximum

# =====================================================================================
# PARAMÈTRES DE BACKTEST
# =====================================================================================

OPTIMIZE_PARAMETERS = True         # Optimisation automatique
MAX_SPREAD = 0.002                # Spread maximum autorisé (0.2%)
MIN_PRICE_MOVEMENT = 0.00005       # Mouvement minimum pour validation

# =====================================================================================
# LOGGING ET OUTPUT
# =====================================================================================

LOG_LEVEL = 'INFO'                 # Niveau de logging (DEBUG, INFO, WARNING, ERROR)
SAVE_DETAILED_LOGS = True          # Sauvegarder logs détaillés
GENERATE_REPORTS = True            # Générer rapports automatiques
SHOW_PLOTS = True                  # Afficher graphiques

# Dossiers de sortie
OUTPUT_DIR = 'output'              # Dossier des résultats
LOGS_DIR = 'logs'                  # Dossier des logs

# =====================================================================================
# VALIDATION DES PARAMÈTRES
# =====================================================================================

def validate_config():
    """Valide la cohérence des paramètres de configuration"""
    errors = []
    warnings = []
    
    # Vérifications critiques
    if RISK_PER_TRADE > 0.05:
        errors.append(f"RISK_PER_TRADE trop élevé: {RISK_PER_TRADE:.1%} > 5%")
    
    if TAKE_PROFIT_MULTIPLIER <= STOP_LOSS_MULTIPLIER:
        errors.append("TAKE_PROFIT_MULTIPLIER doit être > STOP_LOSS_MULTIPLIER")
    
    if MAX_POSITIONS < 1:
        errors.append("MAX_POSITIONS doit être >= 1")
    
    # Avertissements
    if VOLATILITY_THRESHOLD < 30:
        warnings.append(f"VOLATILITY_THRESHOLD très bas: {VOLATILITY_THRESHOLD}%")
    
    if MAX_HEDGE_RATIO > 0.5:
        warnings.append(f"MAX_HEDGE_RATIO élevé: {MAX_HEDGE_RATIO:.1%}")
    
    return errors, warnings

# =====================================================================================
# PROFILS DE CONFIGURATION PRÉDÉFINIS
# =====================================================================================

PROFILES = {
    'CONSERVATIVE': {
        'RISK_PER_TRADE': 0.008,
        'VOLATILITY_THRESHOLD': 70,
        'MAX_POSITIONS': 2,
        'TAKE_PROFIT_MULTIPLIER': 1.2,
        'STOP_LOSS_MULTIPLIER': 0.5
    },
    
    'BALANCED': {
        'RISK_PER_TRADE': 0.012,
        'VOLATILITY_THRESHOLD': 55,
        'MAX_POSITIONS': 3,
        'TAKE_PROFIT_MULTIPLIER': 1.3,
        'STOP_LOSS_MULTIPLIER': 0.6
    },
    
    'AGGRESSIVE': {
        'RISK_PER_TRADE': 0.020,
        'VOLATILITY_THRESHOLD': 40,
        'MAX_POSITIONS': 5,
        'TAKE_PROFIT_MULTIPLIER': 1.5,
        'STOP_LOSS_MULTIPLIER': 0.8
    }
}

# Profil actuel (changez selon vos préférences de risque)
CURRENT_PROFILE = 'BALANCED'
