# Stratégie Straddle Avancée avec Gestion Long/Short et Optimisation

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from config import *

class AdvancedStraddleStrategy:
    """
    Stratégie straddle avancée avec :
    - Gestion des positions longues/courtes pour limiter les pertes
    - Risque maximum = prime d'exercice 
    - Optimisation de la rentabilité
    """
    
    def __init__(self):
        self.positions = []
        self.trades_history = []
        self.capital = INITIAL_CAPITAL
        self.max_risk_per_trade = INITIAL_CAPITAL * RISK_PER_TRADE
        
    def simulate_straddle_price(self, spot_price, strike, volatility, time_to_expiry, interest_rate=0.02):
        """Simule le prix d'un straddle selon Black-Scholes simplifié"""
        if time_to_expiry <= 0:
            call_value = max(0, spot_price - strike)
            put_value = max(0, strike - spot_price)
            return {
                'call_price': call_value,
                'put_price': put_value,
                'straddle_price': call_value + put_value,
                'time_value': 0
            }
        
        # Black-Scholes simplifié
        d1 = (np.log(spot_price / strike) + (interest_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
        d2 = d1 - volatility * np.sqrt(time_to_expiry)
        
        def norm_cdf(x):
            return 0.5 * (1 + np.sign(x) * np.sqrt(1 - np.exp(-2 * x**2 / np.pi)))
        
        call_price = spot_price * norm_cdf(d1) - strike * np.exp(-interest_rate * time_to_expiry) * norm_cdf(d2)
        put_price = call_price - spot_price + strike * np.exp(-interest_rate * time_to_expiry)
        
        straddle_price = call_price + put_price
        intrinsic_value = max(0, abs(spot_price - strike))
        time_value = straddle_price - intrinsic_value
        
        return {
            'call_price': max(0.01, call_price),
            'put_price': max(0.01, put_price),
            'straddle_price': max(0.02, straddle_price),
            'time_value': max(0, time_value),
            'intrinsic_value': intrinsic_value
        }
    
    def calculate_position_size(self, straddle_price):
        """Calcule la taille de position - risque max = prime payée"""
        max_loss = straddle_price
        contracts = int(self.max_risk_per_trade / max_loss)
        contracts = max(1, min(contracts, 10))
        return contracts
    
    def should_enter_straddle(self, current_data, lookback=5):
        """Détermine si on doit entrer en position straddle"""
        if len(current_data) < 100:
            return False, {}
        
        latest = current_data.iloc[-1]
        recent_data = current_data.tail(lookback)
        
        # Critères d'entrée optimisés
        vol_condition = latest['vol_percentile'] >= VOLATILITY_THRESHOLD
        
        price_range = (recent_data['high'].max() - recent_data['low'].min()) / latest['close']
        consolidation_condition = price_range < 0.05
        
        rsi_condition = 30 < latest['rsi'] < 70
        
        vol_increasing = latest['volatility'] > current_data['volatility'].rolling(10).mean().iloc[-1]
        
        avg_volume = current_data['volume'].rolling(20).mean().iloc[-1]
        volume_condition = latest['volume'] > avg_volume * 1.2
        
        conditions = [vol_condition, consolidation_condition, rsi_condition, vol_increasing, volume_condition]
        signal_quality = sum(conditions) / len(conditions)
        
        should_enter = signal_quality >= 0.8
        
        if should_enter:
            entry_info = {
                'signal_quality': signal_quality,
                'volatility': latest['volatility'],
                'vol_percentile': latest['vol_percentile'],
                'price_range': price_range,
                'rsi': latest['rsi'],
                'conditions_met': sum(conditions)
            }
            return True, entry_info
        
        return False, {}
    
    def calculate_hedge_opportunity(self, position, current_price, price_move_pct):
        """Calcule les opportunités de hedge directionnel"""
        direction = 'UP' if price_move_pct > 0 else 'DOWN'
        move_strength = abs(price_move_pct)
        
        if move_strength > 0.05:
            hedge_size = min(0.5, move_strength)
            hedge_type = 'SHORT' if direction == 'UP' else 'LONG'
            
            return {
                'recommended': True,
                'type': hedge_type,
                'size_ratio': hedge_size,
                'reason': f'Mouvement {direction} de {move_strength:.1%}',
                'urgency': 'HIGH' if move_strength > 0.08 else 'MEDIUM'
            }
        
        return {'recommended': False}
    
    def manage_position(self, position, current_price, current_time, current_vol):
        """Gestion avancée des positions avec hedging"""
        time_elapsed = (current_time - position['entry_time']).total_seconds() / 3600
        time_to_expiry = max(0.001, (position['expiry_time'] - current_time).total_seconds() / (365.25 * 24 * 3600))
        
        # Valeur actuelle
        current_straddle = self.simulate_straddle_price(
            current_price, position['strike'], current_vol, time_to_expiry
        )
        
        current_value = current_straddle['straddle_price'] * position['contracts']
        pnl = current_value - position['premium_paid']
        pnl_pct = (pnl / position['premium_paid']) * 100
        
        position['current_value'] = current_value
        position['unrealized_pnl'] = pnl
        position['pnl_pct'] = pnl_pct
        
        # Hedge directionnel
        price_move_pct = (current_price - position['entry_price']) / position['entry_price']
        
        if abs(price_move_pct) > 0.03:
            hedge_info = self.calculate_hedge_opportunity(position, current_price, price_move_pct)
            position['hedge_opportunity'] = hedge_info
        
        # Critères de sortie
        if pnl_pct >= (TAKE_PROFIT_MULTIPLIER * 100 - 100):
            return 'TAKE_PROFIT', {
                'reason': 'Take profit atteint',
                'pnl_pct': pnl_pct,
                'holding_time': time_elapsed
            }
        
        if pnl_pct <= -80:
            return 'STOP_LOSS', {
                'reason': 'Stop loss - perte maximum',
                'pnl_pct': pnl_pct,
                'holding_time': time_elapsed
            }
        
        if time_to_expiry < 0.1 and pnl_pct < 0:
            return 'TIME_DECAY', {
                'reason': 'Time decay critique',
                'pnl_pct': pnl_pct,
                'time_remaining': time_to_expiry
            }
        
        if time_elapsed >= TRADE_TIMEOUT_HOURS:
            return 'TIMEOUT', {
                'reason': 'Timeout atteint',
                'pnl_pct': pnl_pct,
                'holding_time': time_elapsed
            }
        
        if current_vol < position['entry_vol'] * 0.5:
            return 'VOL_COLLAPSE', {
                'reason': 'Volatilité effondrée',
                'pnl_pct': pnl_pct,
                'vol_ratio': current_vol / position['entry_vol']
            }
        
        return 'HOLD', position
    
    def execute_trade(self, action, position_data, exit_data=None):
        """Exécute un trade et met à jour le capital"""
        if action == 'ENTER':
            self.capital -= position_data['premium_paid']
            
            trade_record = {
                'action': 'ENTER_STRADDLE',
                'timestamp': position_data['entry_time'],
                'strike': position_data['strike'],
                'premium_paid': position_data['premium_paid'],
                'contracts': position_data['contracts'],
                'volatility': position_data['entry_vol'],
                'capital_remaining': self.capital
            }
            
        else:
            exit_value = position_data['current_value']
            realized_pnl = position_data['unrealized_pnl']
            self.capital += exit_value
            
            trade_record = {
                'action': f'EXIT_{action}',
                'timestamp': datetime.now(),
                'exit_value': exit_value,
                'realized_pnl': realized_pnl,
                'pnl_pct': position_data['pnl_pct'],
                'holding_time': exit_data.get('holding_time', 0),
                'exit_reason': exit_data.get('reason', action),
                'capital_after': self.capital
            }
        
        self.trades_history.append(trade_record)
        return trade_record
    
    def run_backtest(self, data):
        """Lance le backtest avec stratégie avancée"""
        print("🚀 Lancement backtest straddle avancé...")
        print(f"💰 Capital initial: ${self.capital:,.2f}")
        print(f"🎯 Risque par trade: ${self.max_risk_per_trade:,.2f}")
        
        results = {
            'trades': [],
            'daily_pnl': [],
            'positions_log': [],
            'hedge_opportunities': []
        }
        
        for i in range(100, len(data)):
            current_time = data.index[i]
            current_data = data.iloc[:i+1]
            current_price = data.iloc[i]['close']
            current_vol = data.iloc[i]['volatility']
            
            # Gestion positions existantes
            positions_to_close = []
            
            for j, position in enumerate(self.positions):
                action, exit_info = self.manage_position(
                    position, current_price, current_time, current_vol
                )
                
                if action != 'HOLD':
                    trade_record = self.execute_trade(action, position, exit_info)
                    results['trades'].append({
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
                        'holding_time': exit_info.get('holding_time', 0)
                    })
                    
                    positions_to_close.append(j)
                
                # Opportunities de hedge
                if 'hedge_opportunity' in position and position['hedge_opportunity'].get('recommended'):
                    results['hedge_opportunities'].append({
                        'timestamp': current_time,
                        'position_strike': position['strike'],
                        'hedge_info': position['hedge_opportunity']
                    })
            
            # Supprimer positions fermées
            for j in reversed(positions_to_close):
                del self.positions[j]
            
            # Nouvelles entrées
            if len(self.positions) < MAX_POSITIONS:
                should_enter, entry_info = self.should_enter_straddle(current_data)
                
                if should_enter and self.capital > self.max_risk_per_trade:
                    strike = current_price
                    time_to_expiry = 30 / 365.25
                    
                    straddle_pricing = self.simulate_straddle_price(
                        current_price, strike, current_vol, time_to_expiry
                    )
                    
                    contracts = self.calculate_position_size(straddle_pricing['straddle_price'])
                    premium_paid = straddle_pricing['straddle_price'] * contracts
                    
                    if premium_paid <= self.capital:
                        new_position = {
                            'entry_time': current_time,
                            'expiry_time': current_time + timedelta(days=30),
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
                        self.execute_trade('ENTER', new_position)
                        
                        results['positions_log'].append({
                            'timestamp': current_time,
                            'action': 'NEW_STRADDLE',
                            'strike': strike,
                            'premium': premium_paid,
                            'contracts': contracts,
                            'signal_quality': entry_info['signal_quality']
                        })
            
            # PnL quotidienne
            total_positions_value = sum(pos.get('current_value', pos['premium_paid']) for pos in self.positions)
            daily_pnl = self.capital + total_positions_value - INITIAL_CAPITAL
            
            results['daily_pnl'].append({
                'timestamp': current_time,
                'capital': self.capital,
                'positions_value': total_positions_value,
                'total_pnl': daily_pnl,
                'num_positions': len(self.positions)
            })
        
        # Fermer positions restantes
        final_time = data.index[-1]
        for position in self.positions:
            final_value = position.get('current_value', position['premium_paid'])
            final_pnl = final_value - position['premium_paid']
            
            results['trades'].append({
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
            })
        
        # Statistiques finales
        results['final_capital'] = self.capital + sum(pos.get('current_value', pos['premium_paid']) for pos in self.positions)
        results['total_return'] = ((results['final_capital'] - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
        results['total_trades'] = len(results['trades'])
        
        if results['trades']:
            trade_pnl = [t['pnl_pct'] for t in results['trades']]
            results['win_rate'] = len([p for p in trade_pnl if p > 0]) / len(trade_pnl) * 100
            results['avg_pnl'] = np.mean(trade_pnl)
            results['max_win'] = max(trade_pnl) if trade_pnl else 0
            results['max_loss'] = min(trade_pnl) if trade_pnl else 0
        
        print(f"✅ Backtest terminé:")
        print(f"   📊 {results['total_trades']} trades exécutés")
        print(f"   💰 Capital final: ${results['final_capital']:,.2f}")
        print(f"   📈 Rendement total: {results['total_return']:.2f}%")
        if results['trades']:
            print(f"   🎯 Taux de réussite: {results['win_rate']:.1f}%")
            print(f"   📊 PnL moyen: {results['avg_pnl']:.2f}%")
            print(f"   📈 Meilleur trade: {results['max_win']:.2f}%")
            print(f"   📉 Pire trade: {results['max_loss']:.2f}%")
        
        return results
