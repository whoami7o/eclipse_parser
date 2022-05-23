from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from eclipse_parser.common import TEST_DATA
from eclipse_parser.parser import EclipseParser

_reference_output: pd.DataFrame = pd.read_csv(
    TEST_DATA.joinpath("reference_result.csv")
).replace({np.nan: None})
_test_schedule: Path = TEST_DATA.joinpath("test_schedule.inc")


@pytest.mark.parametrize(
    "test_schedule, reference_output", [(_test_schedule, _reference_output)]
)
def test_parser_integrated(
    test_schedule,
    reference_output,
):

    parser_obj = EclipseParser(file_path=test_schedule)

    parser_obj.parse_file()

    assert parser_obj.frame.equals(reference_output)


@pytest.mark.xfail
@pytest.mark.parametrize(
    "test_schedule, reference_output", [(_test_schedule, _reference_output)]
)
def test_chunks_read(
    test_schedule,
    reference_output,
):
    parser_obj = EclipseParser(
        file_path=test_schedule,
        read_chunks=10,
    )

    assert parser_obj.frame.equals(reference_output)
