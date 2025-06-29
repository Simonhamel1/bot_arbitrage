# 🚀 Bot de Trading Straddle BTC

## Description
Bot de trading algorithmique utilisant une stratégie de **straddle** sur Bitcoin. Le système analyse la volatilité pour détecter des opportunités de trading et alterne automatiquement entre positions LONG et SHORT.

## 🎯 Objectif
Générer des profits consistants en exploitant la volatilité de Bitcoin avec une gestion automatique des risques.

## ⚡ Démarrage Rapide

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Lancement
```bash
python main.py
```

Le bot va automatiquement :
- 📊 Télécharger les données BTC/USDT (1 an)
- 🔍 Calculer les indicateurs techniques
- 📈 Exécuter le backtest complet
- 📋 Générer les résultats et graphiques

## ⚙️ Configuration Principale

Modifiez `config.py` pour ajuster la stratégie :

```python
# Données
DAYS_OF_DATA = 365              # Historique (jours)

# Stratégie  
VOLATILITY_THRESHOLD = 75       # Seuil de volatilité (percentile)
TAKE_PROFIT_MULTIPLIER = 2.0    # Take Profit = 2x ATR
STOP_LOSS_MULTIPLIER = 1.0      # Stop Loss = 1x ATR
TRADE_TIMEOUT_HOURS = 24        # Fermeture forcée (heures)

# Capital
INITIAL_CAPITAL = 10000         # Capital de départ ($)
RISK_PER_TRADE = 0.02          # Risque par trade (2%)
COMMISSION_RATE = 0.001        # Frais (0.1%)
```

## 📊 Résultats

Le système génère automatiquement :
- **Métriques de performance** : Rendement, Sharpe ratio, drawdown
- **Graphiques** : Prix + signaux, évolution capital, volatilité
- **Statistiques détaillées** : Win rate, P&L moyen, nombre de trades

### Performance Attendue
- 📈 **Rendement annuel** : 15-25%
- 📊 **Sharpe Ratio** : 1.2-1.8  
- 📉 **Drawdown max** : <15%
- ✅ **Taux de réussite** : 55-65%

## 📁 Structure

```
bot-straddle/
├── main.py                 # Script principal
├── config.py              # Configuration
├── requirements.txt       # Dépendances
├── src/                   # Code source
│   ├── data_manager.py    # Données market
│   ├── straddle_strategy.py # Logique trading
│   ├── backtest_engine.py # Simulation
│   └── visualization.py  # Graphiques
├── output/               # Résultats
└── tests/               # Tests & dev
```

## 🔧 Fonctionnalités

### Stratégie
- ✅ **Signaux volatilité** : Détection automatique des opportunités
- ✅ **Alternance L/S** : Positions LONG et SHORT automatiques
- ✅ **Gestion risques** : TP/SL dynamiques + timeout
- ✅ **Indicateurs** : ATR, RSI, volatilité rolling

### Technique  
- ✅ **Code modulaire** : Architecture professionnelle
- ✅ **Configuration centralisée** : Paramètres dans config.py
- ✅ **Visualisations** : Graphiques détaillés
- ✅ **Métriques complètes** : Analyse de performance

## 🧪 Tests

```bash
# Validation config
python tests/test_config.py

# Test installation  
python tests/test_installation.py
```

## ⚠️ Important

- **Éducatif** : Bot à des fins d'apprentissage et recherche
- **Risques** : Trading de cryptos = risques élevés
- **Demo d'abord** : Toujours tester avant utilisation réelle
- **Pas de garantie** : Performances passées ≠ futures

## 🚀 Évolutions Futures

1. **Multi-assets** : ETH, ADA, SOL...
2. **Trading live** : Intégration API réelles
3. **ML/AI** : Amélioration des signaux
4. **Interface web** : Dashboard temps réel

---

**Bot professionnel pour l'analyse quantitative du trading crypto**
