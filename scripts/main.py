import os
from datetime import datetime
from pprint import pprint
from time import perf_counter

from dotenv import find_dotenv, load_dotenv

from eclipse_parser.common import DATA_DIR, RESULTS_DIR
from eclipse_parser.parser import EclipseParser

load_dotenv(
    dotenv_path=find_dotenv(
        ".env.file",
    ),
    verbose=True,
)


def main(
    show_info: bool = False,
    print_df: bool = False,
):
    _file_name = os.environ.get("file_name")

    parser = EclipseParser(
        file_path=DATA_DIR.joinpath(_file_name),
    )

    start = perf_counter()
    parser.parse_file()
    end = perf_counter()

    if print_df:
        pprint(parser.frame)

    if show_info:
        pprint(f"Затраченное время: time = {end - start: .2f} s")
        pprint(
            f'Имя файла c результатами: {datetime.now().strftime("%Y_%m_%d_parsing_result.csv")}'
        )

    parser.save_to_csv(
        save_path=RESULTS_DIR.joinpath(
            datetime.now().strftime("%Y_%m_%d_parsing_result.csv")
        ),
        index=False,
    )


if __name__ == "__main__":
    main(
        show_info=True,
    )
