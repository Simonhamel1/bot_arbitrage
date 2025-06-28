# Test simple pour vérifier la configuration

from config import *

print("Configuration loaded:")
print(f"COMMISSION_RATE = {COMMISSION_RATE}")

from straddle_strategy import StraddleStrategy
print("StraddleStrategy imported successfully")
