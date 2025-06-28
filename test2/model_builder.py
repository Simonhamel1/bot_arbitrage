import numpy as np
from sklearn.linear_model import LinearRegression

def build_pair_regression_model(price1, price2):
    """
    Construit un modèle de régression linéaire entre deux séries de prix
    
    Args:
        price1 (numpy.ndarray): Prix du premier actif
        price2 (numpy.ndarray): Prix du deuxième actif
    
    Returns:
        tuple: (beta, alpha, spread)
            - beta: coefficient de la régression
            - alpha: constante de la régression
            - spread: écart entre les prix réels et le modèle
    """
    model = LinearRegression()
    model.fit(price2.reshape(-1, 1), price1)
    beta = model.coef_[0]
    alpha = model.intercept_
    
    # Calcul du spread
    spread = price1 - (beta * price2 + alpha)
    
    return beta, alpha, spread

def calculate_spread_statistics(spread):
    """
    Calcule les statistiques du spread
    
    Args:
        spread (numpy.ndarray): Valeurs du spread
    
    Returns:
        tuple: (mu, sigma, upper_threshold, lower_threshold)
            - mu: moyenne du spread
            - sigma: écart-type du spread
            - upper_threshold: seuil supérieur
            - lower_threshold: seuil inférieur
    """
    from config import THRESHOLD_MULTIPLIER
    
    mu = np.mean(spread)
    sigma = np.std(spread)
    upper_threshold = mu + THRESHOLD_MULTIPLIER * sigma
    lower_threshold = mu - THRESHOLD_MULTIPLIER * sigma
    
    return mu, sigma, upper_threshold, lower_threshold
