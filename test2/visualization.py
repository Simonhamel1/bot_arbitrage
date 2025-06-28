import matplotlib.pyplot as plt
import numpy as np

def plot_strategy_results(timestamps, price1, price2, spread, cumulative_returns, 
                         mu, upper_threshold, lower_threshold, symbol1, symbol2):
    """
    Affiche les graphiques de la stratégie
    
    Args:
        timestamps (pandas.Series): Horodatages des données
        price1 (numpy.ndarray): Prix du premier actif
        price2 (numpy.ndarray): Prix du deuxième actif
        spread (numpy.ndarray): Valeurs du spread
        cumulative_returns (numpy.ndarray): Rendements cumulés
        mu (float): Moyenne du spread
        upper_threshold (float): Seuil supérieur
        lower_threshold (float): Seuil inférieur
        symbol1 (str): Symbole du premier actif
        symbol2 (str): Symbole du deuxième actif
    """
    plt.figure(figsize=(12, 8))

    # Graphique des prix
    plt.subplot(3, 1, 1)
    plt.plot(timestamps, price1, label=symbol1)
    plt.plot(timestamps, price2, label=symbol2)
    plt.title('Prix des actifs')
    plt.legend()

    # Graphique du spread
    plt.subplot(3, 1, 2)
    plt.plot(timestamps, spread, label='Spread')
    plt.axhline(mu, color='black', linestyle='--', label='Moyenne')
    plt.axhline(upper_threshold, color='red', linestyle='--', label='Seuil supérieur')
    plt.axhline(lower_threshold, color='green', linestyle='--', label='Seuil inférieur')
    plt.title('Spread et seuils')
    plt.legend()

    # Graphique des rendements
    plt.subplot(3, 1, 3)
    plt.plot(timestamps[1:], cumulative_returns, label='Rendement cumulé')
    plt.title('Performance de la stratégie')
    plt.legend()

    plt.tight_layout()
    plt.show()

def save_strategy_results(timestamps, price1, price2, spread, signals, cumulative_returns, filename='results.png'):
    """
    Sauvegarde les graphiques de la stratégie dans un fichier
    
    Args:
        timestamps (pandas.Series): Horodatages des données
        price1 (numpy.ndarray): Prix du premier actif
        price2 (numpy.ndarray): Prix du deuxième actif
        spread (numpy.ndarray): Valeurs du spread
        signals (numpy.ndarray): Signaux de trading
        cumulative_returns (numpy.ndarray): Rendements cumulés
        filename (str): Nom du fichier de sauvegarde
    """
    plt.figure(figsize=(12, 10))
    
    # Graphique des prix
    plt.subplot(4, 1, 1)
    plt.plot(timestamps, price1, label='Asset 1')
    plt.plot(timestamps, price2, label='Asset 2')
    plt.title('Prix des actifs')
    plt.legend()
    
    # Graphique du spread
    plt.subplot(4, 1, 2)
    plt.plot(timestamps, spread)
    plt.title('Spread')
    
    # Graphique des signaux
    plt.subplot(4, 1, 3)
    plt.plot(timestamps, signals)
    plt.title('Signaux de trading')
    
    # Graphique des rendements
    plt.subplot(4, 1, 4)
    plt.plot(timestamps[1:], cumulative_returns)
    plt.title('Rendement cumulé')
    
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
