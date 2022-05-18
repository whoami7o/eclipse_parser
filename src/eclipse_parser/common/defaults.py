from pathlib import Path
from typing import Final

PROJECT_ROOT: Final[Path] = Path(__file__).parent.parent.parent.parent
DATA_DIR: Final[Path] = PROJECT_ROOT.joinpath("data")
RESULTS_DIR: Final[Path] = PROJECT_ROOT.joinpath("results")

KEY_WORDS_TO_PARSE: Final[tuple[str, str, str]] = (
    "DATES",
    "COMPDAT",
    "COMPDATL",
)
