# Module de trading pour la stratégie de straddle
import pandas as pd
import numpy as np
import time
from datetime import datetime
import logging

from config import (SYMBOL, TRANSACTION_FEE, POSITION_SIZE_PCT, 
                   MAX_POSITION_DURATION, TAKE_PROFIT_PCT, STOP_LOSS_PCT)

class StraddleTrader:
    """
    Classe pour exécuter la stratégie de straddle
    """
    def __init__(self, exchange, symbol=SYMBOL, dry_run=True):
        """
        Initialise le trader
        
        Args:
            exchange: Instance de l'échange
            symbol (str): Symbole à trader
            dry_run (bool): Si True, n'exécute pas réellement les ordres
        """
        self.exchange = exchange
        self.symbol = symbol
        self.dry_run = dry_run
        
        # État interne
        self.long_position = None
        self.short_position = None
        self.trades_history = []
        
        # Configuration du logger
        self.setup_logger()
    
    def setup_logger(self):
        """Configure le logger pour le trader"""
        self.logger = logging.getLogger('straddle_trader')
        self.logger.setLevel(logging.INFO)
        
        # Créer un gestionnaire de fichier pour enregistrer les logs
        fh = logging.FileHandler('straddle_trades.log')
        fh.setLevel(logging.INFO)
        
        # Créer un format de log
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        
        # Ajouter le gestionnaire au logger
        self.logger.addHandler(fh)
    
    def calculate_position_size(self, capital, risk_pct, entry_price, stop_loss_price):
        """
        Calcule la taille de position en fonction du risque
        
        Args:
            capital (float): Capital disponible
            risk_pct (float): Pourcentage du capital à risquer
            entry_price (float): Prix d'entrée
            stop_loss_price (float): Prix du stop-loss
        
        Returns:
            float: Taille de la position
        """
        risk_amount = capital * risk_pct
        risk_per_unit = abs(entry_price - stop_loss_price)
        
        if risk_per_unit < 0.0000001:
            risk_per_unit = entry_price * 0.01  # Éviter division par zéro
        
        return risk_amount / risk_per_unit
    
    def open_long_position(self, price, take_profit_level, stop_loss_level):
        """
        Ouvre une position longue
        
        Args:
            price (float): Prix d'entrée
            take_profit_level (float): Niveau de prise de profit
            stop_loss_level (float): Niveau de stop-loss
        
        Returns:
            bool: True si la position est ouverte, False sinon
        """
        if self.long_position is not None:
            self.logger.info("Position longue déjà ouverte. Ignoré.")
            return False
        
        try:
            # Récupérer le solde
            balance = self.exchange.fetch_balance()
            quote_currency = self.symbol.split('/')[1]
            available_balance = balance[quote_currency]['free']
            
            # Calculer la taille de la position
            position_size = self.calculate_position_size(
                available_balance * POSITION_SIZE_PCT / 2,  # Diviser par 2 pour le straddle
                1.0,  # Utiliser tout le montant alloué
                price,
                stop_loss_level
            )
            
            # Exécuter l'ordre
            if not self.dry_run:
                order = self.exchange.create_market_buy_order(
                    self.symbol,
                    position_size
                )
                self.logger.info(f"Ordre d'achat exécuté: {order}")
            else:
                self.logger.info(f"[DRY RUN] Achat de {position_size} {self.symbol} à {price}")
            
            # Enregistrer la position
            self.long_position = {
                'entry_time': datetime.now(),
                'entry_price': price,
                'size': position_size,
                'take_profit': take_profit_level,
                'stop_loss': stop_loss_level
            }
            
            return True
        
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ouverture de la position longue: {e}")
            return False
    
    def open_short_position(self, price, take_profit_level, stop_loss_level):
        """
        Ouvre une position courte
        
        Args:
            price (float): Prix d'entrée
            take_profit_level (float): Niveau de prise de profit
            stop_loss_level (float): Niveau de stop-loss
        
        Returns:
            bool: True si la position est ouverte, False sinon
        """
        if self.short_position is not None:
            self.logger.info("Position courte déjà ouverte. Ignoré.")
            return False
        
        try:
            # Récupérer le solde
            balance = self.exchange.fetch_balance()
            quote_currency = self.symbol.split('/')[1]
            available_balance = balance[quote_currency]['free']
            
            # Calculer la taille de la position
            position_size = self.calculate_position_size(
                available_balance * POSITION_SIZE_PCT / 2,  # Diviser par 2 pour le straddle
                1.0,  # Utiliser tout le montant alloué
                price,
                stop_loss_level
            )
            
            # Exécuter l'ordre
            if not self.dry_run:
                order = self.exchange.create_market_sell_order(
                    self.symbol,
                    position_size
                )
                self.logger.info(f"Ordre de vente exécuté: {order}")
            else:
                self.logger.info(f"[DRY RUN] Vente de {position_size} {self.symbol} à {price}")
            
            # Enregistrer la position
            self.short_position = {
                'entry_time': datetime.now(),
                'entry_price': price,
                'size': position_size,
                'take_profit': take_profit_level,
                'stop_loss': stop_loss_level
            }
            
            return True
        
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ouverture de la position courte: {e}")
            return False
    
    def close_long_position(self, price, reason):
        """
        Ferme une position longue
        
        Args:
            price (float): Prix de sortie
            reason (str): Raison de la fermeture
        
        Returns:
            bool: True si la position est fermée, False sinon
        """
        if self.long_position is None:
            return False
        
        try:
            position_size = self.long_position['size']
            entry_price = self.long_position['entry_price']
            
            # Exécuter l'ordre
            if not self.dry_run:
                order = self.exchange.create_market_sell_order(
                    self.symbol,
                    position_size
                )
                self.logger.info(f"Ordre de clôture de position longue exécuté: {order}")
            else:
                self.logger.info(f"[DRY RUN] Vente de {position_size} {self.symbol} à {price}")
            
            # Calculer le P&L
            pnl_pct = ((price * (1 - TRANSACTION_FEE)) / (entry_price * (1 + TRANSACTION_FEE)) - 1) * 100
            
            # Enregistrer le trade
            trade = {
                'type': 'LONG',
                'entry_time': self.long_position['entry_time'],
                'exit_time': datetime.now(),
                'entry_price': entry_price,
                'exit_price': price,
                'size': position_size,
                'pnl_pct': pnl_pct,
                'reason': reason
            }
            
            self.trades_history.append(trade)
            self.logger.info(f"Trade longue terminé: {trade}")
            
            # Réinitialiser la position
            self.long_position = None
            
            return True
        
        except Exception as e:
            self.logger.error(f"Erreur lors de la fermeture de la position longue: {e}")
            return False
    
    def close_short_position(self, price, reason):
        """
        Ferme une position courte
        
        Args:
            price (float): Prix de sortie
            reason (str): Raison de la fermeture
        
        Returns:
            bool: True si la position est fermée, False sinon
        """
        if self.short_position is None:
            return False
        
        try:
            position_size = self.short_position['size']
            entry_price = self.short_position['entry_price']
            
            # Exécuter l'ordre
            if not self.dry_run:
                order = self.exchange.create_market_buy_order(
                    self.symbol,
                    position_size
                )
                self.logger.info(f"Ordre de clôture de position courte exécuté: {order}")
            else:
                self.logger.info(f"[DRY RUN] Achat de {position_size} {self.symbol} à {price}")
            
            # Calculer le P&L
            pnl_pct = (1 - (price * (1 + TRANSACTION_FEE)) / (entry_price * (1 - TRANSACTION_FEE))) * 100
            
            # Enregistrer le trade
            trade = {
                'type': 'SHORT',
                'entry_time': self.short_position['entry_time'],
                'exit_time': datetime.now(),
                'entry_price': entry_price,
                'exit_price': price,
                'size': position_size,
                'pnl_pct': pnl_pct,
                'reason': reason
            }
            
            self.trades_history.append(trade)
            self.logger.info(f"Trade courte terminé: {trade}")
            
            # Réinitialiser la position
            self.short_position = None
            
            return True
        
        except Exception as e:
            self.logger.error(f"Erreur lors de la fermeture de la position courte: {e}")
            return False
    
    def open_straddle(self, price, volatility):
        """
        Ouvre une position straddle (long et short simultanément)
        
        Args:
            price (float): Prix actuel
            volatility (float): Volatilité actuelle
        
        Returns:
            tuple: (long_success, short_success)
        """
        # Calculer les niveaux de TP/SL
        long_tp = price * (1 + TAKE_PROFIT_PCT)
        long_sl = price * (1 - STOP_LOSS_PCT)
        
        short_tp = price * (1 - TAKE_PROFIT_PCT)
        short_sl = price * (1 + STOP_LOSS_PCT)
        
        # Ouvrir les positions
        long_success = self.open_long_position(price, long_tp, long_sl)
        short_success = self.open_short_position(price, short_tp, short_sl)
        
        if long_success and short_success:
            self.logger.info(f"Position straddle ouverte à {price} avec volatilité {volatility}")
        
        return long_success, short_success
    
    def check_positions(self, current_price, current_time):
        """
        Vérifie l'état des positions ouvertes et les ferme si nécessaire
        
        Args:
            current_price (float): Prix actuel
            current_time (datetime): Heure actuelle
        """
        # Vérifier la position longue
        if self.long_position is not None:
            # Vérifier le take profit
            if current_price >= self.long_position['take_profit']:
                self.close_long_position(current_price, 'TAKE_PROFIT')
            
            # Vérifier le stop loss
            elif current_price <= self.long_position['stop_loss']:
                self.close_long_position(current_price, 'STOP_LOSS')
            
            # Vérifier le timeout
            elif (current_time - self.long_position['entry_time']).total_seconds() / 60 >= MAX_POSITION_DURATION:
                self.close_long_position(current_price, 'TIMEOUT')
        
        # Vérifier la position courte
        if self.short_position is not None:
            # Vérifier le take profit
            if current_price <= self.short_position['take_profit']:
                self.close_short_position(current_price, 'TAKE_PROFIT')
            
            # Vérifier le stop loss
            elif current_price >= self.short_position['stop_loss']:
                self.close_short_position(current_price, 'STOP_LOSS')
            
            # Vérifier le timeout
            elif (current_time - self.short_position['entry_time']).total_seconds() / 60 >= MAX_POSITION_DURATION:
                self.close_short_position(current_price, 'TIMEOUT')
    
    def get_performance_summary(self):
        """
        Calcule et renvoie un résumé des performances
        
        Returns:
            dict: Résumé des performances
        """
        if not self.trades_history:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'total_pnl_pct': 0
            }
        
        total_trades = len(self.trades_history)
        profitable_trades = [t for t in self.trades_history if t['pnl_pct'] > 0]
        win_rate = len(profitable_trades) / total_trades if total_trades > 0 else 0
        
        profits = [t['pnl_pct'] for t in self.trades_history if t['pnl_pct'] > 0]
        losses = [t['pnl_pct'] for t in self.trades_history if t['pnl_pct'] <= 0]
        
        avg_profit = np.mean(profits) if profits else 0
        avg_loss = np.mean(losses) if losses else 0
        
        total_profit = sum(profits)
        total_loss = abs(sum(losses))
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        total_pnl_pct = sum(t['pnl_pct'] for t in self.trades_history)
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'avg_profit': avg_profit,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_pnl_pct': total_pnl_pct
        }
    
    def save_trades_to_csv(self, filename='straddle_trades.csv'):
        """
        Sauvegarde l'historique des trades dans un fichier CSV
        
        Args:
            filename (str): Nom du fichier CSV
        """
        if not self.trades_history:
            self.logger.info("Pas de trades à sauvegarder")
            return
        
        df = pd.DataFrame(self.trades_history)
        df.to_csv(filename, index=False)
        self.logger.info(f"Historique des trades sauvegardé dans {filename}")
