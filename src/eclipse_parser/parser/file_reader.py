import os
import re
from pathlib import Path
from typing import Callable, Generator, Optional, TextIO, Union

from eclipse_parser.common.chunks_reader import chunks_reader
from eclipse_parser.common.defaults import KEY_WORDS_TO_PARSE


class EclipseParser:

    _comment_pattern: re.Pattern = re.compile(r"--.*\n")

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
            raise TypeError

        if os.path.getsize(self._file_path) == 0:
            raise ValueError

        self._read_file = read_method
        self._file_encoding = file_encoding
        self._chunks_size = read_chunks

    @property
    def file_path(self) -> Path:
        return self._file_path

    @property
    def encoding(self) -> str:
        return self._file_encoding

    def parse_file(
        self,
    ):
        data: str

        with open(
            file=self._file_path,
            mode="r",
            encoding=self._file_encoding,
        ) as file:

            for data in self._read_file(file, self._chunks_size):
                no_comments = self._comment_pattern.sub(os.linesep, data)
                no_blank_lines = re.sub(r"\n\s*\n", "\n", no_comments)

                _str = r"({0})(\n|.)*/\n".format(
                    "|".join([_ for _ in KEY_WORDS_TO_PARSE])
                )
                _pattern = re.compile(_str)

                print(_pattern)

                block_match = _pattern.findall(no_blank_lines)
                print(block_match)
                # if len(block_match) < 1:
                #     print(f"no matches")
                #
                # for block in block_match:
                #     print(block)

    def parse_to_csv(
        self,
        *args,
        **kwargs,
    ) -> ...:
        ...
