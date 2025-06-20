import re

import qtawesome as qta
from PySide6.QtGui import QIcon, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QMessageBox
from PySide6.QtGui import (QDoubleValidator, QIcon,
                           QStandardItem, QStandardItemModel)
from PySide6.QtWidgets import (QAbstractItemView, 
                               QDialog, QDialogButtonBox,
                               QGridLayout,QLabel, QLineEdit, QMessageBox,
                               QScrollArea, QVBoxLayout, QWidget)

from handlers.filereader import TextFileReader
from handlers.stylesheet import get_icon_color
from pages.mainwindow import Ui_MainWindow
from handlers.latexviewer import LaTeXViewer


class FML:
    """A class managing the formulation page"""

    def __init__(self, ui: Ui_MainWindow, handle_error):
        """Initialize with an instance of the UI"""
        self.ui = ui

        self.objectiveKeys = []
        self.equalityKeys = []
        self.inequalityKeys = []
        self.gradientKeys = []

        self.equalityMods = {}
        self.inequalityMods = {}

        # read in by a file
        self.metamodelFuncs: dict[str, str] = {}

        # any added by a file
        self.importedFuncs: dict[str, str] = {}

        # included in the program
        self.definedFuncs: dict[str, str] = {}

        # any variable ranges defined anywhere
        self.varRanges: dict[str, str] = {}

        self.currentKey = None
        self.init_model()
        self.handle_error = handle_error

    def has_data(self):
        return len(self.get_all_func_keys()) > 0

    def fnc_file_reader(
        self, filename: str, is_file_string: bool = False
    ) -> int:
        """Read in an .fnc file

        Parameters
        ----------
        filename : string
            The filename to read in or a string representing the contents of a file
        is_file_string : boolean
            Whether or not the first variable is the contents of a file
        """

        if not is_file_string:
            var2 = None
            var4 = TextFileReader(filename, "#$*/|", self.handle_error)

            if not var4.is_file_open():
                return -1

            var2 = var4.read_line()
            if var2 == None:
                return self.wrong_format_ret(filename, var4)
            try:
                while var2 != "":
                    if var2[0].lower() == "f" or var2[0:2].lower() == "gf":
                        name, stringDef = re.split(":|=", var2.replace(";", ""))
                        name = name.split("_")[0].upper()

                        while name.strip() in self.importedFuncs:
                            nameNumber = "".join(i for i in name if i.isdigit())
                            name = (
                                f"{''.join(i for i in name if i.isalpha())}{int(nameNumber) + 1}"
                            )

                        self.importedFuncs[name.strip()] = stringDef.strip()
                    elif var2[0].lower() == "x":
                        varName, bounds = var2.split(":")
                        lowerBounds, upperBounds = [
                            i.strip() for i in bounds.split(",")[:2]
                        ]

                        name = f"{varName.upper()}"
                        while (
                            name.strip() in self.varRanges
                        ):
                            nameNumber = "".join(i for i in name if i.isdigit())
                            name =  f"{''.join(i for i in name if i.isalpha())}{int(nameNumber) + 1}"

                        self.varRanges[name.strip()] = (
                            lowerBounds + ", " + upperBounds
                        )

                    var2 = var4.read_line()

                var4.close()
                self.has_data = True
                self.update_combos()
                self.add_metamodel_tree_rows(
                    self.importedFuncs, self.ui.fmlImportedRow
                )
                self.add_metamodel_tree_rows(self.varRanges, self.ui.fmlVarRow)
                return 1
            except Exception as e:
                return self.wrong_format_ret(filename, var4)
        else:
            lines = [
                i
                for i in filename.split("\n")
                if len(i) > 0 and i[0] not in "#$*/|"
            ]
            try:
                if self.ui.settings.value("ReplaceMMD") == 'true':
                    self.metamodelFuncs.clear()

                for line in lines:
                    # read in the functions
                    if line[0].lower() == "f" or line[0:2].lower() == "gf":
                        name, stringDef = re.split(":|=", line.replace(";", ""))
                        name = name.split("_")[0].upper()

                        while name.strip() in self.metamodelFuncs:
                            nameNumber = "".join(i for i in name if i.isdigit())
                            name = (
                                f"{''.join(i for i in name if i.isalpha())}{int(nameNumber) + 1}"
                            )

                        self.metamodelFuncs[name.strip()] = stringDef.strip()
                    # read in the variables
                    elif line[0].lower() == "x":
                        varName, bounds = line[0].split(":")
                        lowerBounds, upperBounds = [
                            i.strip() for i in bounds.split(",")[:2]
                        ]

                        name = f"{varName.upper()} "
                        while (
                            name.strip() in self.varRanges
                            or name.strip() in self.varRanges
                        ):
                            nameNumber = "".join(
                                i for i in name.split(")")[0] if i.isdigit()
                            )
                            name = f"{name.split(')')[0]}{int(nameNumber) + 1}"

                        self.varRanges[name.strip()] = (
                            lowerBounds + ", " + upperBounds
                        )

                self.has_data = True
                self.update_combos()
                self.add_metamodel_tree_rows(
                    self.metamodelFuncs, self.ui.fmlMetamodelRow
                )
                self.add_metamodel_tree_rows(self.varRanges, self.ui.fmlVarRow)
                return 1
            except Exception as e:
                return self.wrong_format_ret(filename, None)

    def get_file_str(self):
        """Get the file string for the current formulate setup"""
        # do PR funcs need formulation?

        innerFileString = """
#-----------------------------------------------------------------------
# Input File Start
#-----------------------------------------------------------------------\n
        """

        functions = {}

        # variable constraints
        innerFileString += (
            f"\n*VARIABLE: {len(self.ui.varRangeCombo.currentData())}\n\n"
        )
        for count, func in enumerate(self.ui.varRangeCombo.currentData()):
            bounds = self.getFuncDefinition(func).split(",")
            innerFileString += (
                f"{func}:\t{bounds[0]},\t{bounds[1]},\tREAL,\t0.000001\n"
            )

        # objective functions
        innerFileString += (
            f"\n*OBJECTIVE: {len(self.ui.optFuncCombo.currentData())}\n\n"
        )
        for count, func in enumerate(self.ui.optFuncCombo.currentData()):
            funcAlias = "F" + str(len(functions.keys()) + 1)
            if func not in functions.values():
                functions[funcAlias] = func
                innerFileString += f"O{count + 1} = {funcAlias};\n"
            else:
                innerFileString += (
                    f"O{count + 1} ="
                    f" {[pair[1] for pair in functions.items() if pair[1] == func][0]};\n"
                )

        # ineq constraints
        innerFileString += (
            "\n*EQUALITY-CONSTRAINT:"
            f" {len(self.ui.eqFuncCombo.currentData())}\n\n"
        )
        for count, func in enumerate(self.ui.eqFuncCombo.currentData()):
            funcAlias = "F" + str(len(functions.keys()) + 1)
            cleansed = self.extract_func_name(func)
            if func not in functions.values():
                functions[funcAlias] = func
                innerFileString += f"EC{count + 1} = {funcAlias}{' - ' + self.equalityMods[cleansed] if cleansed in self.equalityMods else ''};\n"
            else:
                innerFileString += (
                    f"EC{count + 1} ="
                    f" {[self.extract_func_name(pair[1]) for pair in functions.items() if pair[1] == func][0]}{' - ' + self.equalityMods[cleansed] if cleansed in self.equalityMods else ''};\n"
                )

        # eq constraints
        innerFileString += (
            "\n*INEQUALITY-CONSTRAINT:"
            f" {len(self.ui.ineqFuncCombo.currentData())}\n\n"
        )
        for count, func in enumerate(self.ui.ineqFuncCombo.currentData()):
            funcAlias = "F" + str(len(functions.keys()) + 1)
            cleansed = self.extract_func_name(func)
            if func not in functions.values():
                functions[funcAlias] = func
                innerFileString += f"INEC{count + 1} = {funcAlias}{' - ' + self.inequalityMods[cleansed] if cleansed in self.inequalityMods else ''};\n"
            else:
                innerFileString += (
                    f"INEC{count + 1} ="
                    f" {[self.extract_func_name(pair[1]) for pair in functions.items() if pair[1] == func][0]}{' - ' + self.inequalityMods[cleansed] if cleansed in self.inequalityMods else ''};\n"
                )

        # functions
        innerFileString += f"\n*FUNCTION: {len(functions)}\n"
        for count, func in enumerate(functions.keys()):
            innerFileString += (
                f"F{count + 1} = {self.getFuncDefinition(functions[func], func_type=functions[func])};\n\n"
            )

        # gradient functions
        necessary_grad_keys = []

        for funcX in self.ui.optFuncCombo.currentData():
            for varX in self.ui.varRangeCombo.currentData():
                necessary_grad_keys.append(f"G{funcX.upper()}-{varX.upper()}")

        matching_keys = set(
            [
                i
                for i in self.get_all_func_keys()
                if i.upper() in necessary_grad_keys
            ]
        )

        if len(necessary_grad_keys) != len(matching_keys):
            innerFileString += (
                "\n# Gradient function-variable combinations are missing:\n"
            )
            for i in sorted(
                set(necessary_grad_keys).difference(
                    [i.upper() for i in matching_keys]
                )
            ):
                innerFileString += f"#\t{i}\n"
            innerFileString += "# Skipping gradients.\n\n"
        else:
            innerFileString += f"\n*GRADIENTS: {len(matching_keys)}\n\n"
            for grad in sorted(matching_keys):
                innerFileString += (
                    f"{grad.upper()} = {self.getFuncDefinition(grad)};\n"
                )

        innerFileString += "\n#-----------------------------------------------------------------------\n"
        innerFileString += "# End of input file\n"
        innerFileString += "#-----------------------------------------------------------------------\n"

        return innerFileString
    
    def extract_func_name(self, name: str) -> str:
        return name.replace(" (IMP)", "").replace(" (UDF)", "").replace(" (MMD)", "")

    def wrong_format_ret(self, filename: str, reader: TextFileReader) -> int:
        """Return an error if invalid formatting is detected in the file"""

        self.handle_error(
            f"Invalid format <{filename}>.\nLine #:"
            f" {reader.get_current_line_number()}"
        )
        reader.close()
        return -1

    def get_sorted_order_for_funcs(self, x: str):
        return int(x.split(" ")[0][1:]) if "-" not in x else 0

    def add_metamodel_tree_rows(
        self,
        dict: dict[str, str],
        tree_row: QStandardItem,
        deny_delete: bool = False,
    ) -> None:
        """Add rows to the function options

        Parameters
        ----------
        dict : dict[str, str]
            The key/value pairs of functions to add to the function row
        tree_row : QStandardItem
            The row these functions are being added to
        deny_delete : boolean
            Prevent thes rows from being editable or deletable
        """
        rows = [QStandardItem(i) for i in dict.keys() if i[0].lower() == "x" or i[0].lower() == "f"]
        rows.sort(key=lambda x: int(x.text()[1:]))

        # remove all the old rows
        [tree_row.removeRow(0) for _ in range(tree_row.rowCount())]
        
        icon_color = get_icon_color(self.ui.settings.value("Theme"), self.ui.settings.value("ThemeColor"))

        for row in rows:
            edit = QStandardItem(qta.icon("fa5s.edit", color=icon_color), "")
            delete = QStandardItem(qta.icon("fa5s.trash", color=icon_color), "")
            edit.setToolTip("Edit Function")
            delete.setToolTip("Delete Function")

            if deny_delete:
                tree_row.appendRow([row])
            else:
                tree_row.appendRow([row, edit, delete])

    def update_combos(self):
        """Updates the function comboboxes with the latest function options"""
        allKeys = []

        [allKeys.append(i + " (MMD)") for i in list(self.metamodelFuncs.keys()) if re.match("^[F][0-9]*$", i)]
        [allKeys.append(i + " (UDF)") for i in list(self.definedFuncs.keys()) if re.match("^[F][0-9]*$", i)]
        [allKeys.append(i + " (IMP)") for i in list(self.importedFuncs.keys()) if re.match("^[F][0-9]*$", i)]

        self.ui.optFuncCombo.updateWithValues(allKeys)
        self.ui.eqFuncCombo.updateWithValues(allKeys)
        self.ui.ineqFuncCombo.updateWithValues(allKeys)
        allKeys.sort(key=lambda x: int(x.split(' ')[0][1:]))
        self.ui.varRangeCombo.updateWithValues(
            sorted([i for i in self.get_all_func_keys() if re.match("^[X][0-9]*$", i)], key=lambda x: int(x[1]))
        )

    def show_grad_policy(self):
        """Open a dialog explaining the gradient handling policy"""
        QMessageBox.information(
            self.ui.centralwidget,
            "PyPROE Gradient Policy",
            "Gradients are auto-selected from any defined function matching the"
            " naming scheme GF1-X1, GF1-X2...GFm-Xn for the variables defined"
            " in Variable Ranges and the functions defined in Optimization"
            " Functions.\n\nIf one or more gradients are missing for SLSQP"
            " optimization, gradients will be approximated.\n\nNo gradients are"
            " necessary for optimization with genetic algorithms.",
            QMessageBox.Ok,
        )

    def get_all_func_keys(self) -> list[str]:
        """Returns a list of all function names"""
        return (
            list(self.metamodelFuncs.keys())
            + list(self.importedFuncs.keys())
            + list(self.definedFuncs.keys())
            + list(self.varRanges.keys())
        )
    
    def clear_env(self):
        """Deletes all loaded definitions"""
        val = QMessageBox.warning(
            self.ui.centralwidget,
            "Overwriting Environment",
            "Are you sure you want to delete all your currently loaded definitions?",
            QMessageBox.Ok | QMessageBox.Cancel,
        )
        if val == QMessageBox.Ok:
            # reset all the state
            self.objectiveKeys = []
            self.equalityKeys = []
            self.inequalityKeys = []
            self.gradientKeys = []
            self.metamodelFuncs = {}
            self.importedFuncs = {}
            self.definedFuncs = {}
            self.varRanges = {}
            self.currentKey = None
            self.update_combos()
            self.update_treeview()
            self.ui.lineEdit.setText("")
            self.ui.formFuncPreview.setPlainText("")
            self.ui.formFuncEdit.setPlainText("")
        else:
            return 1

    def update_treeview(self) -> None:
        """Remove stale values and add new rows to the treeview"""
        self.ui.fmlMetamodelRow.removeRows(
            0, self.ui.fmlMetamodelRow.rowCount()
        )
        self.add_metamodel_tree_rows(
            self.metamodelFuncs, self.ui.fmlMetamodelRow
        )
        self.ui.fmlImportedRow.removeRows(0, self.ui.fmlImportedRow.rowCount())
        self.add_metamodel_tree_rows(self.importedFuncs, self.ui.fmlImportedRow)

        self.ui.fmlDefinedRow.removeRows(0, self.ui.fmlDefinedRow.rowCount())
        self.add_metamodel_tree_rows(self.definedFuncs, self.ui.fmlDefinedRow)

        self.ui.fmlVarRow.removeRows(0, self.ui.fmlVarRow.rowCount())
        self.add_metamodel_tree_rows(self.varRanges, self.ui.fmlVarRow)

    def init_model(self):
        """Initialize the function treeview"""
        self.ui.formFuncLibrary.clicked.connect(
            lambda x: self.tree_click_handler(x)
        )
        self.ui.formFuncLibrary.setHeaderHidden(True)
        self.ui.fmlTreeModel = QStandardItemModel()
        self.ui.fmlTreeModel.setColumnCount(3)

        self.ui.fmlMetamodelRow = QStandardItem(
            QIcon("file.png"), "Metamodel Functions (MMD)"
        )
        self.ui.fmlImportedRow = QStandardItem(
            QIcon("file.png"), "Imported Functions (IMP)"
        )
        self.ui.fmlDefinedRow = QStandardItem(
            QIcon("file.png"), "User Defined Functions (UDF)"
        )
        self.ui.fmlVarRow = QStandardItem(QIcon("file.png"), "Variable Ranges")

        self.ui.fmlTreeModel.appendRow(self.ui.fmlMetamodelRow)
        self.ui.fmlTreeModel.appendRow(self.ui.fmlImportedRow)
        self.ui.fmlTreeModel.appendRow(self.ui.fmlDefinedRow)
        self.ui.fmlTreeModel.appendRow(self.ui.fmlVarRow)
        self.ui.formFuncLibrary.setModel(self.ui.fmlTreeModel)

        self.ui.formFuncLibrary.header().setStretchLastSection(False)
        self.ui.formFuncLibrary.header().setSectionResizeMode(
            0, QHeaderView.Stretch
        )
        self.ui.formFuncLibrary.header().setSectionResizeMode(
            1, QHeaderView.Fixed
        )
        self.ui.formFuncLibrary.setColumnWidth(1, 20)
        self.ui.formFuncLibrary.header().setSectionResizeMode(
            2, QHeaderView.Fixed
        )
        self.ui.formFuncLibrary.setColumnWidth(2, 20)
        self.ui.formFuncLibrary.setEditTriggers(
            QAbstractItemView.NoEditTriggers
        )

        self.ui.formSaveBtn.clicked.connect(self.save_func)
        self.ui.formSaveBtn.setEnabled(False)

        self.ui.formResetBtn.clicked.connect(self.reset_func)
        self.ui.formNewBtn.clicked.connect(self.new_func)
        self.ui.lineEdit.textChanged.connect(
            lambda text: self.ui.formSaveBtn.setEnabled(len(text.strip()) > 0)
        )

    def check_overwrite(self) -> int:
        """Pull up a modal to double-check function overwrite"""
        if len(self.ui.formFuncEdit.document().toPlainText()) != 0:
            val = QMessageBox.warning(
                self.ui.centralwidget,
                "Overwriting Definition",
                "Are you sure you want to overwrite your current definition?",
                QMessageBox.Ok | QMessageBox.Cancel,
            )
            if val == QMessageBox.Ok:
                return 0
            else:
                return 1
        return 0

    def new_func(self):
        """Set the UI to accept a new function"""
        if not self.check_overwrite():
            self.currentKey = "New Definition"
            self.ui.lineEdit.setText(self.currentKey)
            self.ui.formFuncEdit.setPlainText("")

    def reset_func(self):
        """Reset the UI to the previous function definition"""
        self.ui.lineEdit.setText(self.currentKey)
        funcDefinition = self.getFuncDefinition(self.currentKey)
        self.ui.formFuncPreview.setPlainText(funcDefinition)
        self.ui.formFuncEdit.setPlainText(funcDefinition)

    def save_func(self) -> None:
        """Save a new function definition and update the UI with it"""
        if (
            self.ui.lineEdit.text() in self.get_all_func_keys()
            and self.currentKey != self.ui.lineEdit.text()
        ):
            QMessageBox.critical(
                self.ui.centralwidget,
                "Error",
                "Cannot have duplicate definition names.",
                QMessageBox.Ok,
            )
            return

        if self.ui.lineEdit.text() == "New Definition":
            QMessageBox.critical(
                self.ui.centralwidget,
                "Error",
                "Please name your definition properly.",
                QMessageBox.Ok,
            )
            return
    
        if self.ui.lineEdit.text()[0].upper() not in ["F", "X"]:
            QMessageBox.critical(
                self.ui.centralwidget,
                "Error",
                "Please follow the naming schema: Fn or Xn",
                QMessageBox.Ok,
            )
            return
        
        # TODO: Implement saving for ALL functions
        
        # this happens when the user just types in a name and definition without clicking the "New" button
        if not self.currentKey: self.currentKey = self.ui.lineEdit.text().upper()

        if self.currentKey in self.metamodelFuncs:
            self.metamodelFuncs.pop(self.currentKey)
            self.metamodelFuncs[self.ui.lineEdit.text().upper()] = (
                self.ui.formFuncEdit.document().toPlainText()
            )
        elif self.currentKey in self.importedFuncs:
            self.importedFuncs.pop(self.currentKey)
            self.importedFuncs[self.ui.lineEdit.text().upper()] = (
                self.ui.formFuncEdit.document().toPlainText()
            )
        elif self.currentKey[0].upper() == "X":
            if self.currentKey in self.varRanges:
                self.varRanges.pop(self.currentKey)
            self.varRanges[self.ui.lineEdit.text().upper()] = (
                self.ui.formFuncEdit.document().toPlainText()
            )
        else:
            if self.currentKey in self.definedFuncs:
                self.definedFuncs.pop(self.currentKey)
            self.definedFuncs[self.ui.lineEdit.text().upper()] = (
                self.ui.formFuncEdit.document().toPlainText()
            )

        self.ui.lineEdit.clear()
        self.ui.formFuncEdit.clear()
        self.currentKey = None
        self.update_combos()
        self.update_treeview()

    def tree_click_handler(self, item_index: int) -> None:
        """Handle click actions for the tree at the given item index"""
        data = item_index.data()
        column = item_index.column()

        parent_index = item_index.parent()
        parent_data = parent_index.data() if parent_index.isValid() else ""

        funcName = self.extract_func_name(item_index.siblingAtColumn(0).data())
        funcDefinition = self.getFuncDefinition(funcName, func_type=parent_data)

        if column == 1 and data != None and not self.check_overwrite():
            self.ui.lineEdit.setText(funcName)
            self.ui.formFuncPreview.setPlainText(funcDefinition)
            self.ui.formFuncEdit.setPlainText(funcDefinition)
            self.currentKey = funcName
        elif column == 0 and (
            "Functions" not in data or "Variable" not in data
        ):
            self.ui.formFuncPreview.setPlainText(funcDefinition)
        elif column == 2 and data != None:
            proceed = QMessageBox.warning(
                self.ui.centralwidget,
                "Possible Data Loss",
                "Are you sure you want to delete this function?",
                QMessageBox.Ok | QMessageBox.Cancel,
            )

            if proceed == QMessageBox.Ok:
                if funcName in self.metamodelFuncs:
                    self.metamodelFuncs.pop(funcName)
                elif funcName in self.definedFuncs:
                    self.definedFuncs.pop(funcName)
                elif funcName in self.importedFuncs:
                    self.importedFuncs.pop(funcName)
                elif funcName in self.varRanges:
                    self.varRanges.pop(funcName)
                self.update_combos()
                self.update_treeview()

    def getFuncDefinition(self, key: str, func_type: str = "") -> str | None:
        """Returns the function definition associated with the given key (name)"""
        if func_type == "":  # legacy way of doing it
            key = self.extract_func_name(key)
            if key in self.metamodelFuncs:
                return self.metamodelFuncs[key]
            elif key in self.importedFuncs:
                return self.importedFuncs[key]
            elif key in self.definedFuncs:
                return self.definedFuncs[key]
            elif key in self.varRanges:
                return self.varRanges[key]
            else:
                return None
        
        key = self.extract_func_name(key)
        if "(MMD)" in func_type:
            return self.metamodelFuncs.get(key, None)
        elif "(IMP)" in func_type:
            return self.importedFuncs.get(key, None)
        elif "(UDF)" in func_type:
            return self.definedFuncs.get(key, None)
        elif "Variable Ranges" in func_type:
            return self.varRanges.get(key, None)
        return None

    def getConstraintModifications(
        self,
    ):
        """Programmatically build a dialog to ask the user for constraint modifications"""
            
        if len(self.ui.eqFuncCombo.currentData()) + len(self.ui.ineqFuncCombo.currentData()) == 0:
            return

        # copy values initially so the user can cancel
        eqMods = self.equalityMods.copy()
        ineqMods = self.inequalityMods.copy()

        def setEqConstr(func, val):
            eqMods[func] = val

        def setIneqConstr(func, val):
            ineqMods[func] = val

        rangeDialog = QDialog(self.ui.centralwidget)
        rangeDialog.setWindowTitle("Redefine Constraints")
        rangeDialog.setMaximumWidth(800)
        rangeDialog.setMaximumHeight(400)
        dialogLayout = QVBoxLayout()

        scrollWidget = QWidget(self.ui.centralwidget)
        scrollarea = QScrollArea(rangeDialog)

        masterLayout = QGridLayout()
        scrollWidget.setLayout(masterLayout)

        # track only the necessary function modifications
        eqFuncs = []
        ineqFuncs = []

        # add the variable selection components
        for count, func in enumerate(self.ui.eqFuncCombo.currentData()):
            func = self.extract_func_name(func)
            eqFuncs.append(func)
            layout = QGridLayout()

            # establish the number inputs
            layout.addWidget(QLabel(f"{func} = "), 0, 0)

            lineEdit = QLineEdit(eqMods[func] if func in eqMods else '0')
            lineEdit.setValidator(
                QDoubleValidator(
                    -100000000000.0, 100000000000.0, 50, notation=QDoubleValidator.StandardNotation
                )
            )
            lineEdit.textChanged.connect(
                lambda x, name=func: setEqConstr(name, x)
            )


            layout.addWidget(lineEdit, 1, 0)
            masterLayout.addLayout(layout, count, 0)


        # add the variable selection components
        for count, func in enumerate(self.ui.ineqFuncCombo.currentData()):
            func = self.extract_func_name(func)
            ineqFuncs.append(func)
            layout = QGridLayout()

            # establish the number inputs
            layout.addWidget(QLabel(f"{func} <= "), 0, 0)

            lineEdit = QLineEdit(ineqMods[func] if func in ineqMods else '0')
            lineEdit.setValidator(
                QDoubleValidator(
                    -100000000000.0, 100000000000.0, 50, notation=QDoubleValidator.StandardNotation
                )
            )
            lineEdit.textChanged.connect(
                lambda x, name=func: setIneqConstr(name, x)
            )


            layout.addWidget(lineEdit, 1, 0)
            masterLayout.addLayout(layout, count, 1)

        scrollarea.setWidget(scrollWidget)
        dialogLayout.addWidget(scrollarea)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButtons.Cancel
            | QDialogButtonBox.StandardButtons.Ok
        )
        dialogLayout.addWidget(buttons)
        buttons.accepted.connect(rangeDialog.accept)
        buttons.rejected.connect(rangeDialog.reject)
        rangeDialog.setLayout(dialogLayout)
        proceed = rangeDialog.exec()

        if proceed == 1:
            self.equalityMods = {k: v for k, v in eqMods.items() if k in eqFuncs}
            self.inequalityMods = {k: v for k, v in ineqMods.items() if k in ineqFuncs}
        else:
            pass

    def show_latex(self):
        fns = [self.getFuncDefinition(func, func_type=func) for func in self.ui.optFuncCombo.currentData()]
        eqs = [self.getFuncDefinition(func, func_type=func) for func in self.ui.eqFuncCombo.currentData()]
        iqs = [self.getFuncDefinition(func, func_type=func) for func in self.ui.ineqFuncCombo.currentData()]

        self.latex = LaTeXViewer(fns, eqs, iqs, {'theme': self.ui.settings.value("Theme"), 'color': self.ui.settings.value("ThemeColor")})
        self.latex.show()
