class TextFileWriter:
    """Manage basic file writing operations in the context of the PyGoose app"""

    def __init__(self, filename: str, handle_error):
        self.text_file_name = filename
        self.handle_error = handle_error

        try:
            self.filestream = open(self.text_file_name)
            self.file_open = True
        except:
            self.file_open = False
            self.handle_error(f"I/O Error opening <{self.text_file_name}>")

    def close(self) -> None:
        """Close the file and flush the file buffer"""
        self.file_open = False

        try:
            self.filestream.flush()
            self.filestream.close()
        except:
            self.handle_error(f"I/O error writing to <{self.text_file_name}>")

    def write_line(self, line: str) -> int:
        """Write a line to the open file buffer

        Parameters
        ----------
        line : string
            The line to write to the file
        """
        try:
            self.filestream.write(line)
            self.filestream.flush()
            return 1
        except:
            self.handle_error(f"I/O Error reading from <{self.text_file_name}>")
            return 0

    def write_newline(self, line: str) -> int:
        """Write a line and a newline character to the open file buffer

        Parameters
        ----------
        line : string
            The line to write to the file
        """
        return self.write_line(line + "\n")

    def is_file_open(self) -> bool:
        return self.file_open
