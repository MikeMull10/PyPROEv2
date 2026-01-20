from PySide6.QtWidgets import QVBoxLayout, QWidget
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import Qt, QSize

from qfluentwidgets import MessageBoxBase , SubtitleLabel

from PySide6.QtWidgets import QTableWidgetItem, QAbstractItemView, QApplication, QWidget
from PySide6.QtGui import QKeySequence, QColor

from qfluentwidgets import TableWidget, themeColor, theme, Theme


class Table(TableWidget):
    def __init__(self, parent=None, data=None):
        super().__init__(None)
        self.parent = parent

        if data is not None:
            self.populate(data)

        self.setBorderVisible(True)
        self.setBorderRadius(8)
        self.setWordWrap(False)

        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        self.horizontalHeader().setStyleSheet("QHeaderView::section { border: none; }")
        self.verticalHeader().setStyleSheet("QHeaderView::section { border: none; }")
        self.setCornerButtonEnabled(False)
        
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def populate(self, data: list):
        if len(data) == 0:
            return
        
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        
        self.setRowCount(len(data))
        self.setColumnCount(len(data[0]))

        for i, row in enumerate(data):
            for j, val in enumerate(row):
                item = QTableWidgetItem(val)
                self.setItem(i, j, item)

        self.fix_corner()
        
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self.resizeToContents()

    def fix_corner(self):
        for child in self.findChildren(QWidget):
            if child.metaObject().className() == "QTableCornerButton":
                child.setStyleSheet("QTableCornerButton::section {border: none;}")
                return

    def on_selection_changed(self):
        normal_color = QColor(255, 255, 255) if theme() == Theme.DARK else QColor(0, 0, 0)
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                item = self.item(i, j)
                if item:
                    item.setForeground(normal_color)

        for sel_range in self.selectedRanges():
            for row in range(sel_range.topRow(), sel_range.bottomRow() + 1):
                for col in range(sel_range.leftColumn(), sel_range.rightColumn() + 1):
                    item = self.item(row, col)
                    if item:
                        item.setForeground(themeColor())

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Copy):
            self.copySelection()
            return
        if event.matches(QKeySequence.Paste):
            # self.pasteSelection()
            return
        super().keyPressEvent(event)

    def copySelection(self):
        ranges = self.selectedRanges()
        if not ranges:
            return
        r = ranges[0]
        text = ""
        for row in range(r.topRow(), r.bottomRow() + 1):
            row_data = []
            for col in range(max(r.leftColumn(), 1), r.rightColumn() + 1):
                item = self.item(row, col)
                row_data.append(item.text() if item else "")
            text += "\t".join(row_data) + "\n"
        QApplication.clipboard().setText(text)

    def pasteSelection(self):
        clipboard = QApplication.clipboard().text()
        if not clipboard:
            return

        startRow = self.currentRow()
        startCol = max(self.currentColumn(), 1)

        if startRow < 0:
            return

        rows = clipboard.splitlines()

        for i, rowText in enumerate(rows):
            cols = rowText.split("\t")
            for j, val in enumerate(cols):
                r = startRow + i
                c = startCol + j

                if r >= self.rowCount() or c >= self.columnCount():
                    continue

                item = self.item(r, c)
                if item is None:
                    item = QTableWidgetItem()
                    self.setItem(r, c, item)

                item.setText(val)

    def clear(self):
        super().clear()
        self.setRowCount(0)
        self.setColumnCount(0)

    def resizeToContents(self):
        width = self.verticalHeader().width()  # row numbers
        for col in range(self.columnCount()):
            width += self.columnWidth(col)

        height = self.horizontalHeader().height()
        for row in range(self.rowCount()):
            height += self.rowHeight(row)

        self.setMinimumSize(width + 2, height + 2)
        self.setMaximumSize(width + 2, height + 2)



class StatsPopup(MessageBoxBase):
    def __init__(self, function_name: str, parent=None, data: dict=None):
        """
        parent needs to be the main window
        """
        super().__init__(parent)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(15)

        layout.addWidget(SubtitleLabel(f"Statistics for {function_name}"))

        self.table = Table(self, data=[[key, str(data[key])] for key in data])
        layout.addWidget(self.table)

        # base_size: QSize = parent.size()
        # base_x, base_y = map(int, [0.3 * base_size.width(), 0.3 * base_size.height()])
        # self.table.setMinimumSize(base_x, base_y)

        self.viewLayout.addWidget(container)

        self.yesButton.setCursor(Qt.PointingHandCursor)
        self.cancelButton.setCursor(Qt.PointingHandCursor)

        QShortcut(QKeySequence("Ctrl+Return"), self, activated=self.yesButton.click)
        QShortcut(QKeySequence("Ctrl+Enter"), self, activated=self.yesButton.click)
    