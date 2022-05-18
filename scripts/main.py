import os

from dotenv import find_dotenv, load_dotenv

from eclipse_parser.common import DATA_DIR
from eclipse_parser.parser import EclipseParser

load_dotenv(
    dotenv_path=find_dotenv(
        ".env.file",
    ),
    verbose=True,
)


def main():
    _file_name = os.environ.get("file_name")

    temp_file = DATA_DIR.joinpath(_file_name)

    EclipseParser(
        file_path=temp_file,
    ).parse_file()


if __name__ == "__main__":
    main()
