from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QScrollArea, QSizePolicy,
    QDialog, QDialogButtonBox, QPlainTextEdit
)
from PySide6.QtCore import Qt, QSize, QTimer, Signal
from PySide6.QtGui import QFontMetrics
import sys

class AutoWidthLineEdit(QLineEdit):
    def __init__(self, text='', parent=None):
        super().__init__(text, parent)
        self.setObjectName("AutoWidthLineEdit")

        self.setAlignment(Qt.AlignCenter)
        self.old_text = text
        
        # Track size changes
        self.textChanged.connect(self.update_width)

        # Allow expansion if needed
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self.setStyleSheet("""
            QLineEdit {
                padding: 4px;
                border-radius: 4px;
            }
        """)

        # Initial size
        QTimer.singleShot(0, self.update_width)

    def update_width(self):
        fm = QFontMetrics(self.font())
        width = fm.horizontalAdvance(self.text() or " ") + 30  # add some padding
        self.setFixedWidth(min(width, 2000))

class InlineRow(QWidget):
    def __init__(self, elements: list, parent_section=None):
        super().__init__()
        self.parent_section = parent_section
        self.elements = elements
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Add actual input widgets
        for elem in self.elements:
            layout.addWidget(elem)

        layout.addStretch()

        # Control buttons
        self.delete_button = QPushButton("⤫")
        self.up_button = QPushButton("\u21be")
        self.down_button = QPushButton("\u21c3")

        for i, btn in enumerate([self.down_button, self.up_button, self.delete_button]):
            btn.setFixedSize(24, 24)
            btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(0, 0, 0, .22);
                border-radius: 5px;
            }}
            """) #padding-{'top' if i != 2 else 'bottom'}: 4px;
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn)

        self.setLayout(layout)

        # Connect actions
        self.delete_button.clicked.connect(self.delete_self)
        self.up_button.clicked.connect(self.move_up)
        self.down_button.clicked.connect(self.move_down)

    def delete_self(self):
        if self.parent_section:
            self.parent_section.remove_row(self)

    def move_up(self):
        if self.parent_section:
            self.parent_section.move_row_up(self)

    def move_down(self):
        if self.parent_section:
            self.parent_section.move_row_down(self)
    
    def get_data(self):
        result = []
        for w in self.elements:
            if isinstance(w, QLineEdit):
                result.append(w.text())
            # elif isinstance(w, QLabel):
            #     result.append(w.text())
            elif isinstance(w, QComboBox):
                result.append(w.currentText())
            elif isinstance(w, ToggleIneqButton):
                result.append('lt' if w.text() == '\u2264' else 'gt')
            elif isinstance(w, EquationButton):
                result.append(w.equation_text)
            elif isinstance(w, FunctionDropdown):
                result.append(w.currentText())
        
        return result

class ToggleIneqButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("\u2264", parent)
        self.setFixedWidth(40)
        self.clicked.connect(self.toggle_operator)
        self.setStyleSheet("QPushButton {padding-top: 6px;}")
        self.setCursor(Qt.PointingHandCursor)

    def toggle_operator(self):
        self.setText("\u2265" if self.text() == "\u2264" else "\u2264")

    def get_operator(self):
        return self.text()
    
class Section(QWidget):
    def __init__(self, title: str, row_generator, on_change_callback=None):
        super().__init__()
        self.row_generator = row_generator
        self.on_change_callback = on_change_callback
        self.rows: list[InlineRow] = []

        self.layout: QVBoxLayout = QVBoxLayout()
        header: QHBoxLayout = QHBoxLayout()

        self.label = QLabel(f"{title.upper()}: 0")
        self.add_button = QPushButton("+")
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.setStyleSheet("""
            QPushButton {
                padding: 4px 10px;
                background: rgba(0, 0, 0, .22);
                border-radius: 5px;
            }
        """)
        self.add_button.clicked.connect(self.add_row)

        header.addWidget(self.label)
        header.addStretch()
        header.addWidget(self.add_button)

        self.layout.addLayout(header)
        self.setLayout(self.layout)

    def add_row(self, values=None):
        row = self.row_generator(len(self.rows))
        inline = InlineRow(row, parent_section=self)
        self.rows.append(inline)
        self.layout.addWidget(inline)
        self.update_label()

        if values:
            for widget, value in zip(inline.findChildren(QLineEdit), values):
                widget.setText(str(value))

        if self.on_change_callback:
            self.on_change_callback()

    def remove_row(self, row_widget: QWidget):
        self.rows.remove(row_widget)
        row_widget.setParent(None)
        row_widget.deleteLater()
        self.update_label()
        if self.on_change_callback:
            self.on_change_callback()

    def move_row_up(self, row_widget):
        idx = self.rows.index(row_widget)
        if idx > 0:
            self.rows[idx], self.rows[idx - 1] = self.rows[idx - 1], self.rows[idx]
            self.rebuild_rows()

    def move_row_down(self, row_widget):
        idx = self.rows.index(row_widget)
        if idx < len(self.rows) - 1:
            self.rows[idx], self.rows[idx + 1] = self.rows[idx + 1], self.rows[idx]
            self.rebuild_rows()

    def rebuild_rows(self):
        # Clear layout and re-add in new order
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if isinstance(item, QHBoxLayout):  # Header
                continue
            widget = item.widget()
            if widget:
                self.layout.removeWidget(widget)

        for row in self.rows:
            self.layout.addWidget(row)

        self.update_label()

    def update_label(self):
        self.label.setText(self.label.text().split(":")[0] + f": {len(self.rows)}")
    
    def get_data(self):
        return [row.get_data() for row in self.rows]

def QWidgetWithChildren(widgets: list):
    container = QWidget()
    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    for w in widgets:
        layout.addWidget(w)
    container.setLayout(layout)
    return container

class EquationEditorDialog(QDialog):
    def __init__(self, initial_text="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Equation")
        self.resize(600, 300)

        self.text_area = QPlainTextEdit(self)
        self.text_area.setPlainText(initial_text)
        self.text_area.setPlaceholderText("*equation here*")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.text_area)
        layout.addWidget(buttons)

    def get_equation_text(self):
        return self.text_area.toPlainText()

class EquationButton(QPushButton):
    def __init__(self, equation_text: str="", parent=None):
        super().__init__(equation_text, parent)
        self.equation_text: str = equation_text
        self.display_text: str = ""
        self.set_display_text()
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
QPushButton {
    border: 1px solid white;
    padding: 4px 4px;
    border-radius: 5px;
}
        """)
        self.clicked.connect(self.open_editor)
    
    def set_display_text(self):
        if self.equation_text != "":
            self.display_text = self.equation_text if len(self.equation_text) < 76 else self.equation_text[:50] + "..." + self.equation_text[-25:]

    def set_equation(self, text):
        self.equation_text = text
        self.set_display_text()
        self.setText(self.display_text)

    def open_editor(self):
        dialog = EquationEditorDialog(self.equation_text, self)
        if dialog.exec() == QDialog.Accepted:
            new_text = dialog.get_equation_text()
            self.set_equation(new_text)

class FunctionDropdown(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)  # Optional: let user type if needed

    def update_options(self, function_list: list[str]):
        current = self.currentText()
        self.blockSignals(True)  # Optional: prevent signal spamming during update
        self.clear()
        self.addItems(function_list)
        

        if current in function_list:
            self.setCurrentText(current)
        else:
            self.setCurrentIndex(-1)  # No selection
        self.blockSignals(False)

class FormulationTab(QWidget):
    functions_updated = Signal(list)

    def __init__(self):
        super().__init__()

        self.setObjectName("FormulationTab")
        self.font_size = 24
        self.setStyleSheet("""
            #FormulationTab {
                font-size: 24px;
                font-family: "Courier New", monospace;
            }

            #FormulationTab QLabel,
            #FormulationTab QLineEdit,
            #FormulationTab QPushButton {
                font-size: 24px;
                font-family: "Courier New", monospace;
            }
            QPushButton:focus {
                outline: none;
            }
            QPushButton, #AutoWidthLineEdit {
                border-width: 1px;
                border-style: solid;
                border-color: #aaa;
            }
        """)

        self.variables  = Section("*Variable", variable_row)
        self.constants  = Section("*Constant", constant_row)
        self.objectives = Section("*Objective", lambda i: objective_row(i, self), on_change_callback=self.refresh_function_list)
        self.equality   = Section("*Equality-Constraint", lambda i: eq_constraint_row(i, self), on_change_callback=self.refresh_function_list)
        self.inequality = Section("*Inequality-Constraint", lambda i: ineq_constraint_row(i, self), on_change_callback=self.refresh_function_list)
        self.function   = Section("*Function", function_row, on_change_callback=self.refresh_function_list)

        form_layout = QVBoxLayout(self)
        form_layout.addWidget(self.variables)
        form_layout.addWidget(self.constants)
        form_layout.addWidget(self.objectives)
        form_layout.addWidget(self.equality)
        form_layout.addWidget(self.inequality)
        form_layout.addWidget(self.function)
    
    def create_fnc_file(self):
        ret = """
#-----------------------------------------------------------------------
# Input File Start
#-----------------------------------------------------------------------\n
"""
        vars = self.variables.get_data()
        ret += f"*VARIABLE: {len(vars)}\n"
        for _min, name, _max in vars:
            ret += f"{name.upper()}: {_min}, {_max}, REAL, {1e-6}\n"
        ret += "\n"

        cons = self.constants.get_data()
        ret += f"*CONSTANT: {len(cons)}\n"
        for name, value in cons:
            ret += f"{name.upper()}: {value};\n"
        ret += "\n"

        objs = self.objectives.get_data()
        ret += f"*OBJECTIVE: {len(objs)}\n"
        for name, func in objs:
            ret += f"{name.upper()}: {func};\n"
        ret += "\n"

        eqs = self.equality.get_data()
        ret += f"*EQUALITY-CONSTRAINT: {len(eqs)}\n"
        for name, func, threshold in eqs:
            ret += f"{name.upper()}: {func}{' - ' + str(threshold) if float(threshold) != 0.0 else ''};\n"
        ret += "\n"

        ineqs = self.inequality.get_data()
        ret += f"*EQUALITY-CONSTRAINT: {len(ineqs)}\n"
        for name, func, sign, threshold in eqs:
            ret += f"{name.upper()}: {'-' if sign == 'gt' else ''}{func}{' - ' + str(threshold) if float(threshold) != 0.0 else ''};\n"
        ret += "\n"

        funcs = self.function.get_data()
        ret += f"*FUNCTION: {len(funcs)}\n"
        for name, func in funcs:
            ret += f"{name.upper()}: {func};\n"
        ret += "\n"

        ret += """
#-----------------------------------------------------------------------
# End of input file
#-----------------------------------------------------------------------
"""
        return ret

    def refresh_function_list(self, rename_map=None):
        function_names = [x[0] for x in self.function.get_data()]
        print(function_names)
        self.functions_updated.emit(function_names)
        self.rename_map = rename_map or {}

def variable_row(index):
    return [
        AutoWidthLineEdit("0.0"),
        QLabel("≤"),
        AutoWidthLineEdit(f"X{index + 1}"),
        QLabel("≤"),
        AutoWidthLineEdit("1.0"),
    ]

def constant_row(index):
    return [
        AutoWidthLineEdit(f"C{index + 1}"),
        QLabel("="),
        AutoWidthLineEdit("1.0"),
        QLabel(";"),
    ]

def objective_row(index, parent: FormulationTab):
    drop = FunctionDropdown()
    parent.functions_updated.connect(drop.update_options)

    return [
        AutoWidthLineEdit(f"O{index + 1}"),
        QLabel("="),
        drop,
        QLabel(";"),
    ]

def eq_constraint_row(index, parent: FormulationTab):
    drop = FunctionDropdown()
    parent.functions_updated.connect(drop.update_options)

    return [
        AutoWidthLineEdit(f"EC{index + 1}"),
        QLabel("\u21d2"),
        drop,
        QLabel("="),
        AutoWidthLineEdit("0.0"),
        QLabel(";"),
    ]

def ineq_constraint_row(index, parent: FormulationTab):
    drop = FunctionDropdown()
    parent.functions_updated.connect(drop.update_options)

    return [
        AutoWidthLineEdit(f"INEC{index + 1}"),
        QLabel("\u21d2"),
        drop,
        ToggleIneqButton(),
        AutoWidthLineEdit("0.0"),
        QLabel(";"),
    ]

def function_row(index):
    func_name = AutoWidthLineEdit(f"F{index + 1}")
    equation_btn = EquationButton()

    def my_handler(w):
        print(w.text())

    func_name.editingFinished.connect(lambda w=func_name: my_handler(w))

    return [
        func_name,
        QLabel("="),
        equation_btn,
        QLabel(";"),
    ]

def main():
    app = QApplication([])
    window = QWidget()
    window.setWindowTitle("Formulation Editor")
    layout = QVBoxLayout()
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    ft = FormulationTab()
    scroll.setWidget(ft)
    layout.addWidget(scroll)
    window.setLayout(layout)
    window.resize(700, 500)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
