from PySide6.QtWidgets import QMessageBox

from pages.mainwindow import Ui_MainWindow

STATUS_GOOD = 0
ERROR_NO_FILE_OPEN = 1
ERROR_MISSING_FNC_HEADER = 2
ERROR_MISSING_KEY_SECTION = 3
ERROR_INVALID_FUNCTION = 4
ERROR_MISSING_SEMICOLON = 5

ERROR_NO_SOLUTION_FOUND = 400
ERROR_TOO_MANY_OBJECTIVES = 401
ERROR_INVALID_WEIGHT_MINIMUM = 403
ERROR_INVALID_WEIGHT_INCREMENT = 404
ERROR_ONLY_ONE_OBJECTIVE = 405

errors = {
    STATUS_GOOD: {"title": None, "desc": None},
    ERROR_NO_FILE_OPEN: {
        "title": "No file is open.",
        "desc": "Make sure that you have a file open.",
    },
    ERROR_MISSING_FNC_HEADER: {
        "title": "Missing a header in the FNC file.",
        "desc": (
            "Make sure your FNC has at minimum the following sections:"
            " VARIABLE, OBJECTIVE, and FUNCTION."
        ),
    },
    ERROR_MISSING_KEY_SECTION: {
        "title": "Missing a key section in the FNC file.",
        "desc": (
            "Make sure your FNC has at minimum the following sections defined correctly:"
            " VARIABLE, OBJECTIVE, and FUNCTION."
        ),
    },
    ERROR_INVALID_FUNCTION: {
        "title": "Invalid function.",
        "desc": (
            "Probably missing an operator somewhere. Check the formatting"
            " documentation for help."
        ),
    },
    ERROR_MISSING_SEMICOLON: {
        "title": "Missing semicolon at end of a function.",
        "desc": (
            "Make sure that all functions and gradients have a semicolon (;) at"
            " the end."
        ),   
    },
    ERROR_NO_SOLUTION_FOUND: {
        "title": "No solution found.",
        "desc": "Double check the FNC file and possibly increase the grid size."
    },
    ERROR_TOO_MANY_OBJECTIVES: {
        "title": "Too many objective functions.",
        "desc": "Please make sure that your FNC file only has one objective function."
    },
    ERROR_INVALID_WEIGHT_MINIMUM: {
        "title": "Invalid weight minimum.",
        "desc": "Please enter a valid minimum weight."
    },
    ERROR_INVALID_WEIGHT_INCREMENT: {
        "title": "Invalid weight increment.",
        "desc": "Please enter a valid weight increment."
    },
    ERROR_ONLY_ONE_OBJECTIVE: {
        "title": "Invalid number of objective functions",
        "desc": "WSF requires more than one objective function"
    },
    0: {
        "title": None,
        "desc": None
    },
    0: {
        "title": None,
        "desc": None
    },
    0: {
        "title": None,
        "desc": None
    },
}


class ErrorHandler:
    def __init__(self, ui: Ui_MainWindow) -> None:
        self.ui = ui

    def handle(self, code: int) -> None:
        if code == 0 or code is None:
            return

        if code not in list(errors.keys()):
            self.__error_popup(code, f"Unknown Error", "An unknown error has occured.")
            return
        
        self.__error_popup(code, errors[code]["title"], errors[code]["desc"])
    
    def critical(self, code: int) -> None:
        if code == 0:
            return
        
        QMessageBox.critical(
            self.ui.centralwidget,
            errors[code]["title"],
            errors[code]["desc"],
            QMessageBox.Ok,
        )

    def __error_popup(
        self, code: int, error_title: str, error_message: str
    ) -> None:
        # Create a QMessageBox for the error
        error_popup = QMessageBox()
        error_popup.setIcon(QMessageBox.Critical)
        error_popup.setWindowTitle(f"Error: Code { code }")
        error_popup.setText(error_title)
        error_popup.setInformativeText(error_message)
        error_popup.setStandardButtons(QMessageBox.Ok)
        error_popup.exec()
    
    def gen_error(self, message: str):
        error_popup = QMessageBox()
        error_popup.setIcon(QMessageBox.Critical)
        error_popup.setWindowTitle(f"Error")
        error_popup.setText("An error has occured.")
        error_popup.setInformativeText(message)
        error_popup.setStandardButtons(QMessageBox.Ok)
        error_popup.exec()
