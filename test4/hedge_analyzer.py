# Analyseur d'opportunités de hedging pour straddle

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def analyze_hedge_opportunities(results):
    """Analyse les opportunités de hedging détectées"""
    
    if not results['hedge_opportunities']:
        print("❌ Aucune opportunité de hedge détectée")
        return
    
    hedge_df = pd.DataFrame(results['hedge_opportunities'])
    
    print("\n🛡️ ANALYSE DES OPPORTUNITÉS DE HEDGING")
    print("="*60)
    
    # Statistiques générales
    total_hedges = len(hedge_df)
    print(f"📊 Total opportunités détectées: {total_hedges}")
    
    # Types de hedge
    hedge_types = hedge_df['hedge_info'].apply(lambda x: x.get('type', 'Unknown')).value_counts()
    print(f"\n📈 Types de hedge:")
    for hedge_type, count in hedge_types.items():
        percentage = (count / total_hedges) * 100
        print(f"   {hedge_type}: {count} ({percentage:.1f}%)")
    
    # Urgence des hedges
    urgency_levels = hedge_df['hedge_info'].apply(lambda x: x.get('urgency', 'Unknown')).value_counts()
    print(f"\n🚨 Niveaux d'urgence:")
    for urgency, count in urgency_levels.items():
        percentage = (count / total_hedges) * 100
        print(f"   {urgency}: {count} ({percentage:.1f}%)")
    
    # Taille moyenne des hedges recommandés
    hedge_sizes = hedge_df['hedge_info'].apply(lambda x: x.get('size_ratio', 0))
    avg_hedge_size = hedge_sizes.mean()
    print(f"\n📏 Taille moyenne de hedge recommandée: {avg_hedge_size:.1%}")
    
    # Distribution par jour
    hedge_df['date'] = pd.to_datetime(hedge_df['timestamp']).dt.date
    daily_hedges = hedge_df.groupby('date').size()
    
    print(f"\n📅 Distribution temporelle:")
    print(f"   Jours avec hedges: {len(daily_hedges)}")
    print(f"   Hedges par jour (moyenne): {daily_hedges.mean():.1f}")
    print(f"   Maximum en un jour: {daily_hedges.max()}")
    
    return hedge_df

def simulate_hedged_strategy(results, hedge_implementation_rate=0.5):
    """Simule l'impact d'implémenter les hedges recommandés"""
    
    if not results['trades']:
        print("❌ Aucun trade pour simulation")
        return
    
    print(f"\n💼 SIMULATION AVEC HEDGING ({hedge_implementation_rate:.0%} d'implémentation)")
    print("="*60)
    
    trades_df = pd.DataFrame(results['trades'])
    original_pnl = trades_df['pnl'].sum()
    
    # Supposer que les hedges réduisent les pertes de 30% en moyenne
    hedge_benefit = 0.3
    
    # Identifier les trades avec opportunités de hedge
    hedge_times = set()
    if results['hedge_opportunities']:
        hedge_df = pd.DataFrame(results['hedge_opportunities'])
        hedge_times = set(hedge_df['timestamp'])
    
    # Simuler l'impact du hedging
    hedged_pnl = 0
    hedged_trades = 0
    
    for _, trade in trades_df.iterrows():
        trade_pnl = trade['pnl']
        
        # Vérifier si ce trade avait des opportunités de hedge
        had_hedge_opportunity = trade['entry_time'] in hedge_times
        
        if had_hedge_opportunity and np.random.random() < hedge_implementation_rate:
            # Hedge implémenté
            if trade_pnl < 0:  # Perte réduite
                hedged_trade_pnl = trade_pnl * (1 - hedge_benefit)
                hedged_trades += 1
            else:  # Profit légèrement réduit (coût du hedge)
                hedged_trade_pnl = trade_pnl * 0.95
        else:
            # Pas de hedge
            hedged_trade_pnl = trade_pnl
        
        hedged_pnl += hedged_trade_pnl
    
    improvement = hedged_pnl - original_pnl
    improvement_pct = (improvement / abs(original_pnl)) * 100 if original_pnl != 0 else 0
    
    print(f"📊 PnL original: ${original_pnl:.2f}")
    print(f"📊 PnL avec hedging: ${hedged_pnl:.2f}")
    print(f"📈 Amélioration: ${improvement:.2f} ({improvement_pct:+.1f}%)")
    print(f"🛡️ Trades hedgés: {hedged_trades}/{len(trades_df)}")
    
    return {
        'original_pnl': original_pnl,
        'hedged_pnl': hedged_pnl,
        'improvement': improvement,
        'hedged_trades': hedged_trades
    }

def create_hedge_analysis_chart(hedge_df, results):
    """Crée des graphiques d'analyse du hedging"""
    
    if hedge_df is None or len(hedge_df) == 0:
        print("❌ Pas de données de hedge pour graphiques")
        return
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle('🛡️ Analyse des Opportunités de Hedging', fontsize=16, fontweight='bold')
    
    # 1. Types de hedge
    hedge_types = hedge_df['hedge_info'].apply(lambda x: x.get('type', 'Unknown')).value_counts()
    colors = ['lightcoral' if t == 'SHORT' else 'lightblue' for t in hedge_types.index]
    
    ax1.bar(hedge_types.index, hedge_types.values, color=colors, alpha=0.7)
    ax1.set_title('Distribution des Types de Hedge')
    ax1.set_ylabel('Nombre d\'Opportunités')
    ax1.grid(True, alpha=0.3)
    
    # 2. Distribution temporelle
    hedge_df['date'] = pd.to_datetime(hedge_df['timestamp']).dt.date
    daily_hedges = hedge_df.groupby('date').size()
    
    ax2.plot(daily_hedges.index, daily_hedges.values, marker='o', linewidth=1, markersize=4)
    ax2.set_title('Opportunités de Hedge par Jour')
    ax2.set_ylabel('Nombre d\'Opportunités')
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # 3. Tailles de hedge recommandées
    hedge_sizes = hedge_df['hedge_info'].apply(lambda x: x.get('size_ratio', 0)) * 100
    
    ax3.hist(hedge_sizes, bins=15, alpha=0.7, color='orange', edgecolor='black')
    ax3.axvline(x=hedge_sizes.mean(), color='red', linestyle='--', 
               label=f'Moyenne: {hedge_sizes.mean():.1f}%')
    ax3.set_title('Distribution des Tailles de Hedge')
    ax3.set_xlabel('Taille de Hedge (%)')
    ax3.set_ylabel('Fréquence')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Urgence vs Performance
    if results['trades']:
        trades_df = pd.DataFrame(results['trades'])
        
        # Mapper les urgences
        urgency_map = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        urgencies = hedge_df['hedge_info'].apply(lambda x: urgency_map.get(x.get('urgency', 'LOW'), 1))
        sizes = hedge_df['hedge_info'].apply(lambda x: x.get('size_ratio', 0)) * 100
        
        colors = ['red' if u == 3 else 'orange' if u == 2 else 'yellow' for u in urgencies]
        
        scatter = ax4.scatter(urgencies, sizes, c=colors, alpha=0.6, s=60)
        ax4.set_title('Urgence vs Taille de Hedge')
        ax4.set_xlabel('Niveau d\'Urgence')
        ax4.set_ylabel('Taille de Hedge (%)')
        ax4.set_xticks([1, 2, 3])
        ax4.set_xticklabels(['LOW', 'MEDIUM', 'HIGH'])
        ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Sauvegarder
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f'hedge_analysis_{timestamp}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"📊 Graphiques hedge sauvegardés: {filename}")
    
    plt.show()

def generate_hedge_implementation_guide(hedge_df):
    """Génère un guide d'implémentation des hedges"""
    
    print("\n📋 GUIDE D'IMPLÉMENTATION DES HEDGES")
    print("="*60)
    
    if hedge_df is None or len(hedge_df) == 0:
        print("❌ Aucune opportunité de hedge à implémenter")
        return
    
    # Grouper par type et urgence
    hedge_summary = hedge_df.groupby([
        hedge_df['hedge_info'].apply(lambda x: x.get('type', 'Unknown')),
        hedge_df['hedge_info'].apply(lambda x: x.get('urgency', 'Unknown'))
    ]).size().reset_index(name='count')
    
    print("🎯 Priorités d'implémentation:")
    print("\n1. 🚨 HEDGES HAUTE URGENCE (à implémenter immédiatement)")
    high_urgency = hedge_df[hedge_df['hedge_info'].apply(lambda x: x.get('urgency') == 'HIGH')]
    
    if len(high_urgency) > 0:
        for _, hedge in high_urgency.iterrows():
            hedge_info = hedge['hedge_info']
            print(f"   • Type: {hedge_info.get('type', 'Unknown')}")
            print(f"     Taille: {hedge_info.get('size_ratio', 0):.1%}")
            print(f"     Raison: {hedge_info.get('reason', 'N/A')}")
            print()
    else:
        print("   ✅ Aucun hedge haute urgence")
    
    print("2. ⚠️ HEDGES URGENCE MOYENNE (à considérer)")
    medium_urgency = hedge_df[hedge_df['hedge_info'].apply(lambda x: x.get('urgency') == 'MEDIUM')]
    print(f"   Total: {len(medium_urgency)} opportunités")
    
    print("\n3. 💡 RECOMMANDATIONS GÉNÉRALES:")
    print("   • Implémenter 50-70% des hedges recommandés")
    print("   • Prioriser les hedges SHORT en market haussier")
    print("   • Prioriser les hedges LONG en market baissier")
    print("   • Limiter la taille totale des hedges à 30% du portfolio")
    print("   • Réviser les hedges toutes les 4-6 heures")
    
    # Calcul du coût estimé
    avg_hedge_size = hedge_df['hedge_info'].apply(lambda x: x.get('size_ratio', 0)).mean()
    estimated_cost = avg_hedge_size * 0.02  # 2% de coût estimé pour le hedging
    
    print(f"\n💰 COÛT ESTIMÉ DU HEDGING:")
    print(f"   Taille moyenne: {avg_hedge_size:.1%}")
    print(f"   Coût estimé: {estimated_cost:.2%} du capital par hedge")
    print(f"   Impact sur rendement: -1% à -3% (mais réduction du risque)")

if __name__ == "__main__":
    print("🛡️ Module d'analyse de hedging pour stratégie straddle")
    print("Ce module est conçu pour être utilisé avec les résultats de backtest")
