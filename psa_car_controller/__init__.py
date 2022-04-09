from pathlib import Path
from single_source import get_version

__version__ = get_version(__name__, Path(__file__), default_return="dev")
