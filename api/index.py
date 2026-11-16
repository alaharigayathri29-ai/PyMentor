import sys
from pathlib import Path

# Add backend directory at the very front of sys.path so 'app' refers to backend/app
root_dir = Path(__file__).resolve().parent.parent
backend_dir = root_dir / "backend"
sys.path.insert(0, str(backend_dir))
sys.path.append(str(root_dir))

from app.main import app
