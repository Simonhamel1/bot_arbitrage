# Bot de Trading avec Stratégie de Straddle

Ce projet implémente une stratégie de straddle pour les marchés de cryptomonnaies, exploitant les périodes de forte volatilité pour générer des profits bidirectionnels.

## Structure du Projet

```
test2/
├── analyze_performance.py     # Analyse de performance
├── config.py                  # Configuration du projet
├── data_fetcher.py            # Récupération des données de marché
├── main.py                    # Script principal
├── requirements.txt           # Dépendances
├── run_continuous.py          # Exécution en continu
├── straddle_strategy.py       # Logique de la stratégie straddle
├── straddle_trader.py         # Exécution des ordres de trading
└── straddle_visualization.py  # Visualisation des résultats
```

## Installation

1. Clonez ce dépôt:
```
git clone <url-du-repo>
cd <dossier-du-repo>/test2
```

2. Installez les dépendances:
```
pip install -r requirements.txt  
```
ou

```
conda install -r requirements.txt  
```


## Utilisation

Exécutez le script principal:
```
python main.py
```

Pour une exécution continue:
```
python run_continuous.py
```

Pour optimiser les paramètres de la stratégie:
```
python optimize.py
```

Pour analyser la performance de la stratégie:
```
python analyze_performance.py
```

## Fonctionnement

La stratégie de straddle fonctionne comme suit:

1. Surveillance de la volatilité du marché pour un actif (par défaut BTC/USDT)
2. Détection des périodes de forte volatilité en utilisant divers indicateurs (écart-type, ATR)
3. Lorsqu'une volatilité élevée est détectée, ouverture simultanée de positions longue et courte (straddle)
4. Définition de niveaux de prise de profit et stop-loss pour chaque position
5. Fermeture des positions lorsqu'elles atteignent leur objectif ou leur stop-loss
6. Analyse des performances et ajustement des paramètres

Cette stratégie est particulièrement efficace dans les marchés volatils et en période d'incertitude, où le prix peut connaître des mouvements importants sans direction claire.

## Configuration

Vous pouvez modifier les paramètres de la stratégie dans le fichier `config.py`:

- `EXCHANGE_ID`: Plateforme d'échange à utiliser (par défaut: 'binance')
- `SYMBOL`: Actif sur lequel appliquer la stratégie (par défaut: 'BTC/USDT')
- `TIMEFRAME`: Intervalle de temps pour les données (par défaut: '5m')
- `VOLATILITY_PERIOD`: Période pour le calcul de la volatilité
- `ENTRY_VOLATILITY_PERCENTILE`: Percentile de volatilité pour l'entrée en position
- `TAKE_PROFIT_PCT`: Pourcentage de prise de profit
- `STOP_LOSS_PCT`: Pourcentage de stop loss
- `POSITION_SIZE_PCT`: Taille de position en pourcentage du capital
- `MAX_POSITION_DURATION`: Durée maximale d'une position
- `TRANSACTION_FEE`: Frais de transaction

## Avertissement

Ce bot est fourni à des fins éducatives uniquement. Le trading de cryptomonnaies comporte des risques financiers importants.
