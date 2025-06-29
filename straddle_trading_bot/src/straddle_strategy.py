# Stratégie Straddle Optimisée avec Hedging Dynamique
# Bot de trading professionnel pour options straddle

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from config import *

class TradeAction(Enum):
    """Actions possibles pour une position"""
    HOLD = "HOLD"
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    TIME_DECAY = "TIME_DECAY"
    TIMEOUT = "TIMEOUT"
    VOL_COLLAPSE = "VOL_COLLAPSE"

class HedgeDirection(Enum):
    """Directions de hedge"""
    LONG = "LONG"
    SHORT = "SHORT"
    NONE = "NONE"

@dataclass
class StraddlePosition:
    """Structure d'une position straddle"""
    entry_time: datetime
    expiry_time: datetime
    entry_price: float
    strike: float
    entry_volatility: float
    contracts: int
    premium_paid: float
    current_value: float = 0.0
    unrealized_pnl: float = 0.0
    pnl_percentage: float = 0.0
    hedge_positions: List = None
    entry_confidence: str = "MEDIUM"
    
    def __post_init__(self):
        if self.hedge_positions is None:
            self.hedge_positions = []

@dataclass 
class HedgePosition:
    """Structure d'une position de hedge"""
    direction: HedgeDirection
    entry_time: datetime
    entry_price: float
    size_ratio: float
    parent_position_id: str
    current_pnl: float = 0.0
    active: bool = True

@dataclass
class TradeResult:
    """Résultat d'un trade"""
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    strike: float
    premium_paid: float
    exit_value: float
    pnl: float
    pnl_percentage: float
    contracts: int
    exit_reason: str
    holding_time_hours: float
    hedge_count: int = 0

class StraddleStrategy:
    """
    Stratégie Straddle optimisée avec:
    - Gestion du risque maximale (perte = prime uniquement)
    - Hedging dynamique Long/Short
    - Optimisation continue des paramètres
    - Black-Scholes pour simulation des prix d'options
    """
    
    def __init__(self):
        self.positions: List[StraddlePosition] = []
        self.hedge_positions: List[HedgePosition] = []
        self.trades_history: List[TradeResult] = []
        
        # Gestion du capital
        self.capital = INITIAL_CAPITAL
        self.max_risk_per_trade = INITIAL_CAPITAL * RISK_PER_TRADE
        
        # Statistiques de performance
        self.consecutive_losses = 0
        self.daily_pnl_history = []
        self.performance_metrics = {}
        
        # Configuration logging
        self.logger = logging.getLogger(__name__)
        
    def simulate_straddle_price(
        self, 
        spot_price: float, 
        strike: float, 
        volatility: float, 
        time_to_expiry: float
    ) -> Dict[str, float]:
        """
        Simule le prix d'un straddle avec Black-Scholes
        
        Args:
            spot_price: Prix actuel du sous-jacent
            strike: Prix d'exercice
            volatility: Volatilité implicite
            time_to_expiry: Temps jusqu'à expiration (en années)
            
        Returns:
            Dict avec les prix call, put et straddle
        """
        if time_to_expiry <= 0:
            call_value = max(0, spot_price - strike)
            put_value = max(0, strike - spot_price)
            return {
                'call_price': call_value,
                'put_price': put_value,
                'straddle_price': call_value + put_value,
                'time_value': 0.0,
                'intrinsic_value': call_value + put_value
            }
        
        # Ajustement de la volatilité dans les limites
        volatility = max(MIN_VOLATILITY, min(MAX_VOLATILITY, volatility))
        
        # Paramètres Black-Scholes
        d1 = (np.log(spot_price / strike) + 
              (RISK_FREE_RATE + 0.5 * volatility**2) * time_to_expiry) / \
             (volatility * np.sqrt(time_to_expiry))
        d2 = d1 - volatility * np.sqrt(time_to_expiry)
        
        # Fonction de distribution normale cumulée (approximation)
        def norm_cdf(x):
            return 0.5 * (1 + np.sign(x) * np.sqrt(1 - np.exp(-2 * x**2 / np.pi)))
        
        # Prix du call
        call_price = (spot_price * norm_cdf(d1) - 
                     strike * np.exp(-RISK_FREE_RATE * time_to_expiry) * norm_cdf(d2))
        
        # Prix du put (parité call-put)
        put_price = (call_price - spot_price + 
                    strike * np.exp(-RISK_FREE_RATE * time_to_expiry))
        
        # Assurer prix positifs
        call_price = max(0.01, call_price)
        put_price = max(0.01, put_price)
        straddle_price = call_price + put_price
        
        # Valeurs intrinsèque et temporelle
        intrinsic_value = max(0, abs(spot_price - strike))
        time_value = max(0, straddle_price - intrinsic_value)
        
        return {
            'call_price': call_price,
            'put_price': put_price,
            'straddle_price': straddle_price,
            'time_value': time_value,
            'intrinsic_value': intrinsic_value
        }
    
    def calculate_signal_quality(self, data: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """
        Évalue la qualité du signal d'entrée
        
        Args:
            data: DataFrame avec données historiques
            
        Returns:
            Tuple (should_enter, signal_info)
        """
        if len(data) < 100:
            return False, {'reason': 'Insufficient data'}
        
        latest = data.iloc[-1]
        recent_data = data.tail(20)
        
        # Critères d'évaluation
        criteria = {}
        
        # 1. Volatilité élevée
        criteria['volatility'] = latest['vol_percentile'] >= VOLATILITY_THRESHOLD
        
        # 2. Consolidation de prix (sweet spot pour straddle)
        price_range = (recent_data['high'].max() - recent_data['low'].min()) / latest['close']
        criteria['consolidation'] = 0.02 < price_range < MAX_PRICE_RANGE
        
        # 3. RSI neutre (pas de momentum directionnel fort)
        criteria['rsi_neutral'] = RSI_FILTER_MIN < latest['rsi'] < RSI_FILTER_MAX
        
        # 4. Volume exceptionnel
        criteria['volume'] = latest['volume_ratio'] > MIN_VOLUME_RATIO
        
        # 5. Volatilité en hausse (momentum)
        vol_trend = latest['volatility'] > data['volatility'].rolling(10).mean().iloc[-1]
        criteria['vol_momentum'] = vol_trend
        
        # 6. Pas de tendance forte (favorable au straddle)
        if TREND_FILTER:
            sma_ratio = abs(latest['sma_20'] - latest['sma_50']) / latest['close']
            criteria['no_strong_trend'] = sma_ratio < 0.03
        else:
            criteria['no_strong_trend'] = True
        
        # 7. Position dans le range (ni cassure ni support/résistance)
        criteria['price_position'] = 0.2 < latest['price_position'] < 0.8
        
        # Calcul du score de qualité
        score = sum(criteria.values()) / len(criteria)
        
        # Informations détaillées du signal
        signal_info = {
            'signal_quality': score,
            'volatility_percentile': latest['vol_percentile'],
            'price_range': price_range,
            'rsi': latest['rsi'],
            'volume_ratio': latest['volume_ratio'],
            'volatility': latest['volatility'],
            'criteria_met': sum(criteria.values()),
            'total_criteria': len(criteria),
            'criteria_details': criteria
        }
        
        # Déterminer la confiance
        if score >= 0.85:
            signal_info['confidence'] = 'HIGH'
        elif score >= 0.75:
            signal_info['confidence'] = 'MEDIUM'
        else:
            signal_info['confidence'] = 'LOW'
        
        # Décision d'entrée
        should_enter = score >= MIN_SIGNAL_QUALITY
        
        return should_enter, signal_info
    
    def calculate_position_size(self, straddle_price: float, signal_quality: float) -> int:
        """
        Calcule la taille optimale de la position
        
        Args:
            straddle_price: Prix du straddle
            signal_quality: Qualité du signal (0-1)
            
        Returns:
            Nombre de contrats
        """
        # Taille de base basée sur le risque
        base_contracts = int(self.max_risk_per_trade / straddle_price)
        
        if ADAPTIVE_POSITION_SIZING:
            # Ajustement selon la performance récente
            if self.consecutive_losses >= 2:
                adjustment = 0.5  # Réduire après pertes
            elif signal_quality > 0.85:
                adjustment = 1.2  # Augmenter pour signaux excellents
            else:
                adjustment = 1.0
            
            contracts = int(base_contracts * adjustment)
        else:
            contracts = base_contracts
        
        # Limites de sécurité
        return max(1, min(contracts, 20))
    
    def should_hedge_position(
        self, 
        position: StraddlePosition, 
        current_price: float
    ) -> Tuple[bool, HedgeDirection, float]:
        """
        Détermine si une position doit être hedgée
        
        Args:
            position: Position à évaluer
            current_price: Prix actuel
            
        Returns:
            Tuple (should_hedge, direction, size_ratio)
        """
        if not ENABLE_HEDGING:
            return False, HedgeDirection.NONE, 0.0
        
        # Calcul du mouvement depuis l'entrée
        price_move = (current_price - position.entry_price) / position.entry_price
        
        # Seuil de hedge atteint ?
        if abs(price_move) < HEDGE_THRESHOLD:
            return False, HedgeDirection.NONE, 0.0
        
        # Direction du hedge (opposée au mouvement)
        direction = HedgeDirection.SHORT if price_move > 0 else HedgeDirection.LONG
        
        # Taille du hedge proportionnelle au mouvement
        size_ratio = min(MAX_HEDGE_RATIO, abs(price_move) * 2)
        
        return True, direction, size_ratio
    
    def execute_hedge_position(
        self, 
        position: StraddlePosition, 
        direction: HedgeDirection, 
        size_ratio: float, 
        current_price: float, 
        current_time: datetime
    ) -> HedgePosition:
        """
        Exécute une position de hedge
        
        Args:
            position: Position parent
            direction: Direction du hedge
            size_ratio: Taille relative du hedge
            current_price: Prix d'entrée du hedge
            current_time: Timestamp
            
        Returns:
            Position de hedge créée
        """
        hedge = HedgePosition(
            direction=direction,
            entry_time=current_time,
            entry_price=current_price,
            size_ratio=size_ratio,
            parent_position_id=str(id(position))
        )
        
        position.hedge_positions.append(hedge)
        self.hedge_positions.append(hedge)
        
        self.logger.info(f"🛡️ Hedge {direction.value} exécuté: {size_ratio:.1%} @ ${current_price:,.2f}")
        
        return hedge
    
    def manage_position(
        self, 
        position: StraddlePosition, 
        current_price: float, 
        current_time: datetime, 
        current_volatility: float
    ) -> Tuple[TradeAction, Dict[str, Any]]:
        """
        Gère une position existante
        
        Args:
            position: Position à gérer
            current_price: Prix actuel
            current_time: Timestamp actuel
            current_volatility: Volatilité actuelle
            
        Returns:
            Tuple (action, exit_info)
        """
        # Calcul du temps écoulé et restant
        time_elapsed_hours = (current_time - position.entry_time).total_seconds() / 3600
        time_to_expiry = max(0.001, (position.expiry_time - current_time).total_seconds() / (365.25 * 24 * 3600))
        
        # Mise à jour de la valeur actuelle
        current_straddle = self.simulate_straddle_price(
            current_price, position.strike, current_volatility, time_to_expiry
        )
        
        position.current_value = current_straddle['straddle_price'] * position.contracts
        position.unrealized_pnl = position.current_value - position.premium_paid
        position.pnl_percentage = (position.unrealized_pnl / position.premium_paid) * 100
        
        # Vérifier opportunité de hedge
        should_hedge, hedge_direction, hedge_size = self.should_hedge_position(position, current_price)
        if should_hedge and not any(h.active for h in position.hedge_positions):
            self.execute_hedge_position(position, hedge_direction, hedge_size, current_price, current_time)
        
        # Critères de sortie
        
        # 1. Take Profit
        tp_threshold = (TAKE_PROFIT_MULTIPLIER - 1) * 100
        if position.pnl_percentage >= tp_threshold:
            return TradeAction.TAKE_PROFIT, {
                'reason': f'Take profit atteint: {position.pnl_percentage:.1f}%',
                'pnl_pct': position.pnl_percentage,
                'holding_time': time_elapsed_hours
            }
        
        # 2. Stop Loss (adaptatif)
        sl_threshold = -STOP_LOSS_MULTIPLIER * 100
        if DYNAMIC_STOP_LOSS:
            # SL plus strict si time decay élevé
            time_decay_factor = current_straddle['time_value'] / current_straddle['straddle_price']
            if time_decay_factor < 0.3:  # Peu de valeur temps restante
                sl_threshold *= 0.8
            
            # SL plus strict après pertes consécutives
            if self.consecutive_losses >= 2:
                sl_threshold *= 0.7
        
        if position.pnl_percentage <= sl_threshold:
            return TradeAction.STOP_LOSS, {
                'reason': f'Stop loss: {position.pnl_percentage:.1f}%',
                'pnl_pct': position.pnl_percentage,
                'holding_time': time_elapsed_hours,
                'sl_threshold': sl_threshold
            }
        
        # 3. Time decay critique
        if time_to_expiry < MIN_TIME_TO_EXPIRY and position.pnl_percentage < -30:
            return TradeAction.TIME_DECAY, {
                'reason': 'Time decay critique',
                'pnl_pct': position.pnl_percentage,
                'time_remaining': time_to_expiry
            }
        
        # 4. Timeout
        timeout_hours = TRADE_TIMEOUT_HOURS
        if position.entry_confidence == 'HIGH':
            timeout_hours *= 1.5  # Plus de temps pour signaux excellents
        
        if time_elapsed_hours >= timeout_hours:
            return TradeAction.TIMEOUT, {
                'reason': f'Timeout: {time_elapsed_hours:.1f}h',
                'pnl_pct': position.pnl_percentage,
                'holding_time': time_elapsed_hours
            }
        
        # 5. Effondrement de la volatilité
        vol_ratio = current_volatility / position.entry_volatility
        if vol_ratio < 0.4:  # Volatilité chute de plus de 60%
            return TradeAction.VOL_COLLAPSE, {
                'reason': f'Volatilité effondrée: {vol_ratio:.1%}',
                'pnl_pct': position.pnl_percentage,
                'vol_ratio': vol_ratio
            }
        
        # Continuer à tenir la position
        return TradeAction.HOLD, {}
    
    def should_stop_trading(self) -> Tuple[bool, str]:
        """
        Détermine si le trading doit être arrêté (gestion des risques)
        
        Returns:
            Tuple (should_stop, reason)
        """
        # Arrêt après pertes consécutives
        if self.consecutive_losses >= MAX_CONSECUTIVE_LOSSES:
            return True, f"Trop de pertes consécutives: {self.consecutive_losses}"
        
        # Arrêt si perte quotidienne dépasse le seuil
        daily_loss = (INITIAL_CAPITAL - self.capital) / INITIAL_CAPITAL
        if daily_loss > MAX_DAILY_LOSS:
            return True, f"Perte quotidienne {daily_loss:.1%} > {MAX_DAILY_LOSS:.1%}"
        
        # Arrêt si capital insuffisant
        if self.capital < self.max_risk_per_trade * 2:
            return True, "Capital insuffisant pour continuer"
        
        return False, ""
    
    def run_backtest(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Lance le backtest complet de la stratégie
        
        Args:
            data: Données historiques
            
        Returns:
            Résultats détaillés du backtest
        """
        self.logger.info("🚀 Démarrage backtest stratégie straddle")
        self.logger.info(f"💰 Capital initial: ${self.capital:,.2f}")
        self.logger.info(f"🎯 Risque par trade: {RISK_PER_TRADE:.1%}")
        
        results = {
            'trades': [],
            'daily_pnl': [],
            'positions_log': [],
            'hedge_opportunities': [],
            'performance_metrics': {}
        }
        
        # Boucle principale du backtest
        for i in range(100, len(data)):  # Commencer après 100 barres pour les indicateurs
            current_time = data.index[i]
            current_data = data.iloc[:i+1]
            current_price = data.iloc[i]['close']
            current_vol = data.iloc[i]['volatility']
            
            # Vérifier si on doit arrêter le trading
            should_stop, stop_reason = self.should_stop_trading()
            if should_stop:
                self.logger.warning(f"⚠️ Arrêt du trading: {stop_reason}")
                break
            
            # Gérer les positions existantes
            positions_to_close = []
            
            for j, position in enumerate(self.positions):
                action, exit_info = self.manage_position(
                    position, current_price, current_time, current_vol
                )
                
                if action != TradeAction.HOLD:
                    # Clôturer la position
                    trade_result = self._close_position(position, current_price, current_time, action, exit_info)
                    results['trades'].append(trade_result)
                    positions_to_close.append(j)
            
            # Supprimer les positions fermées
            for j in reversed(positions_to_close):
                del self.positions[j]
            
            # Chercher de nouvelles opportunités
            if len(self.positions) < MAX_POSITIONS:
                should_enter, signal_info = self.calculate_signal_quality(current_data)
                
                if should_enter and self.capital > self.max_risk_per_trade:
                    self._open_new_position(current_price, current_time, current_vol, signal_info, results)
            
            # Enregistrer les métriques quotidiennes
            self._record_daily_metrics(current_time, results)
        
        # Clôturer les positions restantes
        self._close_remaining_positions(data, results)
        
        # Calculer les métriques finales
        self._calculate_final_metrics(results)
        
        self._log_backtest_summary(results)
        
        return results
    
    def _close_position(
        self, 
        position: StraddlePosition, 
        exit_price: float, 
        exit_time: datetime, 
        action: TradeAction, 
        exit_info: Dict
    ) -> TradeResult:
        """Clôture une position et met à jour le capital"""
        # Mettre à jour le capital
        self.capital += position.current_value
        
        # Mettre à jour les statistiques de pertes consécutives
        if position.unrealized_pnl > 0:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
        
        # Créer l'enregistrement du trade
        trade_result = TradeResult(
            entry_time=position.entry_time,
            exit_time=exit_time,
            entry_price=position.entry_price,
            exit_price=exit_price,
            strike=position.strike,
            premium_paid=position.premium_paid,
            exit_value=position.current_value,
            pnl=position.unrealized_pnl,
            pnl_percentage=position.pnl_percentage,
            contracts=position.contracts,
            exit_reason=action.value,
            holding_time_hours=exit_info.get('holding_time', 0),
            hedge_count=len(position.hedge_positions)
        )
        
        return trade_result
    
    def _open_new_position(
        self, 
        current_price: float, 
        current_time: datetime, 
        current_vol: float, 
        signal_info: Dict, 
        results: Dict
    ):
        """Ouvre une nouvelle position straddle"""
        strike = current_price
        time_to_expiry = DEFAULT_EXPIRY_DAYS / 365.25
        
        # Calculer le prix du straddle
        straddle_pricing = self.simulate_straddle_price(
            current_price, strike, current_vol, time_to_expiry
        )
        
        # Calculer la taille de position
        contracts = self.calculate_position_size(
            straddle_pricing['straddle_price'], signal_info['signal_quality']
        )
        
        premium_paid = straddle_pricing['straddle_price'] * contracts
        
        # Vérifier si on a assez de capital
        if premium_paid <= self.capital and premium_paid <= self.max_risk_per_trade:
            # Créer la position
            new_position = StraddlePosition(
                entry_time=current_time,
                expiry_time=current_time + timedelta(days=DEFAULT_EXPIRY_DAYS),
                entry_price=current_price,
                strike=strike,
                entry_volatility=current_vol,
                contracts=contracts,
                premium_paid=premium_paid,
                current_value=premium_paid,
                entry_confidence=signal_info['confidence']
            )
            
            # Débiter le capital
            self.capital -= premium_paid
            
            # Ajouter à la liste des positions
            self.positions.append(new_position)
            
            # Logger l'entrée
            results['positions_log'].append({
                'timestamp': current_time,
                'action': 'NEW_POSITION',
                'strike': strike,
                'premium': premium_paid,
                'contracts': contracts,
                'signal_quality': signal_info['signal_quality'],
                'confidence': signal_info['confidence']
            })
            
            self.logger.info(f"📈 Nouvelle position: Strike ${strike:,.0f}, "
                           f"Prime ${premium_paid:,.2f}, Qualité {signal_info['signal_quality']:.1%}")
    
    def _record_daily_metrics(self, current_time: datetime, results: Dict):
        """Enregistre les métriques quotidiennes"""
        total_positions_value = sum(pos.current_value for pos in self.positions)
        total_value = self.capital + total_positions_value
        daily_pnl = total_value - INITIAL_CAPITAL
        
        results['daily_pnl'].append({
            'timestamp': current_time,
            'capital': self.capital,
            'positions_value': total_positions_value,
            'total_value': total_value,
            'total_pnl': daily_pnl,
            'num_positions': len(self.positions),
            'num_hedges': len([h for h in self.hedge_positions if h.active])
        })
    
    def _close_remaining_positions(self, data: pd.DataFrame, results: Dict):
        """Clôture les positions restantes à la fin du backtest"""
        final_time = data.index[-1]
        final_price = data.iloc[-1]['close']
        
        for position in self.positions:
            trade_result = self._close_position(
                position, final_price, final_time, TradeAction.TIMEOUT, 
                {'reason': 'Fin de backtest', 'holding_time': 0}
            )
            results['trades'].append(trade_result)
    
    def _calculate_final_metrics(self, results: Dict):
        """Calcule les métriques finales de performance"""
        if not results['trades']:
            return
        
        trades = results['trades']
        
        # Métriques de base
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        
        win_rate = len(winning_trades) / total_trades * 100 if total_trades > 0 else 0
        
        # PnL statistiques
        pnl_percentages = [t.pnl_percentage for t in trades]
        avg_pnl = np.mean(pnl_percentages) if pnl_percentages else 0
        max_win = max(pnl_percentages) if pnl_percentages else 0
        max_loss = min(pnl_percentages) if pnl_percentages else 0
        
        # Profit factor
        total_wins = sum(t.pnl for t in winning_trades)
        total_losses = abs(sum(t.pnl for t in losing_trades))
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Capital final
        final_positions_value = sum(pos.current_value for pos in self.positions)
        final_capital = self.capital + final_positions_value
        total_return = ((final_capital - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
        
        # Sharpe ratio approximatif
        if len(pnl_percentages) > 1:
            sharpe_ratio = np.mean(pnl_percentages) / np.std(pnl_percentages)
        else:
            sharpe_ratio = 0
        
        # Métriques de hedging
        total_hedges = sum(len(results['hedge_opportunities']) for _ in results.get('hedge_opportunities', []))
        
        results['performance_metrics'] = {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'avg_pnl': avg_pnl,
            'max_win': max_win,
            'max_loss': max_loss,
            'profit_factor': profit_factor,
            'total_return': total_return,
            'final_capital': final_capital,
            'sharpe_ratio': sharpe_ratio,
            'total_hedges': total_hedges,
            'avg_holding_time': np.mean([t.holding_time_hours for t in trades]) if trades else 0
        }
    
    def _log_backtest_summary(self, results: Dict):
        """Affiche le résumé du backtest"""
        metrics = results['performance_metrics']
        
        self.logger.info("=" * 60)
        self.logger.info("🎯 RÉSULTATS DU BACKTEST")
        self.logger.info("=" * 60)
        self.logger.info(f"📊 Trades exécutés: {metrics['total_trades']}")
        self.logger.info(f"💰 Capital final: ${metrics['final_capital']:,.2f}")
        self.logger.info(f"📈 Rendement total: {metrics['total_return']:.2f}%")
        self.logger.info(f"🎯 Taux de réussite: {metrics['win_rate']:.1f}%")
        self.logger.info(f"📊 PnL moyen: {metrics['avg_pnl']:.2f}%")
        self.logger.info(f"🏆 Meilleur trade: {metrics['max_win']:.2f}%")
        self.logger.info(f"💔 Pire trade: {metrics['max_loss']:.2f}%")
        self.logger.info(f"⚖️ Profit Factor: {metrics['profit_factor']:.2f}")
        self.logger.info(f"📊 Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        self.logger.info(f"🛡️ Hedges utilisés: {metrics['total_hedges']}")
        self.logger.info("=" * 60)
