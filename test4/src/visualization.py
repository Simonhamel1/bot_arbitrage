# Visualisation avancée pour la stratégie straddle avec analyse PnL approfondie

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def create_advanced_pnl_analysis(df, results):
    """
    Crée une analyse PnL complète avec 8 graphiques détaillés
    
    Args:
        df: DataFrame avec les données et signaux
        results: Résultats du backtest
    """
    # Configuration pour les graphiques
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # Créer une figure avec 8 sous-graphiques
    fig = plt.figure(figsize=(20, 16))
    
    # Vérifier la présence de données
    if 'equity' not in results or results['equity'].empty:
        print("⚠️ Pas de données d'équité disponibles")
        return fig
        
    equity = results['equity']
    trades = results.get('trades', pd.DataFrame())
    
    # 1. Évolution du capital avec zones de profit/perte
    ax1 = plt.subplot(4, 2, 1)
    equity_pct = (equity / equity.iloc[0] - 1) * 100
    ax1.plot(equity.index, equity_pct, 'b-', linewidth=2, label='Performance (%)')
    ax1.fill_between(equity.index, equity_pct, 0, where=(equity_pct >= 0), 
                     color='green', alpha=0.3, label='Profit')
    ax1.fill_between(equity.index, equity_pct, 0, where=(equity_pct < 0), 
                     color='red', alpha=0.3, label='Perte')
    ax1.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax1.set_title('📈 Évolution du Capital (%)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Performance (%)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Drawdown (pic de perte)
    ax2 = plt.subplot(4, 2, 2)
    running_max = equity.expanding().max()
    drawdown = (equity - running_max) / running_max * 100
    ax2.fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.7)
    ax2.plot(drawdown.index, drawdown, 'darkred', linewidth=1)
    max_dd = drawdown.min()
    ax2.set_title(f'📉 Drawdown (Max: {max_dd:.2f}%)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Drawdown (%)')
    ax2.grid(True, alpha=0.3)
    
    # 3. Distribution des PnL par trade
    ax3 = plt.subplot(4, 2, 3)
    if not trades.empty and 'pnl_pct' in trades.columns:
        pnl_values = trades['pnl_pct'].dropna()
        if not pnl_values.empty:
            ax3.hist(pnl_values, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
            ax3.axvline(pnl_values.mean(), color='red', linestyle='--', 
                       label=f'Moyenne: {pnl_values.mean():.2f}%')
            ax3.axvline(0, color='black', linestyle='-', alpha=0.5)
            ax3.set_title('📊 Distribution des PnL par Trade', fontsize=12, fontweight='bold')
            ax3.set_xlabel('PnL (%)')
            ax3.set_ylabel('Fréquence')
            ax3.legend()
        else:
            ax3.text(0.5, 0.5, 'Aucune donnée PnL', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('📊 Distribution des PnL par Trade', fontsize=12, fontweight='bold')
    else:
        ax3.text(0.5, 0.5, 'Aucun trade disponible', ha='center', va='center', transform=ax3.transAxes)
        ax3.set_title('📊 Distribution des PnL par Trade', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. PnL cumulé par trade
    ax4 = plt.subplot(4, 2, 4)
    if not trades.empty and 'pnl_pct' in trades.columns:
        pnl_cumul = trades['pnl_pct'].cumsum()
        ax4.plot(range(len(pnl_cumul)), pnl_cumul, 'g-', linewidth=2, marker='o', markersize=3)
        ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax4.fill_between(range(len(pnl_cumul)), pnl_cumul, 0, where=(pnl_cumul >= 0), 
                        color='green', alpha=0.3)
        ax4.fill_between(range(len(pnl_cumul)), pnl_cumul, 0, where=(pnl_cumul < 0), 
                        color='red', alpha=0.3)
        ax4.set_title('💰 PnL Cumulé par Trade', fontsize=12, fontweight='bold')
        ax4.set_xlabel('Numéro du Trade')
        ax4.set_ylabel('PnL Cumulé (%)')
    else:
        ax4.text(0.5, 0.5, 'Aucun trade disponible', ha='center', va='center', transform=ax4.transAxes)
        ax4.set_title('💰 PnL Cumulé par Trade', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # 5. Prix BTC avec signaux et zones de volatilité
    ax5 = plt.subplot(4, 2, 5)
    ax5.plot(df.index, df['close'], 'k-', linewidth=1, alpha=0.8, label='Prix BTC/USDT')
    
    # Signaux de trading
    signals = df[df['signal'] == 1] if 'signal' in df.columns else pd.DataFrame()
    if not signals.empty:
        ax5.scatter(signals.index, signals['close'], 
                   color='red', marker='^', s=100, label='Signaux Straddle', zorder=5)
    
    ax5.set_title('📈 Prix BTC/USDT avec Signaux', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Prix ($)')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Analyse de volatilité avec zones de trading
    ax6 = plt.subplot(4, 2, 6)
    if 'vol_percentile' in df.columns:
        ax6.plot(df.index, df['vol_percentile'], 'purple', linewidth=1.5, label='Volatilité')
        ax6.axhline(y=75, color='red', linestyle='--', linewidth=2, label='Seuil Trading (75%)')
        ax6.fill_between(df.index, df['vol_percentile'], 75, 
                        where=(df['vol_percentile'] >= 75), 
                        color='red', alpha=0.2, label='Zone de Trading')
        
        if not signals.empty:
            ax6.scatter(signals.index, signals['vol_percentile'], 
                       color='red', marker='o', s=50, label='Signaux')
        
        ax6.set_title('📊 Analyse de Volatilité', fontsize=12, fontweight='bold')
        ax6.set_ylabel('Percentile de Volatilité')
        ax6.legend()
    else:
        ax6.text(0.5, 0.5, 'Données de volatilité non disponibles', 
                ha='center', va='center', transform=ax6.transAxes)
        ax6.set_title('📊 Analyse de Volatilité', fontsize=12, fontweight='bold')
    ax6.grid(True, alpha=0.3)
    
    # 7. Métriques de performance clés
    ax7 = plt.subplot(4, 2, 7)
    ax7.axis('off')
    
    # Calculer les métriques
    total_return = ((equity.iloc[-1] / equity.iloc[0]) - 1) * 100
    max_drawdown = drawdown.min()
    sharpe_ratio = calculate_sharpe_ratio(equity)
    
    win_rate = 0
    avg_win = 0
    avg_loss = 0
    total_trades = 0
    
    if not trades.empty and 'pnl_pct' in trades.columns:
        pnl_clean = trades['pnl_pct'].dropna()
        if not pnl_clean.empty:
            total_trades = len(pnl_clean)
            winning_trades = len(pnl_clean[pnl_clean > 0])
            win_rate = (winning_trades / total_trades) * 100
            
            wins = pnl_clean[pnl_clean > 0]
            losses = pnl_clean[pnl_clean < 0]
            avg_win = wins.mean() if not wins.empty else 0
            avg_loss = losses.mean() if not losses.empty else 0
    
    # Texte des métriques
    metrics_text = f"""
    📊 MÉTRIQUES DE PERFORMANCE
    
    💰 Rendement Total: {total_return:.2f}%
    📉 Drawdown Max: {max_drawdown:.2f}%
    📈 Ratio de Sharpe: {sharpe_ratio:.2f}
    
    🔄 Nombre de Trades: {total_trades}
    🎯 Taux de Réussite: {win_rate:.1f}%
    🟢 Gain Moyen: {avg_win:.2f}%
    🔴 Perte Moyenne: {avg_loss:.2f}%
    
    ⚖️ Ratio Gain/Perte: {abs(avg_win/avg_loss):.2f if avg_loss != 0 else 'N/A'}
    """
    
    ax7.text(0.1, 0.9, metrics_text, transform=ax7.transAxes, fontsize=11,
             verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray"))
    
    # 8. Evolution mensuelle des returns
    ax8 = plt.subplot(4, 2, 8)
    if len(equity) > 30:  # Si on a assez de données
        try:
            equity_monthly = equity.resample('M').last()
            monthly_returns = equity_monthly.pct_change().dropna() * 100
            
            colors = ['green' if x >= 0 else 'red' for x in monthly_returns]
            bars = ax8.bar(range(len(monthly_returns)), monthly_returns, color=colors, alpha=0.7)
            ax8.axhline(y=0, color='black', linestyle='-', alpha=0.5)
            ax8.set_title('📅 Rendements Mensuels', fontsize=12, fontweight='bold')
            ax8.set_ylabel('Rendement (%)')
            ax8.set_xlabel('Mois')
            
            # Ajouter les valeurs sur les barres
            for i, (bar, value) in enumerate(zip(bars, monthly_returns)):
                ax8.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (0.1 if value >= 0 else -0.3),
                        f'{value:.1f}%', ha='center', va='bottom' if value >= 0 else 'top', fontsize=8)
        except:
            ax8.text(0.5, 0.5, 'Pas assez de données pour l\'analyse mensuelle', 
                    ha='center', va='center', transform=ax8.transAxes)
            ax8.set_title('📅 Rendements Mensuels', fontsize=12, fontweight='bold')
    else:
        ax8.text(0.5, 0.5, 'Pas assez de données pour l\'analyse mensuelle', 
                ha='center', va='center', transform=ax8.transAxes)
        ax8.set_title('📅 Rendements Mensuels', fontsize=12, fontweight='bold')
    ax8.grid(True, alpha=0.3)
    
    plt.tight_layout(pad=3.0)
    
    # Sauvegarder avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'output/advanced_pnl_analysis_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"📊 Analyse PnL avancée sauvegardée: {filename}")
    
    plt.show()
    return fig

def calculate_sharpe_ratio(equity_series, risk_free_rate=0.02):
    """Calcule le ratio de Sharpe"""
    try:
        returns = equity_series.pct_change().dropna()
        if len(returns) == 0:
            return 0
        
        excess_returns = returns.mean() * 252 - risk_free_rate  # Annualisé
        volatility = returns.std() * np.sqrt(252)  # Annualisé
        
        return excess_returns / volatility if volatility != 0 else 0
    except:
        return 0

def print_advanced_results(results):
    """
    Affiche les résultats de manière détaillée avec analyse des causes de pertes
    
    Args:
        results: Résultats du backtest
    """
    print("\n" + "="*80)
    print("🎯 ANALYSE COMPLÈTE DES PERFORMANCES - STRADDLE BTC")
    print("="*80)
    
    equity = results.get('equity', pd.Series())
    trades = results.get('trades', pd.DataFrame())
    
    if equity.empty:
        print("⚠️ Aucune donnée d'équité disponible")
        return
    
    # Métriques de base
    initial_capital = equity.iloc[0]
    final_capital = equity.iloc[-1]
    total_return = ((final_capital / initial_capital) - 1) * 100
    
    print(f"💰 PERFORMANCE FINANCIÈRE")
    print(f"   Capital Initial: ${initial_capital:,.2f}")
    print(f"   Capital Final: ${final_capital:,.2f}")
    print(f"   Profit/Perte: ${final_capital - initial_capital:,.2f}")
    print(f"   Rendement Total: {total_return:.2f}%")
    
    # Analyse du drawdown
    running_max = equity.expanding().max()
    drawdown = (equity - running_max) / running_max * 100
    max_drawdown = drawdown.min()
    
    print(f"\n📉 ANALYSE DES RISQUES")
    print(f"   Drawdown Maximum: {max_drawdown:.2f}%")
    print(f"   Volatilité: {equity.pct_change().std() * np.sqrt(252) * 100:.2f}%")
    
    # Ratio de Sharpe
    sharpe = calculate_sharpe_ratio(equity)
    print(f"   Ratio de Sharpe: {sharpe:.2f}")
    
    # Analyse des trades
    if not trades.empty and 'pnl_pct' in trades.columns:
        pnl_clean = trades['pnl_pct'].dropna()
        if not pnl_clean.empty:
            total_trades = len(pnl_clean)
            winning_trades = len(pnl_clean[pnl_clean > 0])
            losing_trades = len(pnl_clean[pnl_clean < 0])
            win_rate = (winning_trades / total_trades) * 100
            
            wins = pnl_clean[pnl_clean > 0]
            losses = pnl_clean[pnl_clean < 0]
            avg_win = wins.mean() if not wins.empty else 0
            avg_loss = losses.mean() if not losses.empty else 0
            
            print(f"\n🔄 STATISTIQUES DE TRADING")
            print(f"   Nombre Total de Trades: {total_trades}")
            print(f"   🟢 Trades Gagnants: {winning_trades} ({win_rate:.1f}%)")
            print(f"   � Trades Perdants: {losing_trades} ({100-win_rate:.1f}%)")
            print(f"   💰 Gain Moyen: +{avg_win:.2f}%")
            print(f"   💥 Perte Moyenne: {avg_loss:.2f}%")
            
            if avg_loss != 0:
                profit_factor = abs(avg_win / avg_loss)
                print(f"   ⚖️ Ratio Gain/Perte: {profit_factor:.2f}")
            
            # Meilleur et pire trade
            best_trade = pnl_clean.max()
            worst_trade = pnl_clean.min()
            print(f"   🚀 Meilleur Trade: +{best_trade:.2f}%")
            print(f"   💀 Pire Trade: {worst_trade:.2f}%")
            
            # Séries de gains/pertes
            consecutive_wins = 0
            consecutive_losses = 0
            current_wins = 0
            current_losses = 0
            max_wins = 0
            max_losses = 0
            
            for pnl in pnl_clean:
                if pnl > 0:
                    current_wins += 1
                    current_losses = 0
                    max_wins = max(max_wins, current_wins)
                else:
                    current_losses += 1
                    current_wins = 0
                    max_losses = max(max_losses, current_losses)
            
            print(f"   📈 Série de gains max: {max_wins}")
            print(f"   � Série de pertes max: {max_losses}")
    
    # Diagnostic des problèmes
    print(f"\n🔍 DIAGNOSTIC DES PROBLÈMES")
    
    if total_return < 0:
        print("   ❌ STRATÉGIE PERDANTE - Causes possibles:")
        
        if not trades.empty and 'pnl_pct' in trades.columns:
            pnl_clean = trades['pnl_pct'].dropna()
            if not pnl_clean.empty:
                win_rate = len(pnl_clean[pnl_clean > 0]) / len(pnl_clean) * 100
                
                if win_rate < 40:
                    print("   🎯 Taux de réussite trop faible (<40%)")
                    print("       → Augmenter le seuil de volatilité")
                    print("       → Améliorer les filtres de signaux")
                
                avg_win = pnl_clean[pnl_clean > 0].mean() if len(pnl_clean[pnl_clean > 0]) > 0 else 0
                avg_loss = abs(pnl_clean[pnl_clean < 0].mean()) if len(pnl_clean[pnl_clean < 0]) > 0 else 0
                
                if avg_loss > avg_win:
                    print("   💰 Pertes moyennes > Gains moyens")
                    print("       → Augmenter Take Profit")
                    print("       → Réduire Stop Loss")
        
        if max_drawdown < -20:
            print("   📉 Drawdown excessif (>20%)")
            print("       → Réduire la taille des positions")
            print("       → Améliorer la gestion des risques")
        
        print("   📅 Période de marché défavorable")
        print("       → Tester sur d'autres périodes")
        print("       → Ajouter des filtres de tendance")
    
    elif total_return > 0:
        print("   ✅ STRATÉGIE PROFITABLE")
        if total_return > 20:
            print("   🚀 Performance excellente!")
        elif total_return > 10:
            print("   👍 Performance satisfaisante")
        else:
            print("   📈 Performance modeste mais positive")
    
    # Recommandations
    print(f"\n💡 RECOMMANDATIONS D'AMÉLIORATION")
    
    if not trades.empty and 'pnl_pct' in trades.columns:
        pnl_clean = trades['pnl_pct'].dropna()
        if not pnl_clean.empty:
            win_rate = len(pnl_clean[pnl_clean > 0]) / len(pnl_clean) * 100
            
            if win_rate < 50:
                print("   1. 🎯 Améliorer la sélection des signaux:")
                print("      • Augmenter VOLATILITY_THRESHOLD à 80-85%")
                print("      • Ajouter des filtres de tendance")
                print("      • Éviter les périodes de faible volatilité")
            
            if total_return < 10:
                print("   2. 💰 Optimiser les paramètres de profit:")
                print("      • Augmenter TAKE_PROFIT_MULTIPLIER à 2.5-3.0")
                print("      • Ajuster STOP_LOSS_MULTIPLIER à 1.0-1.2")
            
            if max_drawdown < -15:
                print("   3. 🛡️ Améliorer la gestion des risques:")
                print("      • Réduire RISK_PER_TRADE à 1.5%")
                print("      • Limiter le nombre de positions simultanées")
                print("      • Ajouter un stop loss dynamique")
    
    print("   4. 📊 Utiliser l'optimisation automatique:")
    print("      • Lancer optimize_strategy.py")
    print("      • Tester sur différentes périodes")
    print("      • Analyser la robustesse des paramètres")
    
    print("="*80)

# Fonction de compatibilité (ancien nom)
def create_simple_charts(df, results):
    """Fonction de compatibilité - redirige vers l'analyse avancée"""
    return create_advanced_pnl_analysis(df, results)

def print_simple_results(results):
    """Fonction de compatibilité - redirige vers l'analyse avancée"""
    return print_advanced_results(results)
    
