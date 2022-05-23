from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from eclipse_parser.common import TEST_DATA
from eclipse_parser.parser import EclipseParser

_test_schedule: Path = TEST_DATA.joinpath("test_schedule.inc")
_not_inc_file_path: Path = TEST_DATA.joinpath("reference_result.csv")
_empty_file_path: Path = TEST_DATA.joinpath("empty_file.inc")
_test_raw_string: str = (
    "COMPDAT\n"
    "-- с двух тире начинается комментарий\n"
    "'W1' 10 10  1   3 \tOPEN \t1* \t1\t2 \t1 \t3* \t\t\t1.0 /  -- и комментарии "
    "могут быть\n"
    "'W2' 32 10  1   3 \tOPEN \t1* \t1 \t2 \t1 \t3* \t\t\t2.0 /\n"
    "/  -- практически где угодно\n"
    "\n"
    "COMPDAT\n"
    "-- если у нас несколько секций на одну дату, то их имеет смысл объединить в "
    "одну\n"
    "'W3' 5  36  2   2 \tOPEN \t1* \t1 \t2 \t1 \t3* \t\t\t3.0 /\n"
    "'W4' 40 30  1   3 \tOPEN \t1* \t1 \t2 \t1 \t3* \t\t\t4.0 /\n"
    "/\n"
    "\n"
    "COMPDAT\n"
    "-- эти три секции (одна, разбитая на три) вне дат, но мы не должны их "
    "потерять при парсинге\n"
    "'W5' 21 21  4   4 \tOPEN \t1* \t1 \t2 \t1\t3* \t\t\t5.0 /\n"
    "/\n"
    "\n"
    "\n"
    "\n"
    "           \n"
    "\n"
    "\n"
    "\n"
    "\n"
    "\n"
    "\t\n"
    "\t\n"
    "DATES\n"
    "01 JUN 2018 /\n"
    "/\n"
    "\n"
    "-- есть еще множество других ключевых слов, например, WEFAC,\n"
    "-- но они нас не интересуют в этой задаче, можем смело их пропускать\n"
    "-- кстати, на эту дату нет интересующих нас секций\n"
    "WEFAC\n"
    " W1\t1.0\t/\n"
    "/\n"
    "\n"
    "DATES\n"
    "01 JUL 2018 /\n"
    "/\n"
    "\n"
    "COMPDAT\n"
    "'W3' 32 10  1   1 \tOPEN \t1* \t1 \t2 \t1 \t3* \t\t\t1.0718 /\n"
    "'W5' 21 21  1   3 \tOPEN \t1* \t1 \t2 \t1\t3* \t\t\t5.0 /\n"
    "/\n"
    "\n"
    "DATES\n"
    "01 AUG 2018 /  -- даты можно объединять,\n"
    "01 SEP 2018 /  -- но только на последнюю мы получим отчет\n"
    "/\n"
    "\n"
    "COMPDAT\n"
    "'W1' 10 10  2   3 \tOPEN \t1* \t1\t2 \t1 \t3* \t\t\t1.0918 /\n"
    "'W2' 32 10  1   2 \tOPEN \t1* \t1 \t2 \t1 \t3* \t\t\t2.0 /\n"
    "/\n"
    "\n"
    "COMPDATL\n"
    "'W3' 'LGR1' 10 10  2   2 \tOPEN \t1* \t1\t2 \t1 \t3* \t\t\t1.0918 /\n"
    "/\n"
    "\n"
    "DATES\n"
    "01 OCT 2018 /\n"
    "/\n"
    "\n"
    "DATES\n"
    "01 NOV 2018 /\n"
    "/\n"
    "\n"
    "DATES\n"
    "01 DEC 2018 /\n"
    "/\n"
    "\n"
    "END\n"
)
_reference_processed_raw_string: list[str] = [
    "COMPDAT",
    "W1 10 10 1 3 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 1.0",
    "W2 32 10 1 3 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 2.0",
    "COMPDAT",
    "W3 5 36 2 2 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 3.0",
    "W4 40 30 1 3 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 4.0",
    "COMPDAT",
    "W5 21 21 4 4 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 5.0",
    "DATES",
    "01 JUN 2018",
    "DATES",
    "01 JUL 2018",
    "COMPDAT",
    "W3 32 10 1 1 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 1.0718",
    "W5 21 21 1 3 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 5.0",
    "DATES",
    "01 AUG 2018",
    "01 SEP 2018",
    "COMPDAT",
    "W1 10 10 2 3 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 1.0918",
    "W2 32 10 1 2 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 2.0",
    "COMPDATL",
    "W3 LGR1 10 10 2 2 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 1.0918",
    "DATES",
    "01 OCT 2018",
    "DATES",
    "01 NOV 2018",
    "DATES",
    "01 DEC 2018",
    "END",
    "",
]
_test_dict_to_append: dict = {
    "COMPDAT": [
        "W1 10 10 1 3 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 1.0",
        "W2 32 10 1 3 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 2.0",
        "W3 5 36 2 2 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 3.0",
        "W4 40 30 1 3 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 4.0",
        "W5 21 21 4 4 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 5.0",
    ],
    "COMPDATL": [],
    "DATES": [],
}
_append_reference: pd.DataFrame = (
    pd.read_csv(TEST_DATA.joinpath("reference_result.csv"))
    .replace({np.nan: None})
    .iloc[:5]
)
_test_block_to_parse: list[str] = [
    "COMPDAT",
    "W1 10 10 1 3 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 1.0",
    "W2 32 10 1 3 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 2.0",
    "COMPDAT",
    "W3 5 36 2 2 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 3.0",
    "W4 40 30 1 3 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 4.0",
    "COMPDAT",
    "W5 21 21 4 4 OPEN DEFAULT 1 2 1 DEFAULT DEFAULT DEFAULT 5.0",
]


@pytest.mark.parametrize(
    "not_inc_file_path",
    [_not_inc_file_path],
)
def test_file_suffix_check(
    not_inc_file_path,
):
    with pytest.raises(ValueError):
        EclipseParser(file_path=not_inc_file_path)


@pytest.mark.parametrize(
    "not_file_path",
    [TEST_DATA],
)
def test_not_a_file_check(
    not_file_path,
):
    with pytest.raises(ValueError):
        EclipseParser(file_path=not_file_path)


@pytest.mark.parametrize(
    "empty_file_path",
    [_empty_file_path],
)
def test_empty_file_check(
    empty_file_path,
):
    with pytest.raises(ValueError):
        EclipseParser(file_path=empty_file_path)


@pytest.mark.parametrize(
    "raw_string,reference_result,file_path",
    [(_test_raw_string, _reference_processed_raw_string, _test_schedule)],
)
def test_raw_string_processing(
    raw_string,
    reference_result,
    file_path,
):
    parser_obj = EclipseParser(file_path=file_path)

    assert parser_obj._clear_raw_string(raw_string) == reference_result


@pytest.mark.parametrize(
    "dict_to_append,reference,file_path",
    [(_test_dict_to_append, _append_reference, _test_schedule)],
)
def test_append_method(
    dict_to_append,
    reference,
    file_path,
):
    parser_obj = EclipseParser(file_path=file_path)
    parser_obj.append(dict_to_append)

    assert parser_obj.frame.equals(reference)


@pytest.mark.parametrize(
    "test_input,reference,file_path",
    [(_test_block_to_parse, _test_dict_to_append, _test_schedule)],
)
def test_key_word_block_processing(
    test_input,
    reference,
    file_path,
):
    parser_obj = EclipseParser(file_path=file_path)

    assert parser_obj._process_key_word_block(test_input) == reference
