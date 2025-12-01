from pages.mainwindow import Ui_MainWindow
from handlers.filereader import TextFileReader
from handlers.filewriter import TextFileWriter


class Writer:
    """A class with all the methods for the writer page"""

    def __init__(self, ui: "Ui_MainWindow", handle_error: None):
        """Initialize with an instance of the ui"""
        self.WRT_OK = 1
        self.WRT_ERROR = -1
        self.text_panel = ui.wrtEdit
        self.text_reader = None
        self.text_writer = None
        self.ui = ui
        self.handle_error = handle_error

    def read_text_file(self, filename: str) -> int:
        """Read the given text file"""
        if filename == None:
            return -1
        else:
            var2 = None
            self.text_reader = TextFileReader(filename, "", self.handle_error)
            self.text_reader.set_skip_blank_line(False)
            self.text_reader.set_skip_comment_line(False)

            var2 = self.text_reader.read_line()
            while var2 != None:
                self.text_panel.append(var2)

            self.text_reader.close()
            return 1

    def write_text_file(self, filename: str) -> int:
        """Write to the given filename"""
        if filename == None:
            return -1
        else:
            var2 = None
            self.text_writer = TextFileWriter(filename, self.handle_error)
            var2 = self.text_panel.document()

            if not var2.isEmpty():
                self.text_writer.write_line(var2)
                self.text_writer.close()
                return 1
            else:
                return -1

    def close_text_file(self, filename: str) -> int:
        """Closes the text file"""
        if self.write_text_file(filename) == 1:
            self.text_writer.close()
            return 1
        else:
            return -1
