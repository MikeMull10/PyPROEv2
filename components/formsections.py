from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt, Signal

from qfluentwidgets import TitleLabel, PrimaryToolButton, FluentIcon as FI

from components.formitems import DefaultItem, VariableItem, ConstantItem, ObjectiveItem, FunctionItem, EqualityItem, InequalityItem
from components.clickabletitle import ClickableSubtitleLabelIcon

class FormSection(QWidget):
    def __init__(self, title: str="", clickable_title: bool=True):
        super().__init__()
        self.number_items = 0
        self.showing = True

        # --- Main layout for the section ---
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # --- Top bar layout ---
        self.top_bar = QHBoxLayout()
        self.title_raw = title

        if clickable_title:
            self.title = ClickableSubtitleLabelIcon(f"{self.title_raw}: 0")
            self.title.clicked.connect(self.toggle_view)
        else:
            self.title = TitleLabel(f"{self.title_raw}: 0")
        
        self.add_btn = PrimaryToolButton(FI.ADD)
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.clicked.connect(lambda: self.add_row())
        self.add_btn.setToolTip(f"Add {title[:-1] if title.endswith('s') else title}")

        self.top_bar.addWidget(self.title)
        self.top_bar.addStretch()
        self.top_bar.addWidget(self.add_btn)

        self.main_layout.addLayout(self.top_bar)

        # --- Row container layout ---
        self.row_container = QVBoxLayout()
        self.row_container.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addLayout(self.row_container)
    
    def toggle_view(self):
        for i in range(self.row_container.count()):
            if self.title.showing:
                self.row_container.itemAt(i).widget().show()
            else:
                self.row_container.itemAt(i).widget().hide()

    def add_row(self, item: DefaultItem):
        item.remove_btn.clicked.connect(lambda _, w=item: self.delete_item(w))
        item.up_arrow.clicked.connect(lambda _, w=item: self.move(w, "UP"))
        item.down_arrow.clicked.connect(lambda _, w=item: self.move(w, "DOWN"))
        if not self.showing: item.hide()
        self.update_count()

    def delete_item(self, item: DefaultItem):
        self.row_container.removeWidget(item)
        item.deleteLater()
        self.update_count()
    
    def update_count(self):
        title = self.title.label if type(self.title) == ClickableSubtitleLabelIcon else self.title
        title.setText(f"{self.title_raw}: {self.row_container.count()}")
    
    def swap_rows(self, i: int, j: int):
        layout = self.row_container
        if i == j:
            return

        # Ensure valid indices
        if i < 0 or j < 0 or i >= layout.count() or j >= layout.count():
            return

        # Get widgets at the positions
        item_i = layout.itemAt(i)
        item_j = layout.itemAt(j)

        widget_i = item_i.widget()
        widget_j = item_j.widget()

        # Remove both from layout (this does NOT delete the widgets)
        layout.removeWidget(widget_i)
        layout.removeWidget(widget_j)

        # Reinsert in swapped positions
        if i < j:
            layout.insertWidget(i, widget_j)
            layout.insertWidget(j, widget_i)
        else:
            layout.insertWidget(j, widget_i)
            layout.insertWidget(i, widget_j)

    def move(self, widget, dir: str="UP"):
        layout = self.row_container

        for i in range(layout.count()):
            if layout.itemAt(i).widget() is widget:
                index = i
                break
        else:
            return

        self.swap_rows(index, index - (1 if dir == "UP" else -1))

    def get_fnc(self) -> str:
        raise NotImplementedError
    
    def clear(self) -> None:
        while self.row_container.count() > 0:
            item = self.row_container.itemAt(0).widget()
            self.row_container.removeWidget(item)
            item.deleteLater()
        
        self.update_count()

class VariablesSection(FormSection):
    row_count_changed = Signal(int)

    def __init__(self, clickable_title: bool=True):
        super().__init__("Variables", clickable_title=clickable_title)
    
    def add_row(self, var_min: float = 0.0, var_max: float = 1.0, var_name=None):
        if not var_name:
            var_name = f"X{self.row_container.count() + 1}"

        item = VariableItem(var_name, var_min, var_max)
        self.row_container.addWidget(item)

        super().add_row(item)
        self.row_count_changed.emit(self.row_container.count())
    
    def get_fnc(self) -> str:
        ret = f"*VARIABLE: {self.row_container.count()}\n\n"

        for i in range(self.row_container.count()):
            item: VariableItem = self.row_container.itemAt(i).widget()

            ret += f"{item.var_box.text()}: {item.min_box.text()}, {item.max_box.text()}\n"

        return ret
    
    def delete_item(self, item: DefaultItem):
        super().delete_item(item)
        self.row_count_changed.emit(self.row_container.count())
    
class ConstantsSection(FormSection):
    def __init__(self):
        super().__init__("Constants")
    
    def add_row(self, name: str = None, value: float = 0.0):
        if not name:
            name = f"C{self.row_container.count() + 1}"
        
        item = ConstantItem(name, value)
        self.row_container.addWidget(item)

        super().add_row(item)
    
    def get_fnc(self):
        ret = f"*CONSTANT: {self.row_container.count()}\n\n"

        for i in range(self.row_container.count()):
            item: ConstantItem = self.row_container.itemAt(i).widget()

            ret += f"{item.name_box.text().lower()} = {item.value_box.text()};\n"
        
        return ret

class ObjectivesSection(FormSection):
    def __init__(self, function_name_update: callable=None):
        super().__init__("Objectives")
        self.function_name_update = function_name_update
    
    def add_row(self, name: str=None, value: str=""):
        if not name:
            name = f"O{self.row_container.count() + 1}"

        item = ObjectiveItem(name, value)
        self.row_container.addWidget(item)

        super().add_row(item)
        if self.function_name_update: self.function_name_update()
    
    def delete_item(self, item):
        super().delete_item(item)
        if self.function_name_update: self.function_name_update()

    def get_fnc(self):
        ret = f"*OBJECTIVE: {self.row_container.count()}\n\n"

        for i in range(self.row_container.count()):
            item: ObjectiveItem = self.row_container.itemAt(i).widget()

            ret += f"{item.name_box.text()} = {item.value_box.text()};\n"

        return ret

class EqualitiesSection(FormSection):
    def __init__(self, parent=None, function_name_update: callable=None):
        super().__init__("Equality-Constraints")
        self.parent = parent
        self.function_name_update = function_name_update

    def add_row(self, name: str = None, value: str = "", eq_value: float = 0.0):
        if not name:
            name = f"EQ{self.row_container.count() + 1}"

        item = EqualityItem(name, value, eq_value, self.parent)
        self.row_container.addWidget(item)

        super().add_row(item)
        if self.function_name_update: self.function_name_update()
    
    def delete_item(self, item):
        super().delete_item(item)
        if self.function_name_update: self.function_name_update()
    
    def get_fnc(self):
        ret = f"*EQUALITY-CONSTRAINT: {self.row_container.count()}\n\n"

        for i in range(self.row_container.count()):
            item: EqualityItem = self.row_container.itemAt(i).widget()
            
            eq_text = item.eq_box.text().strip()
            sign = '+' if eq_text.startswith('-') else '-'
            eq = eq_text[1:] if eq_text.startswith('-') else eq_text

            if eq_text == "0.0" or eq_text == "0":
                ret += f"{item.name_box.text()} = {item.value_box.text()};\n"
                continue

            ret += f"{item.name_box.text()} = {item.value_box.text()} {sign} {eq};\n"

        return ret

class InequalitiesSection(FormSection):
    def __init__(self, parent=None, function_name_update: callable=None):
        super().__init__("Inequality-Constraints")
        self.parent = parent
        self.function_name_update = function_name_update

    def add_row(self, name: str = None, value: str = "", eq_value: float = 0.0):
        if not name:
            name = f"INEQ{self.row_container.count() + 1}"

        item = InequalityItem(name, value, eq_value, self.parent)
        self.row_container.addWidget(item)

        super().add_row(item)
        if self.function_name_update: self.function_name_update()
    
    def delete_item(self, item):
        super().delete_item(item)
        if self.function_name_update: self.function_name_update()
    
    def get_fnc(self):
        ret = f"*INEQUALITY-CONSTRAINT: {self.row_container.count()}\n\n"

        for i in range(self.row_container.count()):
            item: InequalityItem = self.row_container.itemAt(i).widget()
            
            ineq_text = item.eq_box.text().strip()
            sign = '+' if ineq_text.startswith('-') else '-'
            ineq = ineq_text[1:] if ineq_text.startswith('-') else ineq_text

            if ineq_text == "0.0" or ineq_text == "0":
                ret += f"{item.name_box.text()} = {item.value_box.text()};\n"
                continue
            
            if item.flip.leq:
                ret += f"{item.name_box.text()} = {item.value_box.text()} {sign} {ineq};\n"
            else:
                ret += f"{item.name_box.text()} = -({item.value_box.text()} {sign} {ineq});\n"

        return ret

class FunctionsSection(FormSection):
    row_count_changed = Signal(int)

    def __init__(self, parent=None, function_name_update: callable=None, clickable_title: bool=True):
        super().__init__("Functions", clickable_title=clickable_title)
        self.parent = parent
        self.function_name_update = function_name_update

    def add_row(self, name: str = None, value: str = ""):
        if not name:
            name = f"F{self.row_container.count() + 1}"

        item = FunctionItem(name, value, self.parent)
        self.row_container.addWidget(item)

        super().add_row(item)
        if self.function_name_update: self.function_name_update()
        self.row_count_changed.emit(self.row_container.count())

    def delete_item(self, item):
        super().delete_item(item)
        if self.function_name_update: self.function_name_update()
        self.row_count_changed.emit(self.row_container.count())
    
    def get_fnc(self):
        ret = f"*FUNCTION: {self.row_container.count()}\n\n"

        for i in range(self.row_container.count()):
            item: FunctionItem = self.row_container.itemAt(i).widget()

            ret += f"{item.name_box.text()} = {item.value_box.equation_text};\n"

        return ret
