import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFrame
)
from PySide6.QtCore import QPropertyAnimation, QRect, QEasingCurve, QPoint, Qt


class FlyoutPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("background-color: #2c3e50; color: white; border-radius: 8px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        for text in ["Option 1", "Option 2", "Option 3"]:
            btn = QPushButton(text, self)
            btn.setStyleSheet("QPushButton { background-color: #34495e; border: none; padding: 4px 8px; }"
                              "QPushButton:hover { background-color: #3b5998; }")
            layout.addWidget(btn)

        self.resize(0, 100)  # start collapsed
        self.hide()

        # Animation setup
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(250)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def toggle(self, target_btn: QPushButton):
        """Show or hide next to the clicked button"""
        btn_pos: QPoint = target_btn.mapToGlobal(QPoint(0, 0))
        parent_pos: QPoint = self.parentWidget().mapFromGlobal(btn_pos)

        start_rect = QRect(parent_pos.x() + target_btn.width(),
                        parent_pos.y(),
                        0, self.height())

        end_rect = QRect(parent_pos.x() + target_btn.width(),
                        parent_pos.y(),
                        150, self.sizeHint().height())

        if self.isVisible() and self.width() > 0:
            # collapse
            self.animation.stop()
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(start_rect)

            # connect once, auto-disconnect after hiding
            self.animation.finished.connect(self.hide, type=Qt.SingleShotConnection)

        else:
            # expand
            self.show()
            self.animation.stop()
            self.animation.setStartValue(start_rect)
            self.animation.setEndValue(end_rect)

        self.animation.start()


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flyout Overlay Example")
        self.resize(400, 200)

        layout = QVBoxLayout(self)

        self.btn1 = QPushButton("Menu A")
        self.btn2 = QPushButton("Menu B")
        self.btn3 = QPushButton("Menu C")

        layout.addWidget(self.btn1)
        layout.addWidget(self.btn2)
        layout.addWidget(self.btn3)
        layout.addStretch()

        self.flyout = FlyoutPanel(self)

        self.btn1.clicked.connect(lambda: self.flyout.toggle(self.btn1))
        self.btn2.clicked.connect(lambda: self.flyout.toggle(self.btn2))
        self.btn3.clicked.connect(lambda: self.flyout.toggle(self.btn3))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec())
