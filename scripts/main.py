import os
from datetime import datetime
from time import perf_counter

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

    parser = EclipseParser(
        file_path=DATA_DIR.joinpath(_file_name),
    )

    start = perf_counter()
    parser.parse_file()
    end = perf_counter()

    print(f"time = {end - start: .2f} s")
    print(datetime.now().strftime("%Y_%m_%d_parsing_result.csv"))

    # parser.save_to_csv(
    #     save_path=RESULTS_DIR.joinpath(
    #         datetime.now().strftime("%Y_%m_%d_parsing_result.csv")
    #     ),
    # )


if __name__ == "__main__":
    main()
