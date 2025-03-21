import json

from loguru import logger


class JSONDecoder:

    @staticmethod
    def decode(text_data: bytes, encoding: str = "utf-8") -> dict | None:
        try:
            return json.loads(text_data.decode(encoding))
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            return None
