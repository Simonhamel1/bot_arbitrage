# 🚀 Backtesting Straddle BTC - Version Simple

Un projet **minimaliste** de backtesting d'une stratégie de straddle sur BTC/USDT.

## 📋 Description

Ce projet implémente une stratégie de straddle simple :
- **Signal** : Quand la volatilité BTC dépasse un seuil (percentile configurable)
- **Position** : Alternance automatique entre LONG et SHORT
- **Sorties** : Take Profit, Stop Loss, ou timeout après 24h
- **Résultats** : 3 graphiques simples + statistiques

## 🛠️ Installation

1. **Cloner/télécharger** le projet
2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

## ⚡ Utilisation

**Lancer le backtest :**
```bash
python main.py
```

Le programme va :
1. Télécharger les données BTC/USDT (dernière année)
2. Calculer les indicateurs (volatilité, ATR, RSI)
3. Détecter les signaux de trading
4. Exécuter le backtest
5. Afficher les résultats
6. Générer 3 graphiques dans le dossier `output/`

## ⚙️ Configuration

**Modifiez les paramètres dans `config.py` :**

```python
# Données
DAYS_OF_DATA = 365              # Nombre de jours de données

# Stratégie
VOLATILITY_THRESHOLD = 75       # Seuil de volatilité (percentile)
TAKE_PROFIT_MULTIPLIER = 2.0    # TP = 2x ATR
STOP_LOSS_MULTIPLIER = 1.0      # SL = 1x ATR
TRADE_TIMEOUT_HOURS = 24        # Fermeture forcée après 24h

# Capital
INITIAL_CAPITAL = 10000         # Capital de départ
RISK_PER_TRADE = 0.02          # 2% de risque par trade
COMMISSION_RATE = 0.001        # 0.1% de frais
```

## 📊 Graphiques Générés

1. **Prix + Signaux** : BTC/USDT avec points d'entrée
2. **Évolution du Capital** : Performance de la stratégie
3. **Volatilité** : Indicateur utilisé pour les signaux

## 📁 Structure

```
test3/
├── config.py              # Configuration des paramètres
├── data_manager.py        # Récupération des données BTC
├── straddle_strategy.py   # Logique de trading
├── visualization.py      # Génération des graphiques
├── main.py               # Script principal
├── requirements.txt      # Dépendances Python
└── output/              # Dossier des résultats
```

## 🎯 Simplicité

- **1 seul symbole** : BTC/USDT uniquement
- **1 seul signal** : Basé sur la volatilité
- **Stratégie simple** : Alternance LONG/SHORT
- **Configuration facile** : Tout dans `config.py`
- **Résultats clairs** : 3 graphiques + statistiques

Parfait pour comprendre et modifier une stratégie de trading simple !
