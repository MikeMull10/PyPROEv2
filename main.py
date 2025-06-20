import os
import sys
import logging
import multiprocessing

from PySide6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PySide6.QtGui import QPixmap

from pages.ui import Interface
from handlers.stylesheet import load_stylesheet, resource_path

from pathlib import Path


if __name__ == "__main__":

    # Override the default exception handler if this is an application and not in development
    if hasattr(sys, '_MEIPASS'):
        # Get the user's home directory
        log_dir = Path(os.path.expanduser("~"))
        log_file = log_dir / "pyproe.log"

        # Ensure the directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)

        # Set up the logging configuration
        logging.basicConfig(
            filename=log_file,      # Log file path
            filemode="a",           # Append mode
            level=logging.ERROR,    # Log level (change to DEBUG/INFO if needed)
            format="%(asctime)s - %(levelname)s - %(message)s",
        )

        # Custom exception hook to log uncaught exceptions
        def exception_hook(exctype, value, traceback):
            logging.error("Uncaught exception", exc_info=(exctype, value, traceback))

            QMessageBox.critical(
                None,
                "Error: check log for additional details",
                str(value),
                QMessageBox.Ok,
            )
        
        sys.excepthook = exception_hook
    
    multiprocessing.freeze_support()  # Add this line for Windows + PyInstaller
    multiprocessing.set_start_method('spawn')  # Explicitly set start method

    # initializee a QApplication
    app = QApplication([])

    # Create the splash screen
    splash_pix = QPixmap(resource_path("assets/pyproe-logo.png"))  # Replace with your image path
    splash = QSplashScreen(splash_pix)
    splash.show()

    # set the stylesheet
    # app.setStyleSheet(load_stylesheet())

    # initialize the interface widget
    widget = Interface()

    # connect with a setting-saving function upon app close
    app.aboutToQuit.connect(widget.about_to_close)

    # show the app
    widget.show()
    splash.finish(widget)

    # gracefully quit the app
    sys.exit(app.exec())
