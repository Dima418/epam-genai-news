class DataProvider:

    def __init__(self, data_parser):
        self._data_parser = data_parser

    def provide_data(self):
        yield from self._data_parser.parse()


class AsyncDataProvider:

        def __init__(self, data_parser):
            self._data_parser = data_parser

        async def provide_data(self):
            async for data in self._data_parser.parse():
                yield data
