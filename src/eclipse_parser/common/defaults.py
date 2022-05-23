from pathlib import Path
from typing import Final

PROJECT_ROOT: Final[Path] = Path(__file__).parent.parent.parent.parent
DATA_DIR: Final[Path] = PROJECT_ROOT.joinpath("data")
RESULTS_DIR: Final[Path] = PROJECT_ROOT.joinpath("results")
TEST_DIR: Final[Path] = PROJECT_ROOT.joinpath("tests")
TEST_DATA: Final[Path] = TEST_DIR.joinpath("test_data")

KEY_WORDS_TO_PARSE: Final[tuple[str, str, str, str]] = (
    "DATES",
    "COMPDAT",
    "COMPDATL",
    "END",
)

DEFAULT_VALUE: Final[str] = "DEFAULT"

COLUMN_NAMES: Final[tuple[str, ...]] = (
    "Date",
    "Well name",
    "Local grid name",
    "I",
    "J",
    "K upper",
    "K lower",
    "Flag on connection",
    "Saturation table",
    "Transmissibility factor",
    "Well bore diameter",
    "Effective Kh",
    "Skin factor",
    "D-factor",
    "Dir_well_penetrates_grid_block",
    "Press_eq_radius",
)
