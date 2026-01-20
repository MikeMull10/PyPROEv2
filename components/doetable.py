from PySide6.QtWidgets import QTableWidgetItem, QAbstractItemView, QApplication, QWidget, QHBoxLayout
from PySide6.QtGui import QKeySequence, QColor

from components.basicpopup import BasicPopup
from components.fnc_objects import Variable, Function

from qfluentwidgets import TableWidget, themeColor, theme, Theme, ToolButton, FluentIcon as FI
import numpy as np


class DOETable(TableWidget):
    def __init__(self, parent=None):
        super().__init__(None)
        self.parent = parent

        self.setBorderVisible(True)
        self.setBorderRadius(8)
        self.setWordWrap(False)

        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        self.horizontalHeader().setStyleSheet("QHeaderView::section { border: none; }")
        self.verticalHeader().setStyleSheet("QHeaderView::section { border: none; }")
        self.setCornerButtonEnabled(False)
        
        self.selectionModel().selectionChanged.connect(self.on_selection_changed)

        self.variables: list[Variable] = []
        self.functions: list[Function] = []
        self.headers:   list[str]      = []

    def populate(self, data: list, headers: list=None):
        if len(data) == 0:
            return
        
        self.setRowCount(len(data))
        self.setColumnCount(len(data[0]) + 1)

        for i, row in enumerate(data):
            for j, val in enumerate(row):
                item = QTableWidgetItem(val)
                self.setItem(i, j + 1, item)
        
        for row in range(self.rowCount()):
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(4)

            del_btn  = ToolButton(FI.DELETE)
            calc_btn = ToolButton(FI.SYNC)
            del_btn.setFixedSize(25, 25)
            calc_btn.setFixedSize(25, 25)
            del_btn.setToolTip("Delete Row")
            calc_btn.setToolTip("Recalculate Function Value(s)")
            del_btn.clicked.connect(self.delete_row_from_button)
            calc_btn.clicked.connect(self.recalculate_from_button)

            layout.addWidget(del_btn)
            layout.addWidget(calc_btn)

            self.setCellWidget(row, 0, container)

        if headers:
            self.setHorizontalHeaderLabels([""] + headers)
            self.headers = headers

        self.fix_corner()
        self.resizeColumnsToContents()
        self.setColumnWidth(0, 70)

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
            self.pasteSelection()
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
        self.variables.clear()
        self.functions.clear()
        self.headers.clear()
    
    def delete_row_from_button(self):
        btn = self.sender()
        if not btn:
            return

        container = btn.parent()
        index = self.indexAt(container.pos())

        if index.isValid():
            self.removeRow(index.row())
        
    def recalculate_from_button(self):
        btn = self.sender()
        if not btn:
            return
        
        container = btn.parent()
        index = self.indexAt(container.pos())

        if index.isValid():
            self.recaculate(index.row())
    
    def recaculate(self, index: int):
        x = []
        end = len(self.variables) + 1
        for i in range(1, end):
            try:
                x.append(float(self.item(index, i).text()))
            except ValueError:
               pop = BasicPopup(parent=self.parent, title="ERROR", message=f"Error converting a variable to a float at ROW: {index}, COL: {i} with VALUE: {self.item(index, i).text()}.")
               pop.exec()
               return
        
        for i, func in enumerate(self.functions):
            cell = self.item(index, end + i)
            cell.setText(str(func(x)))
    
    def add_point(self) -> None:
        if self.columnCount() == 0 or self.rowCount() == 0:
            return

        row = self.rowCount()
        self.insertRow(row)

        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        del_btn  = ToolButton(FI.DELETE)
        calc_btn = ToolButton(FI.SYNC)
        del_btn.setFixedSize(25, 25)
        calc_btn.setFixedSize(25, 25)
        del_btn.setToolTip("Delete Row")
        calc_btn.setToolTip("Recalculate Function Value(s)")
        del_btn.clicked.connect(self.delete_row_from_button)
        calc_btn.clicked.connect(self.recalculate_from_button)

        layout.addWidget(del_btn)
        layout.addWidget(calc_btn)

        self.setCellWidget(row, 0, container)

        end = len(self.variables) + 1
        for i in range(1, end):
            item = QTableWidgetItem("0.0")
            self.setItem(row, i, item)

        values = [0.0 for _ in self.variables]
        for i, func in enumerate(self.functions):
            result = func(values)
            item = QTableWidgetItem(str(result))
            self.setItem(row, end + i, item)
    
    def get_row_data(self, row: int) -> list[str]:
        values = []
        for col in range(1, self.columnCount()):
            item = self.item(row, col)
            values.append(item.text() if item else None)
        return values
    
    def get_save_data(self) -> str:
        ret  = "*TABLE:\n\n"
        ret += ';'.join(self.headers) + '\n'

        for i in range(self.rowCount()):
            ret += ';'.join([str(i + 1)] + self.get_row_data(i)) + '\n'

        ret += f"\n*VARIABLE: {len(self.variables)}\n\n"
        for var in self.variables:
            ret += f"{var}\n"

        ret += f"\n*FUNCTION: {len(self.functions)}\n\n"
        for fun in self.functions:
            ret += f"{fun};\n"
        
        return ret
    
    def get(self, start, stop) -> np.ndarray:
        if self.rowCount() <= 1 or self.columnCount() <= 1:
            return []

        data = []
        for i in range(self.rowCount()):
            row = []
            for ii in range(start, stop):
                try:
                    row.append(float(self.item(i, ii).text()))
                except ValueError:
                    pop = BasicPopup(parent=self.parent, title="ERROR", message=f"Error converting a variable to a float at ROW: {i}, COL: {i} with VALUE: {self.item(i, ii).text()}.")
                    pop.exec()
                    return
                
            data.append(row)

        return np.array(data)

    def get_independent(self) -> np.ndarray:
        return self.get(1, len(self.variables) + 1)

    def get_dependent(self) -> np.ndarray:
        return self.get(len(self.variables) + 1, self.columnCount())
