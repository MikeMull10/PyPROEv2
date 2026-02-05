from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from sections.app import App
from fixpath import app_root
import multiprocessing

if __name__ == "__main__":
    multiprocessing.freeze_support()
    multiprocessing.set_start_method('spawn')

    app = QApplication([])
    app.setWindowIcon(QIcon((app_root() / "assets" / "logo.png").as_posix()))
    window = App()
    window.show()
    app.exec()
