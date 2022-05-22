from typing import Generator, Optional, TextIO


def chunks_reader(
    file_obj: TextIO,
    chunk_size: Optional[int] = None,
) -> Generator[str, None, None]:
    """Функция для чтения большого файла по частям."""
    while True:
        data_chunk = file_obj.read(chunk_size)

        if not data_chunk:
            break

        yield data_chunk
