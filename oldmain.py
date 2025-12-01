import os
import sys
import logging
import multiprocessing

from PySide6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PySide6.QtGui import QPixmap

from sections.ui import MainWindow
from handlers.stylesheet import load_stylesheet, resource_path

from pathlib import Path
import qdarktheme


if __name__ == "__main__":
    multiprocessing.freeze_support()  # Add this line for Windows + PyInstaller
    multiprocessing.set_start_method('spawn')  # Explicitly set start method

    # initializee a QApplication
    app = QApplication([])
    # app.setStyle("Fusion")
    app.setStyleSheet(qdarktheme.load_stylesheet())

    # Create the splash screen
    splash_pix = QPixmap(resource_path("assets/pyproe-logo.png"))  # Replace with your image path
    splash = QSplashScreen(splash_pix)
    splash.show()

    # set the stylesheet
    # app.setStyleSheet(load_stylesheet())

    # initialize the interface widget
    widget = MainWindow()

    # connect with a setting-saving function upon app close
    # app.aboutToQuit.connect(widget.about_to_close)

    # show the app
    widget.show()
    splash.finish(widget)

    # gracefully quit the app
    sys.exit(app.exec())
