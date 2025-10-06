from pathlib import Path
from dotenv import load_dotenv

# Ensure the project's .env is loaded for all tests
project_root = Path(__file__).resolve().parents[2]
dotenv_path = project_root / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path, override=True)
