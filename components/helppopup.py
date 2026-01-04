from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import QUrl, QSize, Qt

from qfluentwidgets import LineEdit, MessageBoxBase, TextBrowser, PrimaryPushButton, FluentIcon as FI


class DocumentationPopup(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        content = QWidget()
        contentLayout = QVBoxLayout(content)

        search_layout = QHBoxLayout()
        self.search_box = LineEdit()
        self.search_btn = PrimaryPushButton("Search")
        self.search_btn.clicked.connect(self.do_search)

        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.search_btn)
        contentLayout.addLayout(search_layout)

        self.browser = TextBrowser()
        self.browser.setSource(QUrl.fromLocalFile("html/help.html"))
        contentLayout.addWidget(self.browser)

        self.viewLayout.addWidget(content)

        base_size: QSize = parent.size()
        base_x, base_y = map(int, [0.9 * base_size.width(), 0.8 * base_size.height()])
        content.setFixedWidth(base_x)
        content.setFixedHeight(base_y)

        self.yesButton.setText("Close")
        self.yesButton.setCursor(Qt.PointingHandCursor)
        self.cancelButton.setCursor(Qt.PointingHandCursor)
        self.cancelButton.hide()

    def do_search(self):
        text = self.search_box.text()
        self.browser.find(text)
