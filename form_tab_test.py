from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QScrollArea, QSizePolicy,
    QDialog, QDialogButtonBox, QPlainTextEdit
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFontMetrics
import sys

class AutoWidthLineEdit(QLineEdit):
    def __init__(self, text='', parent=None):
        super().__init__(text, parent)

        self.setAlignment(Qt.AlignCenter)
        
        # Track size changes
        self.textChanged.connect(self.update_width)

        # Allow expansion if needed
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self.setStyleSheet("""
            QLineEdit {
                padding: 4px;
                border: 1px solid #aaa;
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
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Add actual input widgets
        for elem in elements:
            layout.addWidget(elem)

        layout.addStretch()

        # Control buttons
        self.delete_button = QPushButton("✕")
        self.up_button = QPushButton("↑")
        self.down_button = QPushButton("↓")

        for btn in [self.up_button, self.down_button, self.delete_button]:
            btn.setFixedSize(24, 24)
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

class ToggleIneqButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("≤", parent)
        self.setFixedWidth(40)
        self.clicked.connect(self.toggle_operator)

    def toggle_operator(self):
        self.setText("≥" if self.text() == "≤" else "≤")

    def get_operator(self):
        return self.text()
    
class Section(QWidget):
    def __init__(self, title: str, row_generator):
        super().__init__()
        self.row_generator = row_generator
        self.rows = []

        self.layout = QVBoxLayout()
        header = QHBoxLayout()

        self.label = QLabel(f"{title.upper()}: 0")
        self.add_button = QPushButton("+")
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
        # Use the row_generator, passing index if needed
        row = self.row_generator(len(self.rows))

        # Wrap in InlineRow with this Section as parent
        inline = InlineRow(row, parent_section=self)

        self.rows.append(inline)
        self.layout.addWidget(inline)
        self.update_label()

        # If values were passed, set them
        if values:
            for widget, value in zip(inline.findChildren(QLineEdit), values):
                widget.setText(str(value))

    def remove_row(self, row_widget):
        self.rows.remove(row_widget)
        row_widget.setParent(None)
        row_widget.deleteLater()
        self.update_label()

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

class FormulationTab(QWidget):
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
        """)

        form_layout = QVBoxLayout(self)

        form_layout.addWidget(Section("*Variables", variable_row))
        form_layout.addWidget(Section("*Constants", constant_row))
        form_layout.addWidget(Section("*Objective", objective_row))
        form_layout.addWidget(Section("*Equality Constraint", eq_constraint_row))
        form_layout.addWidget(Section("*Inequality Constraint", ineq_constraint_row))
        form_layout.addWidget(Section("*Function", function_row))

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
        self.equation_text = equation_text
        self.display_text = self.get_display_text()
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        # self.setStyleSheet("""
        #     QPushButton {
        #         border: none;
        #         color: #007acc;
        #         background-color: transparent;
        #         text-align: left;
        #         font-style: italic;
        #     }
        #     QPushButton:hover {
        #         text-decoration: underline;
        #         color: #005f99;
        #     }
        # """)
        self.clicked.connect(self.open_editor)
    
    def get_display_text(self):
        if self.equation_text != "":
            self.display_text = self.equation_text if len(self.equation_text) < 200 else 0 

    def set_equation(self, text):
        self.equation_text = text
        self.setText(text if len(text) < 50 else text[:47] + "...")

    def open_editor(self):
        dialog = EquationEditorDialog(self.equation_text, self)
        if dialog.exec() == QDialog.Accepted:
            new_text = dialog.get_equation_text()
            self.set_equation(new_text)

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
        QLabel(";")
    ]

def objective_row(index):
    return [
        AutoWidthLineEdit(f"O{index + 1}"),
        QLabel("="),
        AutoWidthLineEdit(f"F{index + 1}"),
        QLabel(";"),
    ]

def eq_constraint_row(index):
    return [
        AutoWidthLineEdit(f"EC{index + 1}"),
        QLabel("▶"),
        AutoWidthLineEdit(f"F{index + 1}"),
        QLabel("="),
        AutoWidthLineEdit("0.0"),
        QLabel(";"),
    ]

def ineq_constraint_row(index):
    return [
        AutoWidthLineEdit(f"INEC{index + 1}"),
        QLabel("▶"),
        AutoWidthLineEdit(f"F{index + 1}"),
        ToggleIneqButton(),
        AutoWidthLineEdit("0.0"),
        QLabel(";"),
    ]

def function_row(index):
    equation_btn = EquationButton()

    return [
        AutoWidthLineEdit(f"F{index + 1}"),
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
    scroll.setWidget(FormulationTab())
    layout.addWidget(scroll)
    window.setLayout(layout)
    window.resize(700, 500)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
