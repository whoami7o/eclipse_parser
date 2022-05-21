import os
import re
from copy import deepcopy
from pathlib import Path
from pprint import pprint
from typing import Callable, Generator, Optional, TextIO, Union

import pandas as pd

from eclipse_parser.common.chunks_reader import chunks_reader
from eclipse_parser.common.defaults import (
    COLUMN_NAMES,
    DEFAULT_VALUE,
    KEY_WORDS_TO_PARSE,
)


class EclipseParser:

    _comment_pattern: re.Pattern = re.compile(r"--.*(\r\n*|\n)")
    _blank_line_pattern: re.Pattern = re.compile(r"(\r\n*|\n)\s*(\r\n*|\n)")
    _tab: re.Pattern = re.compile(r"\t+")
    _linesep: re.Pattern = re.compile(r"(\r\n*|\n)")
    _blocks_to_parse: re.Pattern = re.compile(
        r"({0})(\r\n*|\n)(\s|.)+?/\n/".format("|".join([_ for _ in KEY_WORDS_TO_PARSE]))
    )

    def __init__(
        self,
        file_path: Union[str, Path, os.PathLike],
        read_method: Callable[
            [TextIO, Optional[int]], Generator[Optional[int], None, None]
        ] = chunks_reader,
        file_encoding: Optional[str] = "utf-8",
        read_chunks: Optional[int] = None,
    ) -> None:

        self._file_path = file_path if isinstance(file_path, Path) else Path(file_path)

        if not self._file_path.is_file():
            raise ValueError("Passed path is not a file")

        if self._file_path.suffix != ".inc":
            raise ValueError(
                "Incorrect file type: {0}; expected: .inc".format(
                    self._file_path.suffix,
                )
            )

        if os.path.getsize(self._file_path) == 0:
            raise ValueError("File is empty")

        self._read_file = read_method
        self._file_encoding = file_encoding
        self._chunks_size = read_chunks
        self._frame: pd.DataFrame = pd.DataFrame(
            columns=COLUMN_NAMES,
        )

    @property
    def file_path(self) -> Path:
        return self._file_path

    @property
    def encoding(self) -> str:
        return self._file_encoding

    @property
    def frame(self) -> pd.DataFrame:
        return self._frame

    def parse_file(
        self,
    ) -> None:
        data: str

        with open(
            file=self._file_path,
            mode="r",
            encoding=self._file_encoding,
        ) as file:

            for data in self._read_file(file, self._chunks_size):

                i: int = 0
                blocks: list[list[str]] = []
                _block: list[str] = []

                lines = self._clear_raw_string(data)

                while True:
                    _block.append(lines[i])
                    i += 1
                    if i >= len(lines):
                        break

                    if re.fullmatch(
                        r"(DATES|END)",  # hardcoded
                        lines[i],
                    ):
                        block_to_parse = deepcopy(_block)
                        blocks.append(block_to_parse)
                        processed_block = self._process_key_word_block(block_to_parse)
                        self.append(processed_block)
                        _block.clear()

        pprint(self._frame)

    def _clear_raw_string(
        self,
        eclipse_raw_string: str,
    ) -> list[str]:

        no_comments = self.clear_comments(eclipse_raw_string)
        no_blank_lines = self.clear_blank_lines(no_comments)
        no_tabs = self.clear_tabs(no_blank_lines)
        no_unexpected_blocks = self.filter_unexpected_blocks(no_tabs)

        clear_lines = self._linesep.split(no_unexpected_blocks)
        filtered_lines = list(filter(self._empty_string, clear_lines))
        no_spaces_lines = list(map(self._clear_unnecessary_spaces, filtered_lines))
        with_defaults_lines = list(map(self._replace_defaults, no_spaces_lines))

        return with_defaults_lines

    @staticmethod
    def _process_key_word_block(
        block: list[str],
    ) -> dict[str, list[str]]:
        dates_info: list[str] = []
        compdata_info: list[str] = []
        compdatal_info: list[str] = []

        i: int = 0
        _dates = False
        _compdata: bool = False
        _compdatal: bool = False
        while True:
            if re.fullmatch("DATES", block[i]):
                _dates = True
                _compdata: bool = False
                _compdatal: bool = False
            elif re.fullmatch("COMPDAT", block[i]):
                _compdata = True
                _dates: bool = False
                _compdatal: bool = False
            elif re.fullmatch("COMPDATL", block[i]):
                _compdatal = True
                _dates: bool = False
                _compdata: bool = False

            if _dates:
                dates_info.append(block[i])
            elif _compdata:
                compdata_info.append(block[i])
            elif _compdatal:
                compdatal_info.append(block[i])

            i += 1

            if i >= len(block):
                break

        if "DATES" in dates_info:
            dates_info = list(
                filter(
                    lambda x: not re.fullmatch("DATES", x),
                    dates_info,
                )
            )

        if "COMPDAT" in compdata_info:
            compdata_info = list(
                filter(
                    lambda x: not re.fullmatch("COMPDAT", x),
                    compdata_info,
                )
            )

        if "COMPDATL" in compdatal_info:
            compdatal_info = list(
                filter(
                    lambda x: not re.fullmatch("COMPDATL", x),
                    compdatal_info,
                )
            )

        info_dict: dict[str, list[str]] = {
            "DATES": dates_info,
            "COMPDAT": compdata_info,
            "COMPDATL": compdatal_info,
        }

        return info_dict

    @classmethod
    def clear_comments(cls, eclipse_string: str) -> str:
        return cls._comment_pattern.sub(
            os.linesep,
            eclipse_string,
        )

    @classmethod
    def clear_blank_lines(cls, eclipse_string: str) -> str:
        return cls._blank_line_pattern.sub(
            os.linesep,
            eclipse_string,
        )

    @classmethod
    def clear_tabs(cls, eclipse_string: str) -> str:
        return cls._tab.sub(
            " ",
            eclipse_string,
        )

    @classmethod
    def filter_unexpected_blocks(cls, eclipse_string: str) -> str:
        _linesep: re.Pattern = re.compile("(\r\n*|\n)+$")

        unknown_blocks = (
            cls._blocks_to_parse.sub(
                "",
                eclipse_string,
            )
            .strip()
            .replace("END", "")  # фильтром удаляется END, нам надо его оставить
        )

        unknown_blocks = _linesep.sub("", unknown_blocks)

        return eclipse_string.replace(unknown_blocks, "")

    @staticmethod
    def _empty_string(any_str: str) -> bool:
        _pattern = re.compile(r"(\r\n*|\n|\s|/)\s*")
        if _pattern.fullmatch(any_str):
            return False
        else:
            return True

    @staticmethod
    def _clear_unnecessary_spaces(any_str: str) -> str:
        return re.sub(r"\s+", " ", any_str).strip().replace("'", "")

    @classmethod
    def _replace_defaults(cls, any_str: str) -> str:
        _ = re.sub(r"\d[*]", cls._replace_default, any_str)
        return re.sub(r"\s/$", "", _)

    @staticmethod
    def _replace_default(match: re.Match) -> str:
        vals_num_to_replace = match.group().replace("*", "")
        return " ".join([DEFAULT_VALUE for _ in range(int(vals_num_to_replace))])

    @staticmethod
    def _convert_to_float(any_str: str) -> Union[float, str]:
        try:
            return float(any_str)
        except ValueError:
            return any_str

    def append(self, info_dict: dict[str, list[str]]):
        date = info_dict["DATES"][-1] if info_dict["DATES"] else None
        _other_keys = list(info_dict.keys())
        _other_keys.remove("DATES")

        for key in _other_keys:
            if compdates := info_dict[key]:
                for compdata in compdates:
                    _compdata: list[str] = compdata.split()
                    i: int = 0
                    data: dict = {}

                    for column_name in COLUMN_NAMES:
                        if column_name == "Date":
                            data.update({column_name: date})
                        elif column_name == "Local grid name" and key == "COMPDATL":
                            data.update({column_name: _compdata[i]})
                            i += 1
                        else:
                            if column_name == "Local grid name" and key != "COMPDATL":
                                data.update({column_name: None})
                                continue

                            data.update(
                                {column_name: self._convert_to_float(_compdata[i])}
                            )
                            i += 1

                    self._frame = pd.concat(
                        [self._frame, pd.DataFrame(data, index=[len(self._frame)])]
                    )

    def save_to_csv(
        self,
        save_path: Union[str, Path, os.PathLike],
        **kwargs,
    ) -> None:
        self._frame.to_csv(
            path_or_buf=save_path,
            **kwargs,
        )
