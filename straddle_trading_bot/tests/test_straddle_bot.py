# Tests Unitaires pour le Bot Straddle
# Validation des composants principaux

import sys
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Ajouter le dossier src au path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from config import *
from data_manager import DataManager
from straddle_strategy import StraddleStrategy, StraddlePosition, HedgeDirection

class TestConfiguration:
    """Tests de la configuration"""
    
    def test_validate_config(self):
        """Test de validation de la configuration"""
        errors, warnings = validate_config()
        assert isinstance(errors, list)
        assert isinstance(warnings, list)
        # La configuration par défaut ne doit pas avoir d'erreurs
        assert len(errors) == 0
    
    def test_risk_parameters(self):
        """Test des paramètres de risque"""
        assert 0 < RISK_PER_TRADE < 0.1  # Entre 0 et 10%
        assert INITIAL_CAPITAL > 0
        assert MAX_POSITIONS >= 1
        assert TAKE_PROFIT_MULTIPLIER > STOP_LOSS_MULTIPLIER
    
    def test_hedging_parameters(self):
        """Test des paramètres de hedging"""
        if ENABLE_HEDGING:
            assert 0 < HEDGE_THRESHOLD < 0.5
            assert 0 < MAX_HEDGE_RATIO < 1
            assert 0 < DELTA_NEUTRAL_TARGET < 1

class TestDataManager:
    """Tests du gestionnaire de données"""
    
    def test_data_manager_initialization(self):
        """Test d'initialisation du DataManager"""
        dm = DataManager()
        assert dm is not None
        assert hasattr(dm, 'exchange')
        assert hasattr(dm, 'data_cache')
    
    def test_data_validation(self):
        """Test de validation des données"""
        dm = DataManager()
        
        # Créer des données de test
        test_data = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [105, 106, 107],
            'low': [95, 96, 97],
            'close': [103, 104, 105],
            'volume': [1000, 1100, 1200]
        })
        
        # Les données valides doivent passer
        validated = dm._validate_price_consistency(test_data)
        assert len(validated) == len(test_data)
    
    def test_outlier_removal(self):
        """Test de suppression des outliers"""
        dm = DataManager()
        
        # Données avec outliers
        test_data = pd.DataFrame({
            'open': [100, 101, 0],  # 0 est un outlier
            'high': [105, 106, 1],
            'low': [95, 96, 0],
            'close': [103, 104, 0.5],
            'volume': [1000, 1100, 1200]
        })
        
        cleaned = dm._remove_outliers(test_data)
        # Les outliers doivent être supprimés
        assert len(cleaned) < len(test_data)

class TestStraddleStrategy:
    """Tests de la stratégie straddle"""
    
    def test_strategy_initialization(self):
        """Test d'initialisation de la stratégie"""
        strategy = StraddleStrategy()
        assert strategy.capital == INITIAL_CAPITAL
        assert strategy.max_risk_per_trade == INITIAL_CAPITAL * RISK_PER_TRADE
        assert len(strategy.positions) == 0
        assert len(strategy.hedge_positions) == 0
    
    def test_black_scholes_simulation(self):
        """Test de simulation Black-Scholes"""
        strategy = StraddleStrategy()
        
        # Test avec paramètres standards
        result = strategy.simulate_straddle_price(
            spot_price=50000,
            strike=50000,
            volatility=0.5,
            time_to_expiry=30/365
        )
        
        assert 'call_price' in result
        assert 'put_price' in result
        assert 'straddle_price' in result
        assert result['call_price'] > 0
        assert result['put_price'] > 0
        assert result['straddle_price'] > 0
        assert result['straddle_price'] == result['call_price'] + result['put_price']
    
    def test_black_scholes_expiry(self):
        """Test Black-Scholes à l'expiration"""
        strategy = StraddleStrategy()
        
        # À l'expiration (time_to_expiry = 0)
        result = strategy.simulate_straddle_price(
            spot_price=55000,
            strike=50000,
            volatility=0.5,
            time_to_expiry=0
        )
        
        # À l'expiration, seule la valeur intrinsèque compte
        expected_intrinsic = abs(55000 - 50000)
        assert result['straddle_price'] == expected_intrinsic
        assert result['time_value'] == 0
    
    def test_position_size_calculation(self):
        """Test de calcul de taille de position"""
        strategy = StraddleStrategy()
        
        # Test avec prix de straddle normal
        contracts = strategy.calculate_position_size(
            straddle_price=1000,
            signal_quality=0.8
        )
        
        assert contracts >= 1
        assert contracts <= 20
        assert isinstance(contracts, int)
        
        # Test avec prix très élevé
        contracts_high_price = strategy.calculate_position_size(
            straddle_price=10000,
            signal_quality=0.8
        )
        
        # Doit être limité par le capital
        assert contracts_high_price >= 1
    
    def test_signal_quality_calculation(self):
        """Test de calcul de qualité du signal"""
        strategy = StraddleStrategy()
        
        # Créer des données de test
        test_data = create_test_market_data()
        
        should_enter, signal_info = strategy.calculate_signal_quality(test_data)
        
        assert isinstance(should_enter, bool)
        assert isinstance(signal_info, dict)
        assert 'signal_quality' in signal_info
        assert 0 <= signal_info['signal_quality'] <= 1
        assert 'confidence' in signal_info
        assert signal_info['confidence'] in ['LOW', 'MEDIUM', 'HIGH']
    
    def test_hedge_decision(self):
        """Test de décision de hedge"""
        strategy = StraddleStrategy()
        
        # Créer une position de test
        position = StraddlePosition(
            entry_time=datetime.now(),
            expiry_time=datetime.now() + timedelta(days=30),
            entry_price=50000,
            strike=50000,
            entry_volatility=0.5,
            contracts=1,
            premium_paid=1000
        )
        
        # Test avec mouvement significatif (doit déclencher hedge)
        should_hedge, direction, size = strategy.should_hedge_position(position, 52000)
        
        if ENABLE_HEDGING:
            # Mouvement de 4% doit déclencher un hedge
            assert should_hedge == True
            assert direction in [HedgeDirection.LONG, HedgeDirection.SHORT]
            assert 0 < size <= MAX_HEDGE_RATIO
        else:
            assert should_hedge == False
    
    def test_position_management(self):
        """Test de gestion de position"""
        strategy = StraddleStrategy()
        
        # Créer une position de test
        position = StraddlePosition(
            entry_time=datetime.now() - timedelta(hours=1),
            expiry_time=datetime.now() + timedelta(days=29),
            entry_price=50000,
            strike=50000,
            entry_volatility=0.5,
            contracts=1,
            premium_paid=1000
        )
        
        strategy.positions.append(position)
        
        # Test de gestion normale
        action, info = strategy.manage_position(
            position, 50500, datetime.now(), 0.5
        )
        
        # Doit retourner une action valide
        from straddle_strategy import TradeAction
        assert action in TradeAction
        assert isinstance(info, dict)

class TestStraddlePosition:
    """Tests de la classe StraddlePosition"""
    
    def test_position_creation(self):
        """Test de création de position"""
        position = StraddlePosition(
            entry_time=datetime.now(),
            expiry_time=datetime.now() + timedelta(days=30),
            entry_price=50000,
            strike=50000,
            entry_volatility=0.5,
            contracts=1,
            premium_paid=1000
        )
        
        assert position.entry_price == 50000
        assert position.strike == 50000
        assert position.contracts == 1
        assert position.premium_paid == 1000
        assert len(position.hedge_positions) == 0

def create_test_market_data(length=200):
    """Crée des données de marché pour les tests"""
    dates = pd.date_range(start='2023-01-01', periods=length, freq='1H')
    
    # Simulation d'un mouvement de prix
    price_base = 50000
    price_changes = np.random.normal(0, 0.02, length)
    prices = [price_base]
    
    for change in price_changes[1:]:
        new_price = prices[-1] * (1 + change)
        prices.append(new_price)
    
    # Créer le DataFrame avec tous les champs requis
    data = pd.DataFrame({
        'open': prices,
        'high': [p * 1.01 for p in prices],
        'low': [p * 0.99 for p in prices],
        'close': prices,
        'volume': np.random.randint(1000, 10000, length)
    }, index=dates)
    
    # Ajouter les indicateurs techniques simplifiés
    data['returns'] = data['close'].pct_change()
    data['volatility'] = data['returns'].rolling(20).std() * np.sqrt(365 * 24)
    data['vol_percentile'] = data['volatility'].rolling(100, min_periods=1).rank(pct=True) * 100
    data['rsi'] = 50 + np.random.normal(0, 10, length)  # RSI simulé
    data['volume_sma'] = data['volume'].rolling(20).mean()
    data['volume_ratio'] = data['volume'] / data['volume_sma']
    data['sma_20'] = data['close'].rolling(20).mean()
    data['sma_50'] = data['close'].rolling(50).mean()
    data['price_position'] = np.random.uniform(0.2, 0.8, length)
    
    # Remplir les NaN
    data = data.fillna(method='bfill').fillna(method='ffill')
    
    return data

# Tests d'intégration
class TestIntegration:
    """Tests d'intégration du système complet"""
    
    def test_full_backtest_simulation(self):
        """Test complet de simulation de backtest"""
        # Créer des données de test
        test_data = create_test_market_data(1000)
        
        # Initialiser la stratégie
        strategy = StraddleStrategy()
        
        # Lancer un mini-backtest
        results = strategy.run_backtest(test_data.iloc[:500])  # Premier moitié des données
        
        # Vérifier les résultats
        assert 'performance_metrics' in results
        assert 'trades' in results
        assert 'daily_pnl' in results
        
        metrics = results['performance_metrics']
        assert 'total_trades' in metrics
        assert 'final_capital' in metrics
        assert 'total_return' in metrics

# Fixtures pytest
@pytest.fixture
def sample_market_data():
    """Fixture pour données de marché"""
    return create_test_market_data()

@pytest.fixture
def sample_strategy():
    """Fixture pour stratégie"""
    return StraddleStrategy()

# Tests de performance
class TestPerformance:
    """Tests de performance et benchmarks"""
    
    def test_backtest_speed(self):
        """Test de vitesse d'exécution du backtest"""
        import time
        
        data = create_test_market_data(2000)
        strategy = StraddleStrategy()
        
        start_time = time.time()
        results = strategy.run_backtest(data.iloc[:1000])
        execution_time = time.time() - start_time
        
        # Le backtest ne doit pas prendre plus de 30 secondes pour 1000 barres
        assert execution_time < 30
        print(f"Temps d'exécution backtest: {execution_time:.2f}s")
    
    def test_memory_usage(self):
        """Test d'utilisation mémoire"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # Exécuter quelques opérations
        data = create_test_market_data(5000)
        strategy = StraddleStrategy()
        results = strategy.run_backtest(data.iloc[:2000])
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        
        # Ne doit pas utiliser plus de 500MB
        assert memory_used < 500
        print(f"Mémoire utilisée: {memory_used:.1f}MB")

if __name__ == "__main__":
    # Lancer les tests
    pytest.main([__file__, "-v", "--tb=short"])
