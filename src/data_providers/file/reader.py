class FileReader:
    def __init__(self, file_path, total_file_size=None, chunk_size=1024):
        self.file_path = file_path
        self.total_file_size = total_file_size
        self.chunk_size = chunk_size

    def read(self):
        with open(self.file_path, "rb") as f:
            while chunk := f.read(self.chunk_size):
                yield chunk
