from handlers.errorhandler import ErrorHandler

class TextFileReader:
    """Manage basic file reading operations in the context of the PyGoose app"""

    def __init__(
        self, file_name: str, comment_chars: str = "", handle_error: ErrorHandler=None
    ):
        self.text_file_name = file_name
        self.comment_chars = comment_chars
        self.skip_blank_line = False
        self.skip_comment_line = False
        self.current_line = 0
        self.handle_error = handle_error

        try:
            self.filestream = open(self.text_file_name, "r")
            self.file_open = True
        except:
            self.filestream = None
            self.file_open = False
            self.handle_error.gen_error(f"I/O Error opening <{self.text_file_name}>")

    def close(self) -> None:
        """Close the file and flush the file buffer"""
        self.file_open = False
        self.current_line = 0

        try:
            self.filestream.close()
        except:
            self.handle_error.gen_error(f"I/O Error closing <{self.text_file_name}>")

    def set_comment_chars(self, chars: str) -> None:
        """Configure the comment characters

        Parameters
        ----------
        chars : string
            A string with all the characters that indicate the start of a comment line
        """
        self.comment_chars = chars

    def set_skip_blank_line(self, skip: bool) -> None:
        """Configure whether blank lines should be skipped

        Parameters
        ----------
        skip : boolean
            Whether or not blank lines should be skipped over as the input file is read
        """
        self.skip_blank_line = skip

    def set_skip_comment_line(self, skip: bool) -> None:
        """Configure whether comment lines should be skipped over

        Parameters
        ----------
        skip : boolean
            Whether or not comment lines should be skipped over as the input file is read
        """
        self.skip_comment_line = skip

    def get_current_line_number(self) -> int:
        """Returns the current line number in the file reading process"""
        return self.current_line

    def read_line(self) -> str:
        """Read the next line from the input file"""
        try:
            var1 = -1

            while (
                var1 == -1
                or (self.skip_blank_line and self.is_blank_line(var1))
                or (self.skip_comment_line and self.is_comment_line(var1))
            ):
                var1 = self.filestream.readline()
                self.current_line += 1
            return var1
        except:
            self.handle_error.gen_error(
                f"I/O Error reading from <{self.text_file_name}>.\nLine #:"
                f" {self.current_line}"
            )
            return None

    def is_file_open(self) -> bool:
        """whether or not the file is being read"""
        return self.file_open

    def is_comment_line(self, var1: str) -> bool:
        """Evaluate whether a line is a comment"""
        return var1 != None and len(var1) > 0 and var1[0] in self.comment_chars

    def is_blank_line(self, var1: str) -> bool:
        """Evaluate whether a line is blank"""
        return var1 == "\n"
