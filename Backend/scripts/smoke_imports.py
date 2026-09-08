"""Smoke import script to check compiled modules after recent edits."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

modules = [
    'app.services.fin.payment_receipt_service',
    'app.api.v1.fin.payment_receipts',
]
for m in modules:
    try:
        __import__(m)
        print(f'imported {m}')
    except Exception as e:
        print(f'FAILED importing {m}:', e)
        raise
print('smoke imports OK')
