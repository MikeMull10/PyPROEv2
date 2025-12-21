from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from sections.app import App

if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon("assets/logo.png"))
    window = App()
    window.show()
    app.exec()