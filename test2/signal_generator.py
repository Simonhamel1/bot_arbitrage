import numpy as np

def generate_trading_signals(spread, mu, upper_threshold, lower_threshold):
    """
    Génère des signaux de trading basés sur le spread
    
    Args:
        spread (numpy.ndarray): Valeurs du spread
        mu (float): Moyenne du spread
        upper_threshold (float): Seuil supérieur
        lower_threshold (float): Seuil inférieur
    
    Returns:
        numpy.ndarray: Signaux de trading (1: long, -1: short, 0: pas de position)
    """
    from config import CLOSE_AT_MEAN_RATIO, MAX_POSITION_DURATION, USE_STOP_LOSS, STOP_LOSS_MULTIPLIER
    
    signals = np.zeros(len(spread))
    position = 0
    position_start = 0
    
    # Calcul des seuils de sortie dynamiques
    mean_exit_upper = mu + (upper_threshold - mu) * CLOSE_AT_MEAN_RATIO
    mean_exit_lower = mu - (mu - lower_threshold) * CLOSE_AT_MEAN_RATIO
    
    # Calcul des seuils de stop-loss
    stop_loss_upper = upper_threshold * STOP_LOSS_MULTIPLIER
    stop_loss_lower = lower_threshold / STOP_LOSS_MULTIPLIER
    
    for i in range(1, len(spread)):
        # Vérification de la durée de la position
        position_duration = i - position_start if position != 0 else 0
        
        # Vérifier si la position doit être fermée par time-out
        if position != 0 and position_duration >= MAX_POSITION_DURATION:
            position = 0
            position_start = 0
        
        # Vérifier le stop-loss si activé
        if USE_STOP_LOSS and position == 1 and spread[i] < stop_loss_lower:
            position = 0  # Stop-loss pour une position long
        elif USE_STOP_LOSS and position == -1 and spread[i] > stop_loss_upper:
            position = 0  # Stop-loss pour une position short
        
        # Logique principale d'entrée/sortie
        if position == 0:
            if spread[i] > upper_threshold:
                position = -1  # Short quand le spread est au-dessus du seuil supérieur
                position_start = i
            elif spread[i] < lower_threshold:
                position = 1   # Long quand le spread est en-dessous du seuil inférieur
                position_start = i
        elif position == 1 and spread[i] >= mean_exit_lower:
            position = 0       # Ferme la position long quand le spread revient vers la moyenne
        elif position == -1 and spread[i] <= mean_exit_upper:
            position = 0       # Ferme la position short quand le spread revient vers la moyenne
        
        signals[i] = position
    
    return signals

def calculate_strategy_returns(signals, spread):
    """
    Calcule les rendements de la stratégie
    
    Args:
        signals (numpy.ndarray): Signaux de trading
        spread (numpy.ndarray): Valeurs du spread
    
    Returns:
        tuple: (strategy_returns, cumulative_returns)
            - strategy_returns: Rendements de la stratégie
            - cumulative_returns: Rendements cumulés
    """
    from config import TRANSACTION_FEE
    
    # Calcul des rendements sur la variation du spread
    spread_returns = np.diff(spread)
    
    # Détection des changements de position (entrée et sortie)
    position_changes = np.diff(signals)
    
    # Calcul des frais de transaction (à chaque changement de position)
    transaction_costs = np.zeros_like(position_changes)
    transaction_costs[position_changes != 0] = TRANSACTION_FEE
    
    # Les signaux sont décalés d'une période pour éviter le look-ahead bias
    strategy_returns = signals[:-1] * (-spread_returns) - transaction_costs
    
    # Calcul des rendements cumulés
    cumulative_returns = np.cumsum(strategy_returns)
    
    return strategy_returns, cumulative_returns
