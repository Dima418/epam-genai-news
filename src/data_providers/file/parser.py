from loguru import logger

from src.data_providers.file.decoder import JSONDecoder
from src.data_providers.file.reader import FileReader


class FileParser:
    def __init__(self, file_reader: FileReader, decoder: JSONDecoder | None = None):
        self._file_reader = file_reader
        self._decoder = decoder
        logger.info(f"FileParser initialized with {type(file_reader)} file reader and {type(decoder)} decoder.")

    def parse(self):
        buffer = b""
        for chunk in self._file_reader.read():
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)

                if self._decoder:
                    yield self._decoder.decode(line)
                else:
                    yield line.decode("utf-8")
