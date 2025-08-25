import sys
import os

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller bundled executables. """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller stores files in a temporary folder (_MEIPASS) during execution
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
