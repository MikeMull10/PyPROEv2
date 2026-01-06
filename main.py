from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from sections.app import App
from fixpath import app_root

if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon((app_root() / "assets" / "logo.png").as_posix()))
    window = App()
    window.show()
    app.exec()
