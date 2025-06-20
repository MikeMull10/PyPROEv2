from decimal import Decimal
from typing import Optional

from PySide6.QtCore import QModelIndex, QObject, Qt
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QItemDelegate, QLabel, QLineEdit, QMessageBox, QCheckBox

from pages.designexp import DOE

# adapted from user @chart328 in https://stackoverflow.com/questions/26614678/validating-user-input-in-a-qtableview
# many thanks!


class TableDelegate(QItemDelegate):
    """A custom subclass of QItemDelegate for validating input in a QTableView"""

    def __init__(self, parent: Optional[QObject], doe: DOE):
        """
        Parameters
        ----------
        parent : Optional[QObject]
            An optional parent object
        doe : DOE
            A Design of Experiments object
        """
        super().__init__(parent)
        self.item_model = parent
        self.doe = doe

    def createEditor(self, parent: Optional[QObject], options, index):
        """Create a custom editor object with QLineEdit and a QDoubleValidator"""

        editor = QLineEdit(parent)
        editor.setValidator(QDoubleValidator(-100000.0, 100000.0, 50))
        return editor

    def setEditorData(self, editor, index):
        """Update the line editor's data and the associated DOE matrix_funcs matrix value"""
        value = str(index.data())

        if index.column() < self.doe.num_vars * 2:
            bounds = [
                Decimal(self.doe.var_bounds[index.column() - self.doe.num_vars][0]),
                Decimal(self.doe.var_bounds[index.column() - self.doe.num_vars][1]),
            ]

            half = Decimal("0.5")
            target = Decimal(value)

            # reverse engineer the absolute value
            if self.doe.var_bounds[index.column() - self.doe.num_vars] == [0,0]:
                abs_val = self.doe.fifteenth_place_truncation(target)
            else:
                abs_val = self.doe.fifteenth_place_truncation((target - (half*(bounds[0] + bounds[1]))) /(half*(bounds[1] - bounds[0])))
            model = self.doe.ui.doeTable.model()

            editor.setText(value)
            # update the actual matrix of variables for DOE
            self.doe.matrix_vars[index.row()][
                index.column() - self.doe.num_vars
            ] = float(Decimal(abs_val))

            # reevaluate the function values with the new variable values
            # update both the underlying model AND the displayed data
            new_func_values = self.doe.evaluate_func_defs(index.row())
            [
                model.setData(
                    index.siblingAtColumn(i + (self.doe.num_vars * 2)),
                    new_func_values[i]
                )
                for i in range(len(new_func_values))
            ]
            model.setData(
                index.siblingAtColumn(index.column() - self.doe.num_vars),
                float(Decimal(abs_val)),
            )
        else:
            self.doe.matrix_funcs[
                index.row()
            ][index.column() - (self.doe.num_vars * 2)] = float(Decimal(value))

    def setModelData(self, editor, model, index):
        """Set the model data"""

        value = editor.text()

        if index.column() < self.doe.num_vars * 2:
            bounds = [
                Decimal(self.doe.var_bounds[index.column() - self.doe.num_vars][0]),
                Decimal(self.doe.var_bounds[index.column() - self.doe.num_vars][1]),
            ]

            half = Decimal("0.5")
            target = Decimal(value)


            # reverse engineer the absolute value
            
            abs_val = self.doe.fifteenth_place_truncation((target - (half*(bounds[0] + bounds[1]))) /(max(1, half*(bounds[1] - bounds[0]))))
            model = self.doe.ui.doeTable.model()

            msg = QMessageBox(self.doe.ui.centralwidget)
            
            msg.setText("Out of Bounds Variable Value")
            msg.setInformativeText("Are you sure you want to enter a value outside of the predefined variable range?")
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            check = QCheckBox("Do not ask again")
            check.clicked.connect(self.updateDOEBounds)

            msg.setCheckBox(check)

            if ((abs_val >= -1 and abs_val <= 1) or self.doe.ui.settings.value("DOEBoundsWarning") == "False" or (msg.exec() == QMessageBox.Ok)):
                model.setData(index, editor.text(), Qt.EditRole)
        else:
            model.setData(index, editor.text(), Qt.EditRole)

    def updateDOEBounds(self, value):
        self.doe.ui.settings.setValue("DOEBoundsWarning", "False" if value else "True")

    def updateEditorGeometry(self, editor, option, index):
        """Set the editor geometry"""
        editor.setGeometry(option.rect)
