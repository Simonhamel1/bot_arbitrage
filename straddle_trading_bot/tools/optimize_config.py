# Configuration automatique pour optimiser l'activité du bot
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import shutil

print("🔧 CONFIGURATION AUTOMATIQUE POUR PLUS D'ACTIVITÉ")
print("=" * 55)

config_file = Path("src/config.py")
backup_file = Path("src/config_backup.py")

# Faire une sauvegarde
if config_file.exists():
    shutil.copy2(config_file, backup_file)
    print(f"✅ Sauvegarde créée: {backup_file}")

# Lire le fichier actuel
with open(config_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Modifications à apporter
modifications = [
    ("VOLATILITY_THRESHOLD = 55", "VOLATILITY_THRESHOLD = 35"),
    ("VOLATILITY_THRESHOLD = 40", "VOLATILITY_THRESHOLD = 35"),  # Au cas où déjà modifié
    ("MIN_SIGNAL_QUALITY = 0.75", "MIN_SIGNAL_QUALITY = 0.60"),
    ("MIN_SIGNAL_QUALITY = 0.65", "MIN_SIGNAL_QUALITY = 0.60"),  # Au cas où déjà modifié
    ("CURRENT_PROFILE = 'BALANCED'", "CURRENT_PROFILE = 'AGGRESSIVE'"),
    ("TIMEFRAME = '1h'", "TIMEFRAME = '5m'"),
    ("MIN_VOLUME_RATIO = 1.2", "MIN_VOLUME_RATIO = 1.0"),
    ("MAX_PRICE_RANGE = 0.06", "MAX_PRICE_RANGE = 0.08"),
]

changes_made = []
for old, new in modifications:
    if old in content:
        content = content.replace(old, new)
        changes_made.append(f"   • {old} → {new}")

if changes_made:
    # Sauvegarder les modifications
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("🔧 Modifications appliquées:")
    for change in changes_made:
        print(change)
    
    print(f"\n✅ Configuration optimisée sauvegardée dans {config_file}")
    print(f"📋 Sauvegarde disponible dans {backup_file}")
    
    print("\n🎯 PROCHAINES ÉTAPES:")
    print("1. Lancez: python main.py")
    print("2. Si vous voulez restaurer: mv src/config_backup.py src/config.py")
    
else:
    print("ℹ️ Aucune modification nécessaire - configuration déjà optimisée")

print("\n💡 PARAMÈTRES OPTIMISÉS:")
print("   🎯 Seuil volatilité: 35% (plus permissif)")
print("   🎯 Qualité signal: 0.60 (moins sélectif)")
print("   🎯 Profil: AGGRESSIVE (plus de trades)")
print("   🎯 Timeframe: 5m (plus d'opportunités)")
print("   🎯 Volume ratio: 1.0 (assoupli)")
print("   🎯 Price range: 0.08 (assoupli)")
