from __future__ import annotations

import sys
from pathlib import Path

# Assicura che la root del progetto (E:\CLONAZIONE\tpi_evoluto)
# sia nel sys.path, così `import app.main` funziona anche sotto pytest.
ROOT = Path(__file__).resolve().parents[1]
root_str = str(ROOT)
if root_str not in sys.path:
    sys.path.insert(0, root_str)
