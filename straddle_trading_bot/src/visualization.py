# Module de Visualisation pour le Bot Straddle
# Graphiques et analyses visuelles optimisés

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuration style
plt.style.use('dark_background')
sns.set_palette("Set2")

class TradingVisualization:
    """
    Générateur de visualisations pour l'analyse de trading
    
    Fonctionnalités:
    - Dashboard complet de performance
    - Graphiques d'analyse des trades
    - Métriques de risque
    - Visualisation du hedging
    """
    
    def __init__(self):
        self.fig_size = (16, 10)
        self.colors = {
            'profit': '#00ff88',
            'loss': '#ff4444', 
            'neutral': '#888888',
            'hedge': '#ffaa00',
            'background': '#1a1a1a',
            'grid': '#333333',
            'text': '#ffffff'
        }
    
    def create_complete_dashboard(self, data, results, output_dir='output'):
        """
        Crée le dashboard complet de performance
        
        Args:
            data: Données de marché
            results: Résultats du backtest
            output_dir: Dossier de sortie
        """
        print("📊 Génération du dashboard complet...")
        
        # Dashboard principal
        self._create_main_dashboard(data, results, output_dir)
        
        # Analyses détaillées si trades disponibles
        if results['performance_metrics']['total_trades'] > 0:
            self._create_trade_analysis(results, output_dir)
            self._create_risk_analysis(results, output_dir)
        
        print("✅ Visualisations générées avec succès")
    
    def _create_main_dashboard(self, data, results, output_dir):
        """Crée le dashboard principal"""
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.patch.set_facecolor(self.colors['background'])
        fig.suptitle('🚀 DASHBOARD STRADDLE BOT', fontsize=20, fontweight='bold', color=self.colors['text'])
        
        # 1. Évolution du capital
        self._plot_capital_evolution(axes[0, 0], results)
        
        # 2. Distribution des PnL
        self._plot_pnl_distribution(axes[0, 1], results)
        
        # 3. Métriques de performance
        self._plot_performance_metrics(axes[0, 2], results)
        
        # 4. Prix et volatilité
        self._plot_price_volatility(axes[1, 0], data)
        
        # 5. Analyse des trades
        self._plot_trades_timeline(axes[1, 1], results)
        
        # 6. Drawdown
        self._plot_drawdown(axes[1, 2], results)
        
        plt.tight_layout()
        
        # Sauvegarde
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(output_dir) / f"straddle_dashboard_{timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight', 
                   facecolor=self.colors['background'])
        print(f"✅ Dashboard sauvegardé: {filename}")
        
        plt.show()
    
    def _plot_capital_evolution(self, ax, results):
        """Graphique d'évolution du capital"""
        if not results['daily_pnl']:
            ax.text(0.5, 0.5, 'Aucune donnée\ndisponible', ha='center', va='center',
                   transform=ax.transAxes, fontsize=12, color=self.colors['text'])
            ax.set_title('💰 Évolution du Capital', color=self.colors['text'])
            return
        
        df = pd.DataFrame(results['daily_pnl'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Ligne principale
        ax.plot(df['timestamp'], df['total_value'], 
               color=self.colors['profit'], linewidth=3, label='Capital Total')
        
        # Zone profit/perte
        initial_capital = df['total_value'].iloc[0] if len(df) > 0 else 10000
        ax.fill_between(df['timestamp'], df['total_value'], initial_capital,
                       where=(df['total_value'] >= initial_capital),
                       color=self.colors['profit'], alpha=0.3, label='Profit')
        ax.fill_between(df['timestamp'], df['total_value'], initial_capital,
                       where=(df['total_value'] < initial_capital),
                       color=self.colors['loss'], alpha=0.3, label='Perte')
        
        # Ligne de référence
        ax.axhline(y=initial_capital, color=self.colors['neutral'], 
                  linestyle='--', alpha=0.7, label='Capital Initial')
        
        ax.set_title('💰 Évolution du Capital', color=self.colors['text'])
        ax.set_xlabel('Date', color=self.colors['text'])
        ax.set_ylabel('Capital ($)', color=self.colors['text'])
        ax.legend()
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        ax.tick_params(colors=self.colors['text'])
        
        # Format des dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    
    def _plot_pnl_distribution(self, ax, results):
        """Distribution des PnL"""
        if not results.get('trades'):
            ax.text(0.5, 0.5, 'Aucun trade\nexécuté', ha='center', va='center',
                   transform=ax.transAxes, fontsize=12, color=self.colors['text'])
            ax.set_title('📊 Distribution PnL', color=self.colors['text'])
            return
        
        pnl_data = [t.pnl_percentage for t in results['trades']]
        
        # Histogramme
        ax.hist(pnl_data, bins=15, alpha=0.7, color=self.colors['neutral'], 
               edgecolor=self.colors['text'], linewidth=1)
        
        # Statistiques
        mean_pnl = np.mean(pnl_data)
        ax.axvline(mean_pnl, color=self.colors['profit'], linestyle='-', 
                  linewidth=2, label=f'Moyenne: {mean_pnl:.1f}%')
        ax.axvline(0, color=self.colors['loss'], linestyle=':', 
                  linewidth=2, alpha=0.7, label='Break-even')
        
        ax.set_title('📊 Distribution PnL', color=self.colors['text'])
        ax.set_xlabel('PnL (%)', color=self.colors['text'])
        ax.set_ylabel('Fréquence', color=self.colors['text'])
        ax.legend()
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        ax.tick_params(colors=self.colors['text'])
    
    def _plot_performance_metrics(self, ax, results):
        """Tableau des métriques de performance"""
        ax.axis('off')
        
        metrics = results['performance_metrics']
        
        # Données du tableau
        table_data = [
            ['Total Trades', f"{metrics.get('total_trades', 0)}"],
            ['Win Rate', f"{metrics.get('win_rate', 0):.1f}%"],
            ['Rendement', f"{metrics.get('total_return', 0):.2f}%"],
            ['PnL Moyen', f"{metrics.get('avg_pnl', 0):.2f}%"],
            ['Meilleur Trade', f"{metrics.get('max_win', 0):.2f}%"],
            ['Pire Trade', f"{metrics.get('max_loss', 0):.2f}%"],
            ['Profit Factor', f"{metrics.get('profit_factor', 0):.2f}"],
            ['Sharpe Ratio', f"{metrics.get('sharpe_ratio', 0):.2f}"]
        ]
        
        # Création du tableau
        table = ax.table(cellText=table_data,
                        colLabels=['Métrique', 'Valeur'],
                        cellLoc='center',
                        loc='center',
                        colWidths=[0.6, 0.4])
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Style
        for i in range(len(table_data) + 1):
            for j in range(2):
                cell = table[(i, j)]
                if i == 0:  # Header
                    cell.set_facecolor('#333333')
                    cell.set_text_props(weight='bold', color=self.colors['text'])
                else:
                    cell.set_facecolor(self.colors['background'])
                    cell.set_text_props(color=self.colors['text'])
                cell.set_edgecolor(self.colors['text'])
        
        ax.set_title('📊 Métriques Performance', color=self.colors['text'])
    
    def _plot_price_volatility(self, ax, data):
        """Graphique prix et volatilité"""
        if data.empty:
            return
        
        # Prix (axe principal)
        ax.plot(data.index, data['close'], color=self.colors['profit'], 
               linewidth=1, label='Prix BTC')
        
        # Volatilité (axe secondaire)
        ax2 = ax.twinx()
        ax2.plot(data.index, data['volatility'] * 100, color=self.colors['hedge'], 
                linewidth=1, alpha=0.7, label='Volatilité (%)')
        
        ax.set_title('💹 Prix et Volatilité', color=self.colors['text'])
        ax.set_xlabel('Date', color=self.colors['text'])
        ax.set_ylabel('Prix ($)', color=self.colors['text'])
        ax2.set_ylabel('Volatilité (%)', color=self.colors['text'])
        
        # Légendes
        lines1, labels1 = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        ax.tick_params(colors=self.colors['text'])
        ax2.tick_params(colors=self.colors['text'])
    
    def _plot_trades_timeline(self, ax, results):
        """Timeline des trades"""
        if not results.get('trades'):
            ax.text(0.5, 0.5, 'Aucun trade\nexécuté', ha='center', va='center',
                   transform=ax.transAxes, fontsize=12, color=self.colors['text'])
            ax.set_title('📈 Timeline Trades', color=self.colors['text'])
            return
        
        trades = results['trades']
        
        # Séparer gains et pertes
        winning_trades = [t for t in trades if t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl <= 0]
        
        # Plot des trades gagnants
        if winning_trades:
            win_times = [t.exit_time for t in winning_trades]
            win_pnl = [t.pnl_percentage for t in winning_trades]
            ax.scatter(win_times, win_pnl, color=self.colors['profit'], 
                      s=60, alpha=0.8, marker='^', label=f'Gains ({len(winning_trades)})')
        
        # Plot des trades perdants
        if losing_trades:
            loss_times = [t.exit_time for t in losing_trades]
            loss_pnl = [t.pnl_percentage for t in losing_trades]
            ax.scatter(loss_times, loss_pnl, color=self.colors['loss'], 
                      s=60, alpha=0.8, marker='v', label=f'Pertes ({len(losing_trades)})')
        
        ax.axhline(y=0, color=self.colors['neutral'], linestyle='-', alpha=0.7)
        ax.set_title('📈 Timeline des Trades', color=self.colors['text'])
        ax.set_xlabel('Date', color=self.colors['text'])
        ax.set_ylabel('PnL (%)', color=self.colors['text'])
        ax.legend()
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        ax.tick_params(colors=self.colors['text'])
    
    def _plot_drawdown(self, ax, results):
        """Graphique de drawdown"""
        if not results['daily_pnl']:
            ax.text(0.5, 0.5, 'Aucune donnée\ndisponible', ha='center', va='center',
                   transform=ax.transAxes, fontsize=12, color=self.colors['text'])
            ax.set_title('📉 Drawdown', color=self.colors['text'])
            return
        
        df = pd.DataFrame(results['daily_pnl'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Calcul du drawdown
        df['running_max'] = df['total_value'].cummax()
        df['drawdown'] = ((df['total_value'] - df['running_max']) / df['running_max']) * 100
        
        # Plot
        ax.fill_between(df['timestamp'], df['drawdown'], 0, 
                       color=self.colors['loss'], alpha=0.6)
        ax.plot(df['timestamp'], df['drawdown'], 
               color=self.colors['loss'], linewidth=2)
        
        # Max drawdown
        max_dd = df['drawdown'].min()
        ax.set_title(f'📉 Drawdown (Max: {max_dd:.1f}%)', color=self.colors['text'])
        ax.set_xlabel('Date', color=self.colors['text'])
        ax.set_ylabel('Drawdown (%)', color=self.colors['text'])
        ax.grid(True, alpha=0.3, color=self.colors['grid'])
        ax.tick_params(colors=self.colors['text'])
    
    def _create_trade_analysis(self, results, output_dir):
        """Analyse détaillée des trades"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
        fig.patch.set_facecolor(self.colors['background'])
        fig.suptitle('📊 ANALYSE DÉTAILLÉE DES TRADES', fontsize=16, fontweight='bold', color=self.colors['text'])
        
        trades = results['trades']
        
        # 1. PnL par trade
        pnl_values = [t.pnl_percentage for t in trades]
        colors = [self.colors['profit'] if p > 0 else self.colors['loss'] for p in pnl_values]
        
        ax1.bar(range(len(trades)), pnl_values, color=colors, alpha=0.7)
        ax1.axhline(y=0, color=self.colors['neutral'], linestyle='-', alpha=0.7)
        ax1.set_title('📊 PnL par Trade', color=self.colors['text'])
        ax1.set_xlabel('Numéro Trade', color=self.colors['text'])
        ax1.set_ylabel('PnL (%)', color=self.colors['text'])
        ax1.grid(True, alpha=0.3, color=self.colors['grid'])
        ax1.tick_params(colors=self.colors['text'])
        
        # 2. Durée vs PnL
        durations = [t.holding_time_hours for t in trades]
        ax2.scatter(durations, pnl_values, c=colors, alpha=0.7, s=60)
        ax2.axhline(y=0, color=self.colors['neutral'], linestyle='-', alpha=0.7)
        ax2.set_title('⏱️ Durée vs PnL', color=self.colors['text'])
        ax2.set_xlabel('Durée (heures)', color=self.colors['text'])
        ax2.set_ylabel('PnL (%)', color=self.colors['text'])
        ax2.grid(True, alpha=0.3, color=self.colors['grid'])
        ax2.tick_params(colors=self.colors['text'])
        
        # 3. Raisons de sortie
        exit_reasons = {}
        for trade in trades:
            reason = trade.exit_reason
            exit_reasons[reason] = exit_reasons.get(reason, 0) + 1
        
        if exit_reasons:
            ax3.pie(exit_reasons.values(), labels=exit_reasons.keys(), autopct='%1.1f%%',
                   startangle=90, colors=[self.colors['profit'], self.colors['loss'], 
                                        self.colors['hedge'], self.colors['neutral']][:len(exit_reasons)])
            ax3.set_title('🚪 Raisons de Sortie', color=self.colors['text'])
        
        # 4. Évolution du win rate
        cumulative_wins = 0
        win_rates = []
        for i, trade in enumerate(trades):
            if trade.pnl > 0:
                cumulative_wins += 1
            win_rates.append((cumulative_wins / (i + 1)) * 100)
        
        ax4.plot(range(1, len(trades) + 1), win_rates, color=self.colors['profit'], linewidth=2)
        ax4.axhline(y=50, color=self.colors['neutral'], linestyle='--', alpha=0.7, label='50%')
        ax4.set_title('🎯 Évolution Win Rate', color=self.colors['text'])
        ax4.set_xlabel('Nombre de Trades', color=self.colors['text'])
        ax4.set_ylabel('Win Rate (%)', color=self.colors['text'])
        ax4.legend()
        ax4.grid(True, alpha=0.3, color=self.colors['grid'])
        ax4.tick_params(colors=self.colors['text'])
        
        plt.tight_layout()
        
        # Sauvegarde
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(output_dir) / f"trades_analysis_{timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight', 
                   facecolor=self.colors['background'])
        print(f"✅ Analyse trades sauvegardée: {filename}")
        
        plt.show()
    
    def _create_risk_analysis(self, results, output_dir):
        """Analyse des risques"""
        if not results['daily_pnl']:
            return
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
        fig.patch.set_facecolor(self.colors['background'])
        fig.suptitle('🛡️ ANALYSE DES RISQUES', fontsize=16, fontweight='bold', color=self.colors['text'])
        
        df = pd.DataFrame(results['daily_pnl'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['returns'] = df['total_value'].pct_change() * 100
        
        # 1. Volatilité du portefeuille
        df['vol_rolling'] = df['returns'].rolling(20).std()
        ax1.plot(df['timestamp'], df['vol_rolling'], color=self.colors['hedge'], linewidth=2)
        ax1.fill_between(df['timestamp'], df['vol_rolling'], alpha=0.3, color=self.colors['hedge'])
        ax1.set_title('📊 Volatilité du Portefeuille', color=self.colors['text'])
        ax1.set_xlabel('Date', color=self.colors['text'])
        ax1.set_ylabel('Volatilité (%)', color=self.colors['text'])
        ax1.grid(True, alpha=0.3, color=self.colors['grid'])
        ax1.tick_params(colors=self.colors['text'])
        
        # 2. Distribution des retours
        returns_clean = df['returns'].dropna()
        if len(returns_clean) > 0:
            ax2.hist(returns_clean, bins=20, alpha=0.7, color=self.colors['neutral'])
            ax2.axvline(returns_clean.mean(), color=self.colors['profit'], 
                       linestyle='-', linewidth=2, label=f'Moyenne: {returns_clean.mean():.2f}%')
            ax2.axvline(0, color=self.colors['loss'], linestyle=':', linewidth=2, alpha=0.7)
            ax2.set_title('📈 Distribution Retours', color=self.colors['text'])
            ax2.set_xlabel('Retour (%)', color=self.colors['text'])
            ax2.set_ylabel('Fréquence', color=self.colors['text'])
            ax2.legend()
            ax2.grid(True, alpha=0.3, color=self.colors['grid'])
            ax2.tick_params(colors=self.colors['text'])
        
        # 3. Nombre de positions actives
        ax3.plot(df['timestamp'], df['num_positions'], color=self.colors['profit'], 
                linewidth=2, marker='o', markersize=4)
        ax3.set_title('📊 Positions Actives', color=self.colors['text'])
        ax3.set_xlabel('Date', color=self.colors['text'])
        ax3.set_ylabel('Nombre de Positions', color=self.colors['text'])
        ax3.grid(True, alpha=0.3, color=self.colors['grid'])
        ax3.tick_params(colors=self.colors['text'])
        
        # 4. Value at Risk (VaR) approximatif
        if len(returns_clean) > 10:
            var_95 = np.percentile(returns_clean, 5)
            var_99 = np.percentile(returns_clean, 1)
            
            ax4.text(0.1, 0.8, f'VaR 95%: {var_95:.2f}%', transform=ax4.transAxes, 
                    fontsize=12, color=self.colors['text'])
            ax4.text(0.1, 0.6, f'VaR 99%: {var_99:.2f}%', transform=ax4.transAxes, 
                    fontsize=12, color=self.colors['text'])
            ax4.text(0.1, 0.4, f'Max Loss: {returns_clean.min():.2f}%', transform=ax4.transAxes, 
                    fontsize=12, color=self.colors['loss'])
            ax4.text(0.1, 0.2, f'Max Gain: {returns_clean.max():.2f}%', transform=ax4.transAxes, 
                    fontsize=12, color=self.colors['profit'])
            
            ax4.set_title('💰 Value at Risk', color=self.colors['text'])
            ax4.axis('off')
        
        plt.tight_layout()
        
        # Sauvegarde
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = Path(output_dir) / f"risk_analysis_{timestamp}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight', 
                   facecolor=self.colors['background'])
        print(f"✅ Analyse risque sauvegardée: {filename}")
        
        plt.show()
