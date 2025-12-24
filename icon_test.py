import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt
from qfluentwidgets import FluentIcon, IconWidget, SubtitleLabel


class FluentIconBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fluent Icon Browser")
        self.resize(900, 700)

        main_layout = QVBoxLayout(self)

        title = SubtitleLabel("QFluentWidgets – Fluent Icons")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)

        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(16)
        scroll.setWidget(container)

        icons = list(FluentIcon)
        columns = 6

        for i, icon in enumerate(icons):
            row = i // columns
            col = i % columns

            icon_widget = IconWidget(icon)
            icon_widget.setFixedSize(32, 32)

            label = QLabel(icon.name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)

            cell = QVBoxLayout()
            cell.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cell.addWidget(icon_widget)
            cell.addWidget(label)

            cell_widget = QWidget()
            cell_widget.setLayout(cell)

            grid.addWidget(cell_widget, row, col)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FluentIconBrowser()
    window.show()
    sys.exit(app.exec())
