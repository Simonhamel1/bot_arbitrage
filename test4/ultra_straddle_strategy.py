# Stratégie Straddle Ultra-Optimisée avec Gestion Long/Short Avancée

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from config import *

class UltraStraddleStrategy:
    """
    Stratégie straddle ultra-optimisée avec :
    - Gestion avancée des positions longues/courtes
    - Risque maximum strictement limité à la prime
    - Hedging dynamique et adaptatif
    - Optimisation continue de la rentabilité
    """
    
    def __init__(self):
        self.positions = []
        self.hedge_positions = []  # Positions de hedging séparées
        self.trades_history = []
        self.capital = INITIAL_CAPITAL
        self.daily_pnl_history = []
        self.consecutive_losses = 0
        self.max_risk_per_trade = INITIAL_CAPITAL * RISK_PER_TRADE
        
        # Statistiques de performance en temps réel
        self.performance_stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0
        }
    
    def calculate_adaptive_position_size(self, straddle_price, recent_performance):
        """Calcule la taille de position adaptative basée sur la performance récente"""
        base_contracts = int(self.max_risk_per_trade / straddle_price)
        
        if ADAPTIVE_POSITION_SIZING:
            # Ajustement basé sur la performance récente
            if self.consecutive_losses >= 2:
                # Réduire la taille après pertes consécutives
                adjustment_factor = 0.5
            elif recent_performance > 0.1:  # Performance récente > 10%
                # Augmenter légèrement après succès
                adjustment_factor = 1.2
            else:
                adjustment_factor = 1.0
            
            contracts = int(base_contracts * adjustment_factor)
        else:
            contracts = base_contracts
        
        return max(1, min(contracts, 15))  # Entre 1 et 15 contrats max
    
    def calculate_volatility_score(self, data, lookback=20):
        """Calcule un score de volatilité avancé"""
        recent_vol = data['volatility'].tail(lookback)
        vol_ma = recent_vol.mean()
        vol_std = recent_vol.std()
        current_vol = data['volatility'].iloc[-1]
        
        # Score basé sur la position relative de la volatilité
        vol_percentile = (current_vol - recent_vol.min()) / (recent_vol.max() - recent_vol.min())
        vol_momentum = (current_vol - vol_ma) / vol_std if vol_std > 0 else 0
        
        # Score composite (0-100)
        score = (vol_percentile * 70) + (min(abs(vol_momentum), 2) * 15)
        return min(100, max(0, score))
    
    def advanced_entry_signal(self, current_data, lookback=10):
        """Signal d'entrée ultra-optimisé avec multiples critères"""
        if len(current_data) < 100:
            return False, {}
        
        latest = current_data.iloc[-1]
        recent_data = current_data.tail(lookback)
        
        # 1. Score de volatilité avancé
        vol_score = self.calculate_volatility_score(current_data)
        vol_condition = vol_score >= VOLATILITY_THRESHOLD
        
        # 2. Condition de consolidation plus stricte
        price_range = (recent_data['high'].max() - recent_data['low'].min()) / latest['close']
        consolidation_condition = 0.02 < price_range < 0.06  # Sweet spot
        
        # 3. RSI dans zone optimale
        rsi_condition = 35 < latest['rsi'] < 65  # Zone neutre
        
        # 4. Momentum de volatilité
        vol_ma_short = current_data['volatility'].rolling(5).mean().iloc[-1]
        vol_ma_long = current_data['volatility'].rolling(20).mean().iloc[-1]
        vol_momentum_condition = vol_ma_short > vol_ma_long * 1.1
        
        # 5. Volume exceptionnel
        volume_ma = current_data['volume'].rolling(20).mean().iloc[-1]
        volume_condition = latest['volume'] > volume_ma * 1.5
        
        # 6. Pas de tendance forte (bon pour straddle)
        price_ma_short = recent_data['close'].rolling(5).mean().iloc[-1]
        price_ma_long = recent_data['close'].rolling(10).mean().iloc[-1]
        trend_condition = abs(price_ma_short - price_ma_long) / latest['close'] < 0.02
        
        # 7. Support/Résistance proche
        support_resistance_condition = True  # Toujours vrai pour l'instant
        
        conditions = [
            vol_condition, consolidation_condition, rsi_condition, 
            vol_momentum_condition, volume_condition, trend_condition,
            support_resistance_condition
        ]
        
        # Score de qualité du signal
        signal_quality = sum(conditions) / len(conditions)
        
        # Seuil d'entrée élevé pour qualité
        should_enter = signal_quality >= 0.75
        
        if should_enter:
            entry_info = {
                'signal_quality': signal_quality,
                'vol_score': vol_score,
                'volatility': latest['volatility'],
                'price_range': price_range,
                'rsi': latest['rsi'],
                'volume_ratio': latest['volume'] / volume_ma,
                'conditions_met': sum(conditions),
                'entry_confidence': 'HIGH' if signal_quality >= 0.85 else 'MEDIUM'
            }
            return True, entry_info
        
        return False, {}
    
    def calculate_dynamic_hedge(self, position, current_price, current_vol):
        """Calcule le hedge dynamique optimal"""
        price_move = (current_price - position['entry_price']) / position['entry_price']
        vol_change = (current_vol - position['entry_vol']) / position['entry_vol']
        
        # Hedge basé sur le mouvement de prix
        if abs(price_move) > HEDGE_THRESHOLD:
            direction = 'SHORT' if price_move > 0 else 'LONG'
            
            # Taille du hedge basée sur l'intensité du mouvement
            hedge_size = min(MAX_HEDGE_RATIO, abs(price_move) * 2)
            
            # Ajustement pour volatilité
            if vol_change < -0.2:  # Volatilité chute
                hedge_size *= 1.5  # Hedge plus agressif
            
            return {
                'recommended': True,
                'direction': direction,
                'size_ratio': hedge_size,
                'entry_price': current_price,
                'reason': f'Mouvement {price_move:.1%}, Vol change {vol_change:.1%}',
                'urgency': 'HIGH' if abs(price_move) > 0.06 else 'MEDIUM',
                'expected_delta': hedge_size if direction == 'LONG' else -hedge_size
            }
        
        return {'recommended': False}
    
    def execute_hedge_position(self, hedge_info, position, current_time):
        """Exécute une position de hedge"""
        hedge_position = {
            'parent_position_id': id(position),
            'entry_time': current_time,
            'direction': hedge_info['direction'],
            'size_ratio': hedge_info['size_ratio'],
            'entry_price': hedge_info['entry_price'],
            'reason': hedge_info['reason'],
            'status': 'ACTIVE'
        }
        
        self.hedge_positions.append(hedge_position)
        
        # Log du hedge
        self.trades_history.append({
            'action': f'HEDGE_{hedge_info["direction"]}',
            'timestamp': current_time,
            'entry_price': hedge_info['entry_price'],
            'size_ratio': hedge_info['size_ratio'],
            'reason': hedge_info['reason']
        })
        
        return hedge_position
    
    def advanced_position_management(self, position, current_price, current_time, current_vol):
        """Gestion avancée des positions avec hedging dynamique"""
        time_elapsed = (current_time - position['entry_time']).total_seconds() / 3600
        time_to_expiry = max(0.001, (position['expiry_time'] - current_time).total_seconds() / (365.25 * 24 * 3600))
        
        # Simulation prix actuel
        current_straddle = self.simulate_straddle_price(
            current_price, position['strike'], current_vol, time_to_expiry
        )
        
        current_value = current_straddle['straddle_price'] * position['contracts']
        pnl = current_value - position['premium_paid']
        pnl_pct = (pnl / position['premium_paid']) * 100
        
        # Mise à jour position
        position['current_value'] = current_value
        position['unrealized_pnl'] = pnl
        position['pnl_pct'] = pnl_pct
        position['time_decay_factor'] = current_straddle['time_value'] / current_straddle['straddle_price']
        
        # Hedge dynamique
        hedge_info = self.calculate_dynamic_hedge(position, current_price, current_vol)
        if hedge_info['recommended'] and MOMENTUM_HEDGE:
            hedge_position = self.execute_hedge_position(hedge_info, position, current_time)
            position['active_hedge'] = hedge_position
        
        # Critères de sortie ultra-optimisés
        tp_threshold = (TAKE_PROFIT_MULTIPLIER * 100 - 100)
        sl_threshold = -(STOP_LOSS_MULTIPLIER * 100)
        
        # Take Profit adaptatif
        if pnl_pct >= tp_threshold:
            return 'TAKE_PROFIT', {
                'reason': f'TP atteint: {pnl_pct:.1f}%',
                'pnl_pct': pnl_pct,
                'holding_time': time_elapsed,
                'quality': 'EXCELLENT'
            }
        
        # Stop Loss dynamique
        if DYNAMIC_STOP_LOSS:
            # SL plus serré si time decay élevé
            if position['time_decay_factor'] > 0.7:
                sl_threshold *= 0.8
            
            # SL plus serré après pertes consécutives
            if self.consecutive_losses >= 2:
                sl_threshold *= 0.7
        
        if pnl_pct <= sl_threshold:
            return 'STOP_LOSS', {
                'reason': f'SL dynamique: {pnl_pct:.1f}%',
                'pnl_pct': pnl_pct,
                'holding_time': time_elapsed,
                'sl_threshold': sl_threshold
            }
        
        # Time decay critique
        if time_to_expiry < 0.08 and pnl_pct < -20:
            return 'TIME_DECAY', {
                'reason': 'Time decay critique',
                'pnl_pct': pnl_pct,
                'time_remaining': time_to_expiry
            }
        
        # Timeout adaptatif
        timeout_hours = TRADE_TIMEOUT_HOURS
        if position.get('entry_info', {}).get('entry_confidence') == 'HIGH':
            timeout_hours *= 1.5  # Plus de temps pour signaux de haute qualité
        
        if time_elapsed >= timeout_hours:
            return 'TIMEOUT', {
                'reason': f'Timeout adaptatif: {time_elapsed:.1f}h',
                'pnl_pct': pnl_pct,
                'holding_time': time_elapsed
            }
        
        # Volatilité effondrée
        vol_ratio = current_vol / position['entry_vol']
        if vol_ratio < 0.4:
            return 'VOL_COLLAPSE', {
                'reason': f'Vol effondrée: {vol_ratio:.1%}',
                'pnl_pct': pnl_pct,
                'vol_ratio': vol_ratio
            }
        
        return 'HOLD', position
    
    def simulate_straddle_price(self, spot_price, strike, volatility, time_to_expiry, interest_rate=0.02):
        """Simulation Black-Scholes optimisée"""
        if time_to_expiry <= 0:
            call_value = max(0, spot_price - strike)
            put_value = max(0, strike - spot_price)
            return {
                'call_price': call_value,
                'put_price': put_value,
                'straddle_price': call_value + put_value,
                'time_value': 0,
                'intrinsic_value': call_value + put_value
            }
        
        # Black-Scholes avec ajustements
        volatility = max(MIN_VOLATILITY, min(MAX_VOLATILITY, volatility))
        
        d1 = (np.log(spot_price / strike) + (interest_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
        d2 = d1 - volatility * np.sqrt(time_to_expiry)
        
        def norm_cdf(x):
            return 0.5 * (1 + np.sign(x) * np.sqrt(1 - np.exp(-2 * x**2 / np.pi)))
        
        call_price = spot_price * norm_cdf(d1) - strike * np.exp(-interest_rate * time_to_expiry) * norm_cdf(d2)
        put_price = call_price - spot_price + strike * np.exp(-interest_rate * time_to_expiry)
        
        call_price = max(0.01, call_price)
        put_price = max(0.01, put_price)
        straddle_price = call_price + put_price
        
        intrinsic_value = max(0, abs(spot_price - strike))
        time_value = straddle_price - intrinsic_value
        
        return {
            'call_price': call_price,
            'put_price': put_price,
            'straddle_price': straddle_price,
            'time_value': max(0, time_value),
            'intrinsic_value': intrinsic_value
        }
    
    def update_performance_stats(self, trade_result):
        """Met à jour les statistiques de performance"""
        self.performance_stats['total_trades'] += 1
        
        if trade_result['pnl'] > 0:
            self.performance_stats['winning_trades'] += 1
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
        
        self.performance_stats['total_pnl'] += trade_result['pnl']
        
        # Win rate
        self.performance_stats['win_rate'] = (
            self.performance_stats['winning_trades'] / 
            self.performance_stats['total_trades'] * 100
        )
    
    def should_stop_trading(self):
        """Détermine si on doit arrêter de trader (gestion du risque)"""
        # Arrêt après trop de pertes consécutives
        if self.consecutive_losses >= MAX_CONSECUTIVE_LOSSES:
            return True, "Trop de pertes consécutives"
        
        # Arrêt si perte quotidienne dépasse le seuil
        daily_loss = (INITIAL_CAPITAL - self.capital) / INITIAL_CAPITAL
        if daily_loss > MAX_DAILY_LOSS:
            return True, f"Perte quotidienne {daily_loss:.1%} > {MAX_DAILY_LOSS:.1%}"
        
        # Arrêt si capital insuffisant
        if self.capital < self.max_risk_per_trade * 2:
            return True, "Capital insuffisant pour continuer"
        
        return False, ""
    
    def run_ultra_backtest(self, data):
        """Lance le backtest ultra-optimisé"""
        print("🚀 Lancement backtest ULTRA-OPTIMISÉ...")
        print(f"💰 Capital initial: ${self.capital:,.2f}")
        print(f"🎯 Risque par trade: {RISK_PER_TRADE:.1%}")
        print(f"📊 Positions max: {MAX_POSITIONS}")
        print(f"🛡️ Hedging activé: {MOMENTUM_HEDGE}")
        
        results = {
            'trades': [],
            'daily_pnl': [],
            'positions_log': [],
            'hedge_opportunities': [],
            'performance_timeline': []
        }
        
        for i in range(100, len(data)):
            current_time = data.index[i]
            current_data = data.iloc[:i+1]
            current_price = data.iloc[i]['close']
            current_vol = data.iloc[i]['volatility']
            
            # Vérifier si on doit arrêter
            should_stop, stop_reason = self.should_stop_trading()
            if should_stop:
                print(f"⚠️ Arrêt du trading: {stop_reason}")
                break
            
            # Gestion positions existantes
            positions_to_close = []
            
            for j, position in enumerate(self.positions):
                action, exit_info = self.advanced_position_management(
                    position, current_price, current_time, current_vol
                )
                
                if action != 'HOLD':
                    # Mise à jour statistiques
                    trade_result = {
                        'entry_time': position['entry_time'],
                        'exit_time': current_time,
                        'entry_price': position['entry_price'],
                        'exit_price': current_price,
                        'strike': position['strike'],
                        'premium_paid': position['premium_paid'],
                        'exit_value': position['current_value'],
                        'pnl': position['unrealized_pnl'],
                        'pnl_pct': position['pnl_pct'],
                        'contracts': position['contracts'],
                        'exit_reason': exit_info.get('reason', action),
                        'holding_time': exit_info.get('holding_time', 0),
                        'entry_confidence': position.get('entry_info', {}).get('entry_confidence', 'MEDIUM')
                    }
                    
                    results['trades'].append(trade_result)
                    self.update_performance_stats(trade_result)
                    
                    # Mise à jour capital
                    self.capital += position['current_value']
                    positions_to_close.append(j)
                
                # Hedge opportunities
                if 'active_hedge' in position:
                    results['hedge_opportunities'].append({
                        'timestamp': current_time,
                        'position_strike': position['strike'],
                        'hedge_info': position['active_hedge']
                    })
            
            # Supprimer positions fermées
            for j in reversed(positions_to_close):
                del self.positions[j]
            
            # Nouvelles entrées (si conditions favorables)
            if len(self.positions) < MAX_POSITIONS:
                should_enter, entry_info = self.advanced_entry_signal(current_data)
                
                if should_enter and self.capital > self.max_risk_per_trade:
                    strike = current_price
                    time_to_expiry = DEFAULT_EXPIRY_DAYS / 365.25
                    
                    straddle_pricing = self.simulate_straddle_price(
                        current_price, strike, current_vol, time_to_expiry
                    )
                    
                    # Calcul performance récente pour taille adaptative
                    recent_trades = [t for t in results['trades'] if (current_time - t['exit_time']).days <= 30]
                    recent_performance = np.mean([t['pnl_pct'] for t in recent_trades]) / 100 if recent_trades else 0
                    
                    contracts = self.calculate_adaptive_position_size(
                        straddle_pricing['straddle_price'], recent_performance
                    )
                    premium_paid = straddle_pricing['straddle_price'] * contracts
                    
                    if premium_paid <= self.capital and premium_paid <= self.max_risk_per_trade:
                        new_position = {
                            'entry_time': current_time,
                            'expiry_time': current_time + timedelta(days=DEFAULT_EXPIRY_DAYS),
                            'entry_price': current_price,
                            'strike': strike,
                            'entry_vol': current_vol,
                            'contracts': contracts,
                            'premium_paid': premium_paid,
                            'current_value': premium_paid,
                            'unrealized_pnl': 0,
                            'pnl_pct': 0,
                            'entry_info': entry_info
                        }
                        
                        self.positions.append(new_position)
                        self.capital -= premium_paid
                        
                        results['positions_log'].append({
                            'timestamp': current_time,
                            'action': 'NEW_ULTRA_STRADDLE',
                            'strike': strike,
                            'premium': premium_paid,
                            'contracts': contracts,
                            'signal_quality': entry_info['signal_quality'],
                            'confidence': entry_info['entry_confidence']
                        })
            
            # Logging performance quotidienne
            total_positions_value = sum(pos.get('current_value', pos['premium_paid']) for pos in self.positions)
            daily_total = self.capital + total_positions_value
            daily_pnl = daily_total - INITIAL_CAPITAL
            
            results['daily_pnl'].append({
                'timestamp': current_time,
                'capital': self.capital,
                'positions_value': total_positions_value,
                'total_value': daily_total,
                'total_pnl': daily_pnl,
                'num_positions': len(self.positions),
                'win_rate': self.performance_stats.get('win_rate', 0)
            })
        
        # Fermer positions restantes
        final_time = data.index[-1]
        for position in self.positions:
            final_value = position.get('current_value', position['premium_paid'])
            final_pnl = final_value - position['premium_paid']
            
            trade_result = {
                'entry_time': position['entry_time'],
                'exit_time': final_time,
                'entry_price': position['entry_price'],
                'exit_price': data.iloc[-1]['close'],
                'strike': position['strike'],
                'premium_paid': position['premium_paid'],
                'exit_value': final_value,
                'pnl': final_pnl,
                'pnl_pct': (final_pnl / position['premium_paid']) * 100,
                'contracts': position['contracts'],
                'exit_reason': 'BACKTEST_END',
                'holding_time': (final_time - position['entry_time']).total_seconds() / 3600
            }
            
            results['trades'].append(trade_result)
            self.update_performance_stats(trade_result)
        
        # Calcul résultats finaux
        final_positions_value = sum(pos.get('current_value', pos['premium_paid']) for pos in self.positions)
        results['final_capital'] = self.capital + final_positions_value
        results['total_return'] = ((results['final_capital'] - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
        results['total_trades'] = len(results['trades'])
        
        if results['trades']:
            trade_pnl = [t['pnl_pct'] for t in results['trades']]
            winning_trades = [p for p in trade_pnl if p > 0]
            losing_trades = [p for p in trade_pnl if p <= 0]
            
            results['win_rate'] = len(winning_trades) / len(trade_pnl) * 100
            results['avg_pnl'] = np.mean(trade_pnl)
            results['avg_winner'] = np.mean(winning_trades) if winning_trades else 0
            results['avg_loser'] = np.mean(losing_trades) if losing_trades else 0
            results['max_win'] = max(trade_pnl) if trade_pnl else 0
            results['max_loss'] = min(trade_pnl) if trade_pnl else 0
            results['profit_factor'] = abs(sum(winning_trades) / sum(losing_trades)) if losing_trades else float('inf')
            
            # Sharpe ratio approximatif
            returns = [t['pnl_pct'] for t in results['trades']]
            if len(returns) > 1:
                results['sharpe_ratio'] = np.mean(returns) / np.std(returns) if np.std(returns) > 0 else 0
        
        # Affichage résultats ultra-détaillés
        print("=" * 60)
        print("🎯 RÉSULTATS ULTRA-OPTIMISÉS")
        print("=" * 60)
        print(f"📊 Trades totaux: {results['total_trades']}")
        print(f"💰 Capital final: ${results['final_capital']:,.2f}")
        print(f"📈 Rendement total: {results['total_return']:.2f}%")
        
        if results['trades']:
            print(f"🎯 Taux de réussite: {results['win_rate']:.1f}%")
            print(f"📊 PnL moyen: {results['avg_pnl']:.2f}%")
            print(f"📈 Gain moyen: {results['avg_winner']:.2f}%")
            print(f"📉 Perte moyenne: {results['avg_loser']:.2f}%")
            print(f"🏆 Meilleur trade: {results['max_win']:.2f}%")
            print(f"💔 Pire trade: {results['max_loss']:.2f}%")
            print(f"⚖️ Profit Factor: {results['profit_factor']:.2f}")
            print(f"📊 Sharpe Ratio: {results['sharpe_ratio']:.2f}")
            print(f"🛡️ Hedges exécutés: {len(results['hedge_opportunities'])}")
        
        print("=" * 60)
        
        return results
