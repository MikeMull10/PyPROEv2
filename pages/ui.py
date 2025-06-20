import ctypes
import sys
import re

import qtawesome as qta
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtCore import QSettings, Qt, QUrl
from PySide6.QtGui import (QAction, QColor, QCursor, QDesktopServices,
                           QDoubleValidator, QIcon, QKeySequence, QShortcut,
                           QStandardItem, QStandardItemModel, QTextOption)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QComboBox,
                               QDialog, QDialogButtonBox, QFileDialog,
                               QGridLayout, QInputDialog, QLabel, QLineEdit,
                               QMainWindow, QMenuBar, QMessageBox, QPushButton,
                               QScrollArea, QSizePolicy, QTextEdit, QToolTip, 
                               QVBoxLayout, QHBoxLayout, QWidget, QCheckBox)

from components.customtabledelegate import TableDelegate
from components.customtreeviwe import NewTreeView
from components.multiselect import MultiSelect
from handlers.devconsole import CommandConsole
from handlers.errorhandler import ErrorHandler
from handlers.inputfnc import InputFile, create_function_from_string, clean
from handlers.stylesheet import resource_path, load_stylesheet, PALETTES, NEON_COLORS, ICON_COLORS
from pages.designexp import DOE, normalize_to_real_value
from pages.mainwindow import Ui_MainWindow
from pages.formulate import FML
from pages.gradients import GRAD
from pages.metamodel import MMD
from pages.optconfig import OPT
from pages.plotting import PLOT

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np

from datetime import datetime
from copy import copy

import os
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
os.environ["QT_SCALE_FACTOR"] = "1"


class Interface(QMainWindow):
    """Subclass of QMainWindow for the PyGoose interface"""

    def __init__(self, parent=None):
        """All the necessary inits of settings, layouts, and programmatically added components"""
        super(Interface, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.settings = QSettings("PyPROE", "Interface")

        self.setup_settings()
        self.ui.setupUi(self)
        self.ui.verticalLayout_3.setSpacing(0)

        # add the subclassed QTreeView
        self.ui.formFuncLibrary = NewTreeView(self.ui.tabForm)
        self.ui.formFuncLibrary.setObjectName("formFuncLibrary")
        sizePolicy4 = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(
            self.ui.formFuncLibrary.sizePolicy().hasHeightForWidth()
        )
        self.ui.formFuncLibrary.setSizePolicy(sizePolicy4)

        self.ui.gridLayout_2.addWidget(self.ui.formFuncLibrary, 0, 0, 1, 1)

        # error handling
        self.error_manager = ErrorHandler(self.ui)

        # file managing
        self.open_files = [ None for i in range(8) ]

        # initialize the pages
        self.DOE = DOE(self.ui, self.error_manager)
        self.MMD = MMD(self.ui, self.error_manager)
        self.FML = FML(self.ui, self.error_manager)
        self.OPT = OPT(self.ui, self.error_manager)
        self.MMD.bindTo(self.mmd_data_status_change)
        self.PLOT = PLOT(self.ui)
        self.GRAD = GRAD(self.ui, self.error_manager)

        # add custom widgets
        self.ui.optFuncCombo = MultiSelect()
        self.ui.verticalLayout_5.addWidget(self.ui.optFuncCombo)

        self.ui.eqFuncCombo = MultiSelect(editFlag="=")
        self.ui.verticalLayout_13.addWidget(self.ui.eqFuncCombo)

        self.ui.ineqFuncCombo = MultiSelect(editFlag="<=")
        self.ui.verticalLayout_15.addWidget(self.ui.ineqFuncCombo)

        self.ui.varRangeCombo = MultiSelect()
        self.ui.verticalLayout_12.addWidget(self.ui.varRangeCombo)

        self.set_taskbar_icons()
        self.set_combo_options()
        self.set_themes()

        # set up the tab change handlers and navigate to the last opened one
        self.ui.tabEditBtn.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentIndex(0)
        )
        self.ui.tabEditBtn.clicked.connect(self.setup_tab_handlers)
        self.ui.doeMetamodel.clicked.connect(self.send_to_metamodel)

        self.ui.tabMMDBtn.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentIndex(1)
        )
        self.ui.tabMMDBtn.clicked.connect(self.setup_tab_handlers)

        self.ui.tabOptBtn.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentIndex(2)
        )
        self.ui.tabOptBtn.clicked.connect(self.setup_tab_handlers)

        self.ui.tabWriterBtn.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentIndex(3)
        )
        self.ui.tabWriterBtn.clicked.connect(self.setup_tab_handlers)

        self.ui.tabFormulationBtn.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentIndex(4)
        )
        self.ui.tabFormulationBtn.clicked.connect(self.setup_tab_handlers)
        self.ui.stackedWidget.setCurrentIndex(
            int(self.ui.settings.value("Tab"))
        )

        self.ui.tabMatpltBtn.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentIndex(5)
        )
        self.ui.tabMatpltBtn.clicked.connect(self.setup_tab_handlers)

        self.ui.tabGradientBtn.clicked.connect(
            lambda: self.ui.stackedWidget.setCurrentIndex(6)
        )
        self.ui.tabGradientBtn.clicked.connect(self.setup_tab_handlers)

        self.ui.openDoeFile.clicked.connect(self.open_file_dialog)

        self.setup_tab_handlers()
        self.ui.optStopBtn.setEnabled(False)
        self.ui.centralwidget.layout().setContentsMargins(0, 0, 0, 0)

        self.ui.mmdFormBtn.clicked.connect(  # send to formulate tab from modeling
            lambda: self.ui.stackedWidget.setCurrentIndex(4)
        )
        self.ui.mmdFormBtn.clicked.connect(self.setup_tab_handlers)
        self.ui.mmdFormBtn.clicked.connect(
            lambda: self.FML.fnc_file_reader(
                self.ui.mmdEdit.document().toPlainText(), True
            )
        )
        self.ui.form_constr_mods.clicked.connect(self.FML.getConstraintModifications)
        self.ui.mmdOrderCombo.addItems(["0", "1"])
        self.ui.normalizeFNC.deleteLater()  # delete the normalize button ... for now

        ### Fun shortcut stuff :)
        self.ctrl_right = QShortcut(QKeySequence("Ctrl+Right"), self)
        self.ctrl_right.activated.connect(self.move_tab_right)
        self.ctrl_right.activated.connect(lambda: self.kon_check('r'))

        self.ctrl_left = QShortcut(QKeySequence("Ctrl+Left"), self)
        self.ctrl_left.activated.connect(self.move_tab_left)
        self.ctrl_left.activated.connect(lambda: self.kon_check('l'))

        self.ctrl_t = QShortcut(QKeySequence("Ctrl+T"), self)
        self.ctrl_t.activated.connect(self.open_settings)

        # CTRL1-7 shortcuts
        for i, o in enumerate([0, 1, 4, 2, 5, 6, 3]):
            tab = QShortcut(QKeySequence(f"Ctrl+{i + 1}"), self)
            tab.activated.connect(lambda o=o: self.change_tab(o))
        
        # QOL shortcuts
        self.ctrl_q = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.ctrl_q.activated.connect(self.close_application)

        self.is_fullscreen = False
        self.ctrl_f = QShortcut(QKeySequence("Ctrl+F"), self)
        self.ctrl_f.activated.connect(self.toggle_fullscreen)

        self.esc = QShortcut(QKeySequence("Esc"), self)
        self.esc.activated.connect(self.disable_fullscreen)

        self.ctrl_enter = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.ctrl_enter.activated.connect(self.submit)
        self.ctrl_enter.activated.connect(lambda: self.kon_check('e'))

        # advanced mode
        self.in_advanced_mode = False

        # self.ctrl_e = QShortcut(QKeySequence("Ctrl+E"), self)
        # self.ctrl_e.activated.connect(self.advanced_mode)

        ### SECRET FUN THING
        self.pressed_keys = []
        QShortcut(QKeySequence("Ctrl+A"), self).activated.connect(lambda: self.kon_check('a'))
        QShortcut(QKeySequence("Ctrl+B"), self).activated.connect(lambda: self.kon_check('b'))
        QShortcut(QKeySequence("Ctrl+Up"), self).activated.connect(lambda: self.kon_check('u'))
        QShortcut(QKeySequence("Ctrl+Down"), self).activated.connect(lambda: self.kon_check('d'))

        ### DEV CONSOLE
        QShortcut(QKeySequence("Ctrl+M"), self).activated.connect(self.open_console)
        self.console = None
    
    def open_console(self):
        if not self.console or not self.console.isVisible():
            self.console = CommandConsole(self, self.ui, self.set_themes)  # Pass main window as parent
            self.console.show()  # Non-blocking popup

    def send_to_metamodel(self):
        """Send design of experiements data to the metamodeling page"""
        self.ui.stackedWidget.setCurrentIndex(1)
        self.setup_tab_handlers()
        self.ui.mmdFileLabel.setText(f"Reading DOE Table")
        try:
            data = self.DOE.display_des_matrix()

            self.MMD.read_design_file(data, is_str=True)
        except:
            pass

        if not self.MMD.read_doe_tab(self.DOE) == 1:
            QMessageBox.critical(
                self.ui.centralwidget,
                "Error",
                "Failed to read DOE table. Check your parameters.",
                QMessageBox.Ok,
            )

    def preview_file(self):
        """Open a file preview modal with he correct data based on the current page"""
        if self.ui.stackedWidget.currentIndex() == 0 and self.DOE.has_data:
            self.create_preview_popup(
                "DOE File Preview", self.DOE.display_des_matrix()
            )
        elif self.ui.stackedWidget.currentIndex() == 1 and self.MMD.has_data:
            self.create_preview_popup(
                "MMD File Preview", self.MMD.mmd_full_func_file_str()
            )
        elif self.ui.stackedWidget.currentIndex() == 2 and self.OPT.result_file is not None:
            self.create_preview_popup(
                "Optimization Output Preview", self.OPT.result_file
            )
        elif self.ui.stackedWidget.currentIndex() == 4 and self.FML.has_data:
            self.create_preview_popup(
                "FNC File Preview", self.FML.get_file_str()
            )
        elif (
            self.ui.stackedWidget.currentIndex() == 6
            and self.ui.gradientOutput.toPlainText() != ""
        ):
            self.create_preview_popup("FNC File Preview", self.ui.gradientOutput.toPlainText())
        else:
            QMessageBox.critical(
                self.ui.centralwidget,
                "Error",
                "No data available to preview.",
                QMessageBox.Ok,
            )

    def create_preview_popup(
        self,
        title: str,
        text: str,
        width: int = 400,
        height: int = 400,
        readOnly: bool = True,
        wordWrap=QTextOption.NoWrap,
    ):
        preview = QDialog(self.ui.centralwidget)
        preview.setWindowTitle(title)
        preview.resize(width, height)
        previewLayout = QVBoxLayout()
        previewText = QTextEdit(preview)
        previewText.setText(text)
        previewText.setReadOnly(readOnly)
        previewText.setWordWrapMode(wordWrap)
        previewLayout.addWidget(previewText)
        preview.setLayout(previewLayout)
        preview.exec()

    def setup_settings(self):
        """Initialize the settings file"""
        try:
            if not self.ui.settings.contains("Solver"):
                self.ui.settings.setValue("Solver", "./GimOPT/GimOPT_v03.exe")
            if not self.ui.settings.contains("Tab"):
                self.ui.settings.setValue("Tab", 0)
            if not self.ui.settings.contains("RecentOpenDir"):
                self.ui.settings.setValue("RecentOpenDir", "")
            if not self.ui.settings.contains("RecentSaveDir"):
                self.ui.settings.setValue("RecentSaveDir", "")
            if not self.ui.settings.contains("Theme"):
                self.ui.settings.setValue("Theme", "White")
            if not self.ui.settings.contains("ThemeColor"):
                self.ui.settings.setValue("ThemeColor", "")
            if not self.ui.settings.contains("ClearConfirm"):
                self.ui.settings.setValue("ClearConfirm", True)
            if not self.ui.settings.contains("ReplaceMMD"):
                self.ui.settings.setValue("ReplaceMMD", True)
            if not self.ui.settings.contains("Tolerance"):
                self.ui.settings.setValue("Tolerance", 1e-20)
            if not self.ui.settings.contains("Popup-Color"):
                self.ui.settings.setValue("Popup-Color", "#051923")
            if not self.ui.settings.contains("Popup-Finish"):
                self.ui.settings.setValue("Popup-Finish", True)
            if not self.ui.settings.contains("WSFTol"):
                self.ui.settings.setValue("WSFTol", 1e-20)
            if not self.ui.settings.contains("WSFMaxIter"):
                self.ui.settings.setValue("WSFMaxIter", 100)
        except:
            self.handle_error(
                "Error in settings file. Resetting user configuration."
            )
            self.ui.settings.clear()

    def setup_tab_handlers(self):
        """Handle all the switching in between pages"""
        current_index = self.ui.stackedWidget.currentIndex()

        self.open_file_name = self.open_files[ current_index ]
        self.save_file_name = None

        match current_index:
            case 0:  # set up DOE tab
                self.ui.tabEditBtn.setChecked(True)
                self.ui.tabMMDBtn.setChecked(False)
                self.ui.tabOptBtn.setChecked(False)
                self.ui.tabWriterBtn.setChecked(False)
                self.ui.tabFormulationBtn.setChecked(False)
                self.ui.tabMatpltBtn.setChecked(False)
                self.ui.tabGradientBtn.setChecked(False)
                self.open_file_title = "Open a DOE file"
                self.save_file_title = "Save a DOE file"
                self.open_file_ext_desc = "Design of experiment files (*.doe)"
                self.save_file_ext_desc = self.open_file_ext_desc + ";;Any files (*)"
                self.open_file_ext = ["doe"]
                self.save_file_ext = self.open_file_ext + ["*.*"]
                # self.textOutput = self.ui.doeEdit
            case 1:  # set up MMD tab
                self.ui.tabMMDBtn.setChecked(True)
                self.ui.tabEditBtn.setChecked(False)
                self.ui.tabOptBtn.setChecked(False)
                self.ui.tabWriterBtn.setChecked(False)
                self.ui.tabFormulationBtn.setChecked(False)
                self.ui.tabMatpltBtn.setChecked(False)
                self.ui.tabGradientBtn.setChecked(False)
                self.open_file_title = "Open a DOE file"
                self.save_file_title = "Save a function file"
                self.open_file_ext_desc = "Design of experiment files (*.doe)"
                self.save_file_ext_desc = "Meta-format function files (*.fnc);;Any files (*)"
                self.open_file_ext = ["doe"]
                self.save_file_ext = ["fnc", "*.*"]
                self.textOutput = self.ui.mmdEdit
                if not self.MMD.has_data:
                    self.ui.mmdFileLabel.setText(
                        "No file opened for metamodeling."
                    )
            case 2:  # set up OPT tab
                self.ui.tabOptBtn.setChecked(True)
                self.ui.tabMMDBtn.setChecked(False)
                self.ui.tabEditBtn.setChecked(False)
                self.ui.tabWriterBtn.setChecked(False)
                self.ui.tabFormulationBtn.setChecked(False)
                self.ui.tabMatpltBtn.setChecked(False)
                self.ui.tabGradientBtn.setChecked(False)
                self.open_file_title = "Open a OPT file"
                self.save_file_title = "Save a OPT file"
                self.open_file_ext_desc = "Optimization function files (*.fnc)"
                self.save_file_ext_desc = "Optimization output files (*.out);;Any files (*)"
                self.open_file_ext = ["fnc"]
                self.save_file_ext = ["out", "*.*"]
                self.textOutput = self.ui.optEdit
                if not self.open_file_name or not ".fnc" in self.open_file_name:
                    self.ui.optFileLabel.setText(
                        "No file opened for optimization."
                    )
            case 3:  # set up Writer
                self.ui.tabWriterBtn.setChecked(True)
                self.ui.tabMMDBtn.setChecked(False)
                self.ui.tabOptBtn.setChecked(False)
                self.ui.tabEditBtn.setChecked(False)
                self.ui.tabFormulationBtn.setChecked(False)
                self.ui.tabMatpltBtn.setChecked(False)
                self.ui.tabGradientBtn.setChecked(False)
                self.open_file_title = "Open a text file"
                self.save_file_title = "Save a text file"
                self.open_file_ext_desc = ""
                self.save_file_ext_desc = self.open_file_ext_desc
                self.open_file_ext = ["*.*"]
                self.save_file_ext = self.open_file_ext
                self.textOutput = self.ui.wrtEdit
            case 4:  # set up Formulation
                self.ui.tabWriterBtn.setChecked(False)
                self.ui.tabMMDBtn.setChecked(False)
                self.ui.tabOptBtn.setChecked(False)
                self.ui.tabEditBtn.setChecked(False)
                self.ui.tabFormulationBtn.setChecked(True)
                self.ui.tabMatpltBtn.setChecked(False)
                self.ui.tabGradientBtn.setChecked(False)
                self.open_file_title = "Open a FNC file"
                self.save_file_title = "Save a FNC file"
                self.open_file_ext_desc = "Meta-format function files (*.fnc)"
                self.save_file_ext_desc = "Meta-format function files (*.fnc);;Any files (*)"
                self.open_file_ext = ["fnc"]
                self.save_file_ext = ["fnc", "*.*"]
                self.textOutput = self.ui.formFuncEdit
            case 5:  # set up Plotting
                self.ui.tabWriterBtn.setChecked(False)
                self.ui.tabMMDBtn.setChecked(False)
                self.ui.tabOptBtn.setChecked(False)
                self.ui.tabEditBtn.setChecked(False)
                self.ui.tabFormulationBtn.setChecked(False)
                self.ui.tabMatpltBtn.setChecked(True)
                self.ui.tabGradientBtn.setChecked(False)
                self.open_file_title = "Open a FNC file"
                self.save_file_title = "Save a FNC file"
                self.open_file_ext_desc = "Meta-format function files (*.fnc)"
                self.open_file_ext = ["fnc"]
                self.save_file_ext = [""]
                self.textOutput = self.ui.wrtEdit
            case 6:  # set up Gradient calculation
                self.ui.tabWriterBtn.setChecked(False)
                self.ui.tabMMDBtn.setChecked(False)
                self.ui.tabOptBtn.setChecked(False)
                self.ui.tabEditBtn.setChecked(False)
                self.ui.tabFormulationBtn.setChecked(False)
                self.ui.tabMatpltBtn.setChecked(False)
                self.ui.tabGradientBtn.setChecked(True)
                self.open_file_title = "Open a FNC file"
                self.save_file_title = "Save a FNC file"
                self.open_file_ext_desc = "Meta-format function files (*.fnc)"
                self.save_file_ext_desc = "Meta-format function files (*.fnc);;Any files (*)"
                self.open_file_ext = ["fnc"]
                self.save_file_ext = ["fnc", "*.*"]
                self.textOutput = self.ui.wrtEdit

    def confirm_action(self, title: str, message: str) -> bool:
        """
        Show a confirmation dialog and return the user's choice.

        Args:
            title (str): The title of the confirmation dialog.
            message (str): The message to display in the dialog.

        Returns:
            bool: True if the user confirms, False otherwise.
        """
        confirmation_box = QMessageBox()
        confirmation_box.setWindowIcon(QIcon(resource_path("PyPROE.ico")))
        confirmation_box.setIcon(QMessageBox.Warning)
        confirmation_box.setWindowTitle(title)
        confirmation_box.setText(message)
        confirmation_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        confirmation_box.setDefaultButton(QMessageBox.No)
        result = confirmation_box.exec()

        return result == QMessageBox.Yes

    def set_combo_options(self):
        """Set the options for all the combos"""
        # --- Design of Experiments Stuff ---
        #
        self.ui.methodCombo.addItems(
            [
                "Factorial",
                "Central Composite, Spherical",
                "Central Composite, Face-Centered",
                "Taguchi Orthogonal Array",
                "Latin Hypercube",
            ]
        )
        self.ui.methodCombo.currentIndexChanged.connect(
            self.handle_design_type_change
        )
        self.ui.doeDesignBtn.clicked.connect(self.trigger_design_slot)
        self.ui.doe_edit_vals.clicked.connect(
            lambda: self.trigger_design_slot(
                self.DOE.var_bounds if self.DOE.var_bounds != [] else None,
                self.DOE.func_defs if self.DOE.func_defs != [] else None,
                self.DOE.num_points,
            )
        )
        self.ui.doe_add_point.clicked.connect(
            lambda: (
                self.DOE.handle_add_point(),
                self.update_doe_table(self.DOE.num_vars),
            )
        )
        self.ui.doe_rmv_point.clicked.connect(
            lambda: (
                self.DOE.handle_remove_point(),
                self.update_doe_table(self.DOE.num_vars),
            )
        )
        self.ui.doe_clearBtn.clicked.connect(self.doe_clear)

        # --- Metamodeling Stuff ---
        #
        self.ui.mmdDoeButton.clicked.connect(self.open_file_dialog)
        self.ui.mmdMethodCombo.addItems(
            ["Polynomial Regression", "Radial Basis Functions"]
        )
        self.ui.mmdMethodCombo.currentIndexChanged.connect(
            self.handle_mmd_change
        )
        self.ui.mmdTableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.oneFuncBtn.clicked.connect(self.mmd_gen_func)
        self.ui.clearDispBtn.clicked.connect(self.mmd_clear)
        self.ui.funcValBtn.clicked.connect(self.mmd_find_func_val)
        self.handle_mmd_change(0)

        # --- Optimization Stuff ---
        #
        self.ui.opt_solverCombo.addItems(
            [
                "SLSQP (Single Obj)",
                "SLSQP + WSF",
                "NSGAII",
                "NSGAIII",
            ]
        )
        self.ui.opt_solverCombo.currentIndexChanged.connect(
            self.OPT.set_solver_options
        )
        self.OPT.set_solver_options()

        self.ui.optFncBtn.clicked.connect(self.open_file_dialog)
        self.ui.opt_startBtn.clicked.connect(self.opt_start)
        self.ui.opt_clearBtn.clicked.connect(self.opt_clear)

        self.ui.formOptBtn.clicked.connect(self.send_form_to_opt)
        self.ui.form_grad_policy.clicked.connect(self.FML.show_grad_policy)
        self.ui.form_load_file.clicked.connect(self.open_file_dialog)
        self.ui.formResetEnv.clicked.connect(self.FML.clear_env)
        self.ui.view_latex.clicked.connect(self.FML.show_latex)

        # Plotting stuff
        self.ui.plotOpenFile.clicked.connect(self.open_file_dialog)
        self.ui.genPlot.clicked.connect(self.contour_plot_start)
        self.ui.genSurface.clicked.connect(self.surface_popup)

        # Gradient tab stuff
        self.ui.gradientOpenFile.clicked.connect(self.open_file_dialog)
        self.ui.genGradientsBtn.clicked.connect(self.gen_grads)
        self.ui.genBlankTemplate.clicked.connect(self.gen_blank_template)
        self.ui.normalizeFNC.clicked.connect(self.normalize_fnc)

        self.ui.normalize_function.addItems(["No", "Yes"])

    def send_form_to_opt(self) -> None:
        """Send formulation data to the optimization page"""
        self.OPT = OPT(self.ui, self.error_manager)
        self.ui.opt_solverCombo.currentIndexChanged.connect(
            self.OPT.set_solver_options
        )
        self.OPT.set_solver_options()
        self.OPT.input_file = self.FML.get_file_str()
        self.OPT.input_file_is_str = True
        self.open_file_name = ""
        self.open_files[2] = ""
        self.ui.stackedWidget.setCurrentIndex(2)
        self.setup_tab_handlers()
        self.ui.optFileLabel.setText("Reading Formulation tab")

    def opt_clear(self, bypass: bool = False) -> None:
        """Clear the optimization page output"""
        if self.ui.settings.value("ClearConfirm") == 'true' and not bypass:
            # Show the confirmation popup
            confirmed = self.confirm_action(
                "Confirm Clear", 
                "Are you sure you want to clear all the Optimization data? This action cannot be undone."
            )
            if not confirmed:
                return  # User canceled the action

        self.ui.optEdit.clear()
        try:
            self.ui.graphWidget.setParent(None)
            self.ui.viewGraph.setParent(None)
        except Exception as e:
            pass

    def doe_clear(self) -> None:
        """Reset the state of the DOE page"""
        if self.ui.settings.value("ClearConfirm") == 'true':
            # Show the confirmation popup
            confirmed = self.confirm_action(
                "Confirm Clear", 
                "Are you sure you want to clear all DOE data? This action cannot be undone."
            )
            if not confirmed:
                return  # User canceled the action
        
        self.ui.doeTable.model().clear()
        self.DOE = DOE(self.ui, self.handle_error)
        
        button = self.ui.verticalLayout_11.parentWidget().findChild(QPushButton, "compareBtn")
        if button:
            button.deleteLater()
    
    def mmd_clear(self, bypass: bool = False) -> None:
        """Reset the state of the MMD page"""
        if self.ui.settings.value("ClearConfirm") == 'true' and not bypass:
            # Show the confirmation popup
            confirmed = self.confirm_action(
                "Confirm Clear", 
                "Are you sure you want to clear all Metamodeling data? This action cannot be undone."
            )
            if not confirmed:
                return  # User canceled the action
        
        if self.ui.mmdEdit: self.ui.mmdEdit.clear()
        if self.ui.mmdTableView.model(): self.ui.mmdTableView.model().clear()

    def mmd_gen_func(self) -> None:
        """Generate functions for the metamodeling tab"""
        
        self.mmd_clear(bypass=True)

        var1: int = self.ui.mmdMethodCombo.currentIndex() # check mmd method: 0 -> polynomial regression, 1 -> radial-basis functions
        abstractModel = QStandardItemModel()
        self.ui.mmdTableView.setItemDelegate(
            TableDelegate(abstractModel, self.MMD)
        )
        self.ui.mmdTableView.setModel(abstractModel)
        self.ui.mmdTableView.setAlternatingRowColors(True)
        cols = (
            [f"f{i + 1}(x)" for i in range(len(self.MMD.PR_Funcs))]
            if var1 == 0
            else [
                self.ui.mmdFuncCombo.itemText(i)
                for i in range(1, self.ui.mmdFuncCombo.count() + 1)
            ]
        )
        rows = (
            ["F", "Pr>F", "R2", "R2adj", "RMSE", "PRESS", "R2press"]
            if var1 == 0
            else ["Min", "Max", "Avg", "Norm"]
        )
        abstractModel.setVerticalHeaderLabels(rows)

        if var1 == 0:
            var2: int = self.ui.mmdOrderCombo.currentIndex()
            var5 = (
                len(self.MMD.PR_Funcs) if var1 == 0 else len(self.MMD.RBF_Funcs)
            )

            var3 = var5

            abstractModel = self.generate_mmd(var1, self.ui.mmdFuncCombo.currentIndex(), var2, cols, abstractModel)

        else:  # do Radial Basis Function
            # print(self.MMD)
            # self.MMD.read_design_file(self.DOE.display_des_matrix(), is_str=True)
            if (
                self.MMD.get_mmd_funcs(
                    self.ui.mmdMethodCombo.currentIndex(),
                    self.ui.mmdFuncCombo.currentIndex(),
                    self.ui.mmdOrderCombo.currentIndex(),
                )
                == 1
            ):
                self.ui.mmdEdit.append(self.MMD.get_func_str())
                abstractModel.insertColumn(
                    0,
                    [
                        QStandardItem(i.split("\n")[0])
                        for i in self.MMD.get_stats().split(
                            "= " if var1 == 0 else ": "
                        )[1:]
                    ],
                )
                abstractModel.setHorizontalHeaderItem(
                    0,
                    QStandardItem(
                        f"Radius ({self.ui.mmdFuncCombo.currentText()})"
                    ),
                )
                self.ui.mmdFormBtn.setEnabled(True)
            else:
                QMessageBox.critical(
                    self.ui.centralwidget,
                    "Error",
                    "Failed to generate metamodels. Check your parameters.",
                    QMessageBox.Ok,
                )
    
    def generate_mmd(self, _method: int, _type: int, _order: int, cols: list, abstract_model: QStandardItemModel) -> None:
        # check to see if mmd funcs are invalid
        if self.MMD.get_mmd_funcs(_method, _type, _order) != 1:
            QMessageBox.critical(
                self.ui.centralwidget,
                "Error",
                "Failed to generate at least one function. Check your"
                " parameters.",
                QMessageBox.Ok,
            )
            return

        headers = [
            "Linear",
            "Quad Int",
            "Quad No"
        ]

        num_funcs = len(self.MMD.pr.data)
        for f in range(num_funcs):
            abstract_model = self.add_column(abstract_model, f"{headers[_type]} - F{f + 1}", self.MMD.get_stats(_type, f))

        self.ui.mmdFormBtn.setEnabled(True)

        self.ui.mmdEdit.append(self.MMD.get_func_str())

        return abstract_model
    
    def add_column(self, abstract_model: QStandardItemModel, header: str, data: list):
        col_num = abstract_model.columnCount()

        for row, val in enumerate(data):
            item = QStandardItem(val)
            abstract_model.setItem(row, col_num, item)

        abstract_model.setHeaderData(col_num, Qt.Horizontal, header)
        
        return abstract_model

    def mmd_find_func_val(self) -> None:
        """Find function values for the metamodeling tab"""
        if not self.MMD.has_data:
            QMessageBox.critical(
                self.ui.centralwidget,
                "Error",
                "No functions have been generated yet.",
                QMessageBox.Ok,
            )
            return
        if self.MMD.get_num_vars() < 0:
            QMessageBox.critical(
                self.ui.centralwidget,
                "Error",
                "There must be more than 0 variables in the .doe file.",
                QMessageBox.Ok,
            )
            return
        vals, ok = QInputDialog.getText(
            self.ui.centralwidget, "Function Evaluation", "Variable Values (Comma Separated)"
        )
        if ok:
            vals = [
                float(i) for i in re.split(" |,|\t|\t|\n", vals) if i.isdigit()
            ]
            var9 = self.MMD.get_func_value(vals)
            self.textOutput.append("# FUNCTION EVALUATION")
            self.textOutput.append("#-----------------------------------------")

            self.textOutput.append(
                "X[i] = "
                + "\t".join(
                    str(vals[i]) for i in range(self.MMD.get_num_vars())
                )
            )

            for var8 in range(self.MMD.get_num_funcs()):
                self.textOutput.append(f"F{var8+1}(x) = {var9[var8]}")

    def opt_start(self) -> None:
        """Start the optimization process"""
        self.opt_clear(bypass=True)
        if self.open_file_name != "":
            self.OPT.input_file = self.open_file_name
            self.OPT.input_file_is_str = False
        self.error_manager.handle(self.OPT.start_task())

        formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get the current time and format it
        self.ui.optEdit.setText(f"Optimization started at {formatted_time}...")  # Set the formatted time into your UI

    def contour_plot_start(self) -> None:
        """Generate a countour plot"""
        if self.open_file_name is None:
            self.error_manager.handle(1)
            return
        self.PLOT.input_file = self.open_file_name
        self.error_manager.handle(self.PLOT.generate_contour_graph())

    def surface_plot_start(self, function_to_graph: str = "F1") -> None:
        """Generate a surface plot"""
        self.PLOT.input_file = self.open_file_name
        self.error_manager.handle(
            self.PLOT.generate_surface_graph(function_to_graph)
        )

    def surface_popup(self) -> None:
        if self.open_file_name is None:
            self.error_manager.handle(1)
            return

        file = InputFile(self.open_file_name)
        if file.status != 0:
            self.error_manager.handle(file.status)
            return

        # Create a dialog window
        dialog = QDialog()
        dialog.setWindowTitle("Select Function")
        dialog.setWindowIcon(QIcon(resource_path("PyPROE.ico")))

        # Set up the layout
        layout = QVBoxLayout(dialog)

        # Add a label
        label = QLabel("Please select a function:")
        layout.addWidget(label)

        # Create a dropdown menu (QComboBox)
        combo_box = QComboBox()
        combo_box.addItems(list(file.functions.keys()))
        layout.addWidget(combo_box)

        # Create an OK button
        ok_button = QPushButton("GRAPH")
        layout.addWidget(ok_button)

        # Define the action to be triggered when the OK button is pressed
        def on_ok_pressed():
            selected_option = combo_box.currentText()
            self.surface_plot_start(selected_option)
            dialog.accept()  # Close the dialog

        # Connect the OK button to the action
        ok_button.clicked.connect(on_ok_pressed)

        # Show the dialog
        dialog.exec()

    def gen_grads(self) -> None:
        """Generate the gradients for an FNC file."""
        self.GRAD.input_file = self.open_file_name
        self.error_manager.handle(self.GRAD.re_calc_grads())
    
    def gen_blank_template(self) -> None:
        """Generate a blank template for gradients."""
        self.ui.gradientOutput.setPlainText(self.GRAD.get_blank_template())
    
    def normalize_fnc(self) -> None:
        """Generate the normlization of an FNC file."""
        if self.open_file_name is None:
            self.error_manager.handle(1)
            return
        self.GRAD.input_file = self.open_file_name
        self.error_manager.handle(self.GRAD.normalize())

    def error_popup(self, error_message: str) -> None:
        # Create a QMessageBox for the error
        error_popup = QMessageBox()
        error_popup.setIcon(QMessageBox.Critical)
        error_popup.setWindowTitle("Error")
        error_popup.setText("An error has occurred")
        error_popup.setInformativeText(error_message)
        error_popup.setStandardButtons(QMessageBox.Ok)
        error_popup.exec()

    def handle_design_type_change(self, index) -> None:
        """Enable/Disable inputs based on design type change"""
        if index == 4:
            self.ui.designPointNum.setEnabled(True)
            self.ui.levelCombo.setEnabled(False)
        else:
            self.ui.designPointNum.setEnabled(False)
            self.ui.levelCombo.setEnabled(True)

    def trigger_design_slot(
        self,
        var_ranges: list[list[float]] = None,
        func_defs: list[str] = None,
        extra_points: int = 0,
    ):
        """Programmatically build a dialog to ask the user for variable ranges and function definitions"""
        designMethod = int(self.ui.methodCombo.currentIndex())
        designVariableCount = int(
            self.ui.designVarNum.value()
        )  #  if self.DOE.has_data == False else self.DOE.num_points
        designLevelCount = int(self.ui.levelCombo.value())
        designPointCount = int(self.ui.designPointNum.value())
        designFunctionCount = int(self.ui.functionNum.value())

        varRanges = [
            [0, 0] if not var_ranges else var_ranges[i]
            for i in range(designVariableCount)
        ]
        funcStrings = [
            "0" if not func_defs else func_defs[i]
            for i in range(designFunctionCount)
        ]

        def setVarRanges(varNum, bound, val):
            varRanges[varNum][bound] = val

        def setFuncValue(funcNum, val):
            funcStrings[funcNum] = val

        rangeDialog = QDialog(self.ui.centralwidget)
        rangeDialog.setWindowTitle("Define Experiment Properties")
        rangeDialog.setMaximumWidth(800)
        rangeDialog.setMaximumHeight(400)
        dialogLayout = QVBoxLayout()

        scrollWidget = QWidget(self.ui.centralwidget)
        scrollarea = QScrollArea(rangeDialog)

        masterLayout = QGridLayout()
        scrollWidget.setLayout(masterLayout)

        # add the variable selection components
        for variable in range(designVariableCount):
            layout = QGridLayout()

            # establish the number inputs
            layout.addWidget(QLabel(f"X{variable + 1} Lower Bound"), 0, 0)
            layout.addWidget(QLabel(f"X{variable + 1} Upper Bound"), 0, 1)

            lineEdit = QLineEdit(str(varRanges[variable][0]))
            lineEdit.setValidator(
                QDoubleValidator(
                    -100000000000000.0, 100000000000000.0, 50, notation=QDoubleValidator.StandardNotation
                )
            )
            lineEdit.textChanged.connect(
                lambda x, itr=variable: setVarRanges(itr, 0, x)
            )

            lineEdit2 = QLineEdit(str(varRanges[variable][1]))
            lineEdit2.setValidator(
                QDoubleValidator(
                    -100000000000000.0, 100000000000000.0, 50, notation=QDoubleValidator.StandardNotation
                )
            )
            lineEdit2.textChanged.connect(
                lambda x, itr=variable: setVarRanges(itr, 1, x)
            )

            layout.addWidget(lineEdit, 1, 0)
            layout.addWidget(lineEdit2, 1, 1)
            masterLayout.addLayout(layout, variable, 0)

        # add the function string definitions
        for function in range(designFunctionCount):
            layout = QGridLayout()
            line_edit = QLineEdit(funcStrings[function])
            line_edit.setMaxLength(1000000)
            line_edit.setPlaceholderText("X1 + 1")

            layout.addWidget(QLabel(f"F{function + 1} Definition"), 0, 0)
            layout.addWidget(line_edit, 1, 0)

            line_edit.textChanged.connect(
                lambda x, itr=function: setFuncValue(itr, x)
            )

            masterLayout.addLayout(layout, function, 1)

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
            self.DOE.set_var_bounds(varRanges)
            self.DOE.set_func_defs(funcStrings)

            success = (
                self.DOE.get_des_matrix(
                    designMethod,
                    designVariableCount,
                    designLevelCount,
                    designPointCount,
                    designFunctionCount,
                )
                if not extra_points
                else 1
            )

            if success == 1:
                self.update_doe_table(designVariableCount)
            else:
                QMessageBox.critical(
                    self.ui.centralwidget,
                    "Error",
                    "Failed to generate matrix. Check your parameters.",
                    QMessageBox.Ok,
                )

    def update_doe_table(self, design_var_count):
        designModelRows, designModelHeaders = self.DOE.get_des_matrix_model()
        abstractModel = QStandardItemModel()
        self.ui.doeTable.setItemDelegate(TableDelegate(abstractModel, self.DOE))
        abstractModel.setHorizontalHeaderLabels(designModelHeaders)

        self.ui.doeTable.setModel(abstractModel)
        self.ui.doeTable.setAlternatingRowColors(True)

        for count, row in enumerate(designModelRows):
            newRow = [QStandardItem(str(j)) for j in row]

            # prevent any relative values from being editable
            for j in range(design_var_count):
                newRow[j].setEditable(False)
                newRow[j].setStatusTip(
                    "This value is autogenerated and cannot be changed."
                )
                newRow[j].setBackground(QColor("#36454F"))
                if self.ui.settings.value("Theme") == "White":  # change the text color for the white theme (bleh) for Dr. Fang
                    newRow[j].setForeground(QColor("white"))
                elif self.ui.settings.value("Theme") == "Dark":  # change the background color for the dark theme
                    newRow[j].setBackground(QColor("#1C1C1C"))

            abstractModel.insertRow(count, newRow)

        abstractModel.setVerticalHeaderLabels(
            [f"Point {x + 1}" for x in range(len(designModelRows))]
        )

        button = self.ui.verticalLayout_11.parentWidget().findChild(QPushButton, "compareBtn")
        if not button:
            button = QPushButton("Sensitivity Analysis")
            button.setObjectName("compareBtn")
            button.clicked.connect(self.handle_doe_compare)
            self.ui.verticalLayout_11.addWidget(button)
    
    def handle_doe_compare(self):
        if self.DOE.num_vars < 2 or self.DOE.num_funcs < 1:
            QMessageBox.critical(
                self.ui.centralwidget,
                "Error",
                "You need at least 2 variables and 1 function for this.",
                QMessageBox.Ok,
            )
            return
        
        x_values = [f"X{x+1}" for x in range(self.DOE.num_vars)]
        y_values = [f"F{y+1}" for y in range(self.DOE.num_funcs)]

        dialog = QDialog(self)
        dialog.setWindowTitle("Sensitivity Analysis Settings")

        layout = QVBoxLayout(dialog)

        label1 = QLabel("X-Axis:")
        x_axis = QComboBox()
        x_axis.addItems(x_values)

        label2 = QLabel("Y-Axis:")
        y_axis = QComboBox()
        y_axis.addItems(y_values)

        label3 = QLabel("X to Compare:")
        comp = QComboBox()
        comp.addItems(x_values)
        comp.setCurrentIndex(1)

        label4 = QLabel("X to Change on Iteration")
        x_to_change = QComboBox()
        x_to_change.addItems(x_values)

        # Add buttons to accept or cancel
        button_layout = QHBoxLayout()
        accept_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")

        # Connect the buttons
        accept_button.clicked.connect(lambda: self.accept_doe_compare(dialog, [x_axis.currentIndex(), y_axis.currentIndex(), comp.currentIndex(), x_to_change.currentIndex()]))
        cancel_button.clicked.connect(dialog.reject)

        # Add widgets to layouts
        button_layout.addWidget(accept_button)
        button_layout.addWidget(cancel_button)

        layout.addWidget(label1)
        layout.addWidget(x_axis)
        layout.addWidget(label2)
        layout.addWidget(y_axis)
        layout.addWidget(label3)
        layout.addWidget(comp)

        if self.DOE.num_vars > 2:
            x_to_change.setCurrentIndex(2)
            layout.addWidget(label4)
            layout.addWidget(x_to_change)
        
        layout.addLayout(button_layout)

        # Show the dialog
        dialog.exec_()
    
    def accept_doe_compare(self, dialog, values: list = []):
        xes = [values[0]] + values[2:]

        if self.DOE.num_vars <= 3:
            if self.DOE.num_vars < 3:
                values.pop(-1)
                xes.pop(-1)
            
            if len(xes) != len(set(xes)):
                QMessageBox.critical(
                    self.ui.centralwidget,
                    "Error",
                    "You cannot use the same X for multiple parts.",
                    QMessageBox.Ok,
                )
                return
            
            self.finish_compare([dialog], values, [])
            return
        
        if len(xes) != len(set(xes)):
            QMessageBox.critical(
                self.ui.centralwidget,
                "Error",
                "You cannot use the same X for multiple parts.",
                QMessageBox.Ok,
            )
            return
        
        remaining = list(range(self.DOE.num_vars))
        for x in xes: remaining.remove(x)

        self.manual_x_values(dialog, remaining, values)

    def manual_x_values(self, _dialog, remaining, _vals):
        dialog = QDialog(self)
        dialog.setWindowTitle("Set X-Values")

        layout = QVBoxLayout(dialog)

        labels, values = [], []
        for r in remaining:
            lab = QLabel(f"Set Value for X{r+1}:")
            val = QComboBox()
            dl = np.linspace(np.float64(self.DOE.var_bounds[r][0]), np.float64(self.DOE.var_bounds[r][1]), self.DOE.num_levels)
            val.addItems([str(s) for s in list(dl)])

            labels.append(lab)
            values.append(val)

        # Add buttons to accept or cancel
        button_layout = QHBoxLayout()
        accept_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")

        # Connect the buttons
        accept_button.clicked.connect(lambda: self.finish_compare([_dialog, dialog], _vals, zip(remaining, values)))
        cancel_button.clicked.connect(dialog.reject)

        # Add widgets to layouts
        button_layout.addWidget(accept_button)
        button_layout.addWidget(cancel_button)

        for l, v in zip(labels, values):
            layout.addWidget(l)
            layout.addWidget(v)
        
        layout.addLayout(button_layout)

        # Show the dialog
        dialog.exec_()
    
    def finish_compare(self, dialogs, vars, values):
        for dialog in dialogs:  # close popups
            dialog.accept()

        graph_dialog = QDialog(self)
        graph_dialog.setWindowTitle("Sensitivity Analysis")
        graph_dialog.resize(1200, 800)  # Set initial size of the dialog

        if self.ui.settings.value("Theme") == "White":
            graph_dialog.setStyleSheet("background-color: #003554;")

        # Create a scroll area
        scroll_area = QScrollArea(graph_dialog)
        scroll_area.setWidgetResizable(True)

        # Create a widget to hold the main layout
        content_widget = QWidget()
        scroll_area.setWidget(content_widget)

        # Create the main layout for the content
        layout = QVBoxLayout(content_widget)
        graph_layout = QGridLayout()

        canvases = []
        toolbars = []

        while len(vars) < 4:
            vars += [-1]
        x_axis, y_axis, x_for_comp, x_to_change = vars

        x_bounds = [np.float64(x) for x in self.DOE.var_bounds[x_axis]]
        x_values = np.linspace(*x_bounds, self.DOE.num_levels)
        
        ### get all the values from the matrix
        # get all bounds as floats
        bounds = [[np.float64(_min), np.float64(_max)] for _min, _max in self.DOE.var_bounds]
        
        # take all the normalized values and convert them to the real values using the bounds
        matrix_values = []
        for row in self.DOE.matrix_vars:
            v = []
            for i, r in enumerate(row):
                v.append(normalize_to_real_value(r, *bounds[i]))
            matrix_values.append(v)

        function_values = [r[y_axis] for r in self.DOE.matrix_funcs]

        # START with [0, 0, ..., 0] for the number of variables and then set the constants to their respective values
        func_xs = [np.float64(0.0) for i in range(self.DOE.num_vars)]
        title_vars = []  # for the graph later
        for n, v in values:
            title_vars.append(f"$X_{n + 1} = {v.currentText()}$")
            func_xs[n] = np.float64(v.currentText())

        xs_to_change_on_iteration = np.linspace(np.float64(self.DOE.var_bounds[x_to_change][0]), np.float64(self.DOE.var_bounds[x_to_change][1]), self.DOE.num_levels) if x_to_change != -1 else []
        for i in range(self.DOE.num_levels):
            x_array = copy(func_xs)

            if len(xs_to_change_on_iteration) > 0:
                x_array[x_to_change] = xs_to_change_on_iteration[i]

            fig = Figure()
            canvas = FigureCanvas(fig)
            toolbar = NavigationToolbar(canvas, graph_dialog)
            if self.ui.settings.value("Theme") == "White":
                # Find the QLabel responsible for the (x, y) coordinates
                for child in toolbar.children():
                    if isinstance(child, QLabel):
                        child.setStyleSheet("color: white;")
            ax = fig.add_subplot(111)

            xs_to_change_for_comparison = np.linspace(np.float64(self.DOE.var_bounds[x_for_comp][0]), np.float64(self.DOE.var_bounds[x_for_comp][1]), self.DOE.num_levels)
            for _x in xs_to_change_for_comparison:
                plot_x, plot_y = [], []
                x_array[x_for_comp] = _x
                for x in x_values:
                    x_array[x_axis] = x
                    for v, f in zip(matrix_values, function_values):
                        if np.array_equal(v, x_array):
                            plot_x.append(x)
                            plot_y.append(f)
                
                ax.plot(np.array(plot_x), np.array(plot_y), label=f"$X_{x_for_comp + 1} = {_x}$", marker='o')
            
            title = [f"$X_{x_to_change + 1} = {xs_to_change_on_iteration[i]}$"] + title_vars if len(xs_to_change_on_iteration) > 0 else ["Graph"]
            ax.set_title(", ".join(title))
            ax.legend()
            
            canvas.setMinimumSize(450, 400)
            toolbar.setMinimumHeight(30)

            ax.set_xlabel(f"$X_{x_axis + 1}$")
            ax.set_ylabel(f"$F_{y_axis + 1}$")

            canvases.append(canvas)
            toolbars.append(toolbar)

            if len(xs_to_change_on_iteration) == 0:
                break
        
        cols = 2 if self.DOE.num_levels <= 4 else 3
        for i, (c, t) in enumerate(zip(canvases, toolbars)):
            graph_layout.addWidget(t, (i // cols) * 2, i % cols)
            graph_layout.addWidget(c, (i // cols) * 2 + 1, i % cols)

        # Add the graph layout to the main layout
        layout.addLayout(graph_layout)

        # Set the scroll area in the dialog
        main_layout = QVBoxLayout(graph_dialog)
        main_layout.addWidget(scroll_area)

        # Show the dialog
        graph_dialog.exec_()

    def handle_mmd_change(self, x):
        """Change the options based on MMD input selections"""
        if x == 0:
            self.ui.mmdFuncCombo.clear()
            self.ui.mmdFuncCombo.addItems(
                [
                    "Linear Polynomial",
                    "Quadratic Polynomial with No Interaction",
                    "Quadratic Polynomial with Interaction",
                ]
            )
            self.ui.mmdOrderCombo.setEnabled(False)
        else:
            self.ui.mmdFuncCombo.clear()
            self.ui.mmdFuncCombo.addItems(
                [
                    "Linear",
                    "Cubic",
                    "Thin Plate Spline",
                    "Gaussian",
                    "Multiquadratic",
                    "Inverse Multiquadratic",
                    "Compactly Supported (2,0)",
                    "Compactly Supported (2,1)",
                    "Compactly Supported (2,2)",
                    "Compactly Supported (3,0)",
                    "Compactly Supported (3,1)",
                    "Compactly Supported (3,2)",
                    "Compactly Supported (3,3)",
                ]
            )
            self.ui.mmdOrderCombo.setEnabled(True)

    def set_taskbar_icons(self):
        """Set the taskbar icons and hover/click actions"""
        # set the icons
        self.openSettings = QAction(
            qta.icon("fa5s.cog", color="white"), "Settings", self.ui.menubar
        )
        self.openSettings.hovered.connect(
            lambda text="Settings": QToolTip.showText(QCursor.pos(), text)
        )
        self.openSettings.triggered.connect(self.open_settings)
        self.ui.menubar.addAction(self.openSettings)  # add this when you have settings ready

        self.openAction = QAction(
            qta.icon("fa5s.folder-open", color="white"), "Open", self.ui.menubar
        )
        self.openAction.setShortcut(QKeySequence(QKeySequence.Open))
        self.openAction.hovered.connect(
            lambda text="Open": QToolTip.showText(QCursor.pos(), text)
        )
        self.openAction.triggered.connect(self.open_file_dialog)
        self.ui.menubar.addAction(self.openAction)

        self.saveAction = QAction(
            qta.icon("fa5s.save", color="white"), "Save", self.ui.menubar
        )
        self.saveAction.setShortcut(QKeySequence(QKeySequence.Save))
        self.saveAction.hovered.connect(
            lambda text="Save": QToolTip.showText(QCursor.pos(), text)
        )
        self.saveAction.triggered.connect(self.save_file_dialog)
        self.ui.menubar.addAction(self.saveAction)

        self.fileAction = QAction(
            qta.icon("fa5s.file", color="white"), "Preview", self.ui.menubar
        )
        self.fileAction.setShortcut(QKeySequence(QKeySequence.Print))
        self.fileAction.hovered.connect(
            lambda text="Preview File": QToolTip.showText(QCursor.pos(), text)
        )
        self.fileAction.triggered.connect(self.preview_file)
        self.ui.menubar.addAction(self.fileAction)

        separator = QAction(" ", self.ui.menubar)
        separator.setEnabled(False)
        self.ui.menubar.addAction(separator)

        self.undoAction = QAction(
            qta.icon("fa5s.undo", color="white"), "Undo", self.ui.menubar
        )
        self.undoAction.setShortcut(QKeySequence(QKeySequence.Undo))
        self.undoAction.hovered.connect(
            lambda text="Undo": QToolTip.showText(QCursor.pos(), text)
        )
        self.undoAction.triggered.connect(self.undo_handler)
        self.ui.menubar.addAction(self.undoAction)

        self.redoAction = QAction(
            qta.icon("fa5s.redo", color="white"), "Redo", self.ui.menubar
        )
        self.redoAction.setShortcut(QKeySequence(QKeySequence.Redo))
        self.redoAction.hovered.connect(
            lambda text="Redo": QToolTip.showText(QCursor.pos(), text)
        )
        self.redoAction.triggered.connect(self.redo_handler)
        self.ui.menubar.addAction(self.redoAction)

        separator = QAction(" ", self.ui.menubar)
        separator.setEnabled(False)
        self.ui.menubar.addAction(separator)

        self.copyAction = QAction(
            qta.icon("fa5s.copy", color="white"), "Copy", self.ui.menubar
        )
        self.copyAction.setShortcut(QKeySequence(QKeySequence.Copy))
        self.copyAction.hovered.connect(
            lambda text="Copy": QToolTip.showText(QCursor.pos(), text)
        )
        self.copyAction.triggered.connect(self.copy_handler)
        self.ui.menubar.addAction(self.copyAction)

        self.pasteAction = QAction(
            qta.icon("fa5s.paste", color="white"), "Paste", self.ui.menubar
        )
        self.pasteAction.setShortcut(QKeySequence(QKeySequence.Paste))
        self.pasteAction.hovered.connect(
            lambda text="Paste": QToolTip.showText(QCursor.pos(), text)
        )
        self.pasteAction.triggered.connect(self.paste_handler)
        self.ui.menubar.addAction(self.pasteAction)

        self.cutAction = QAction(
            qta.icon("fa5s.cut", color="white"), "Cut", self.ui.menubar
        )
        self.cutAction.setShortcut(QKeySequence(QKeySequence.Cut))
        self.cutAction.hovered.connect(
            lambda text="Cut": QToolTip.showText(QCursor.pos(), text)
        )
        self.cutAction.triggered.connect(self.cut_handler)
        self.ui.menubar.addAction(self.cutAction)

        self.rightMenu = QMenuBar(self.ui.menubar)
        self.infoAction = QAction(
            qta.icon("fa5s.info-circle", color="white"), "About", self.rightMenu
        )
        self.infoAction.triggered.connect(self.show_about_popup)
        self.infoAction.hovered.connect(
            lambda text="About": QToolTip.showText(
                QCursor.pos(), text
            )
        )
        self.rightMenu.addAction(self.infoAction)

        self.aboutAction = QAction(
            qta.icon("fa5s.question-circle", color="white"), "Help", self.rightMenu
        )
        self.aboutAction.triggered.connect(self.show_help_popup)
        self.aboutAction.hovered.connect(
            lambda text="Help": QToolTip.showText(QCursor.pos(), text)
        )
        self.rightMenu.addAction(self.aboutAction)

        self.bugAction = QAction(
            qta.icon("fa5s.bug", color="white"), "Report Bug", self.rightMenu
        )
        self.bugAction.triggered.connect(self.bug_report)
        self.bugAction.hovered.connect(
            lambda text="Report bug": QToolTip.showText(QCursor.pos(), text)
        )
        self.rightMenu.addAction(self.bugAction)

        self.ui.menubar.setCornerWidget(self.rightMenu)

        self.setWindowIcon(QIcon(resource_path("PyPROE.ico")))
        # Set the taskbar icon
        # https://stackoverflow.com/questions/67599432/setting-the-same-icon-as-application-icon-in-task-bar-for-pyqt5-application
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "PyPROE.v1"
        )
    
    def create_info_popup(self, title: str, html_content: str, icon: QIcon=None):
        # Create a QDialog as a popup
        popup = QDialog()
        popup.setWindowTitle(title)
        popup.setWindowIcon(icon if icon is not None else QIcon(resource_path("PyPROE.ico")))

        # Create a QWebEngineView for displaying HTML content
        text_browser = QWebEngineView()
        text_browser.setHtml(html_content)

        # Create a search bar
        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Search...")

        # Create search buttons
        search_button = QPushButton("Search")
        next_button = QPushButton("Next")
        previous_button = QPushButton("Previous")

        # Variable to track the current search term
        current_term = {"text": ""}

        # Connect search functionality
        def perform_search():
            term = search_bar.text().strip()
            if term:
                current_term["text"] = term
                text_browser.findText(term, QWebEnginePage.FindFlag(0))  # Initial search

        def find_next():
            if current_term["text"]:
                text_browser.findText(current_term["text"], QWebEnginePage.FindFlag(0))

        def find_previous():
            if current_term["text"]:
                text_browser.findText(current_term["text"], QWebEnginePage.FindFlag.FindBackward)

        search_button.clicked.connect(perform_search)
        next_button.clicked.connect(find_next)
        previous_button.clicked.connect(find_previous)

        # Layout for search bar and buttons
        search_layout = QHBoxLayout()
        search_layout.addWidget(search_bar)
        search_layout.addWidget(search_button)
        search_layout.addWidget(previous_button)
        search_layout.addWidget(next_button)

        # Add everything to the main layout
        layout = QVBoxLayout()
        layout.addLayout(search_layout)
        layout.addWidget(text_browser)
        popup.setLayout(layout)

        # Set the size of the popup
        popup.resize(1200, 800)

        # Center the dialog on the screen
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - popup.width()) // 2
        y = (screen_geometry.height() - popup.height()) // 2
        popup.move(x, y)

        # Show the dialog and keep it open until the user closes it
        popup.show()

        return popup

    def show_about_popup(self):
        # Set HTML content with custom CSS
        with open(resource_path("html/about.html"), "r") as file:
            html_content = file.read()

        self.about_popup = self.create_info_popup('About', html_content)
    
    def show_help_popup(self):
        # Set HTML content with custom CSS
        with open(resource_path("html/help.html"), "r") as file:
            html_content = file.read()

        self.help_popup = self.create_info_popup('Help', html_content)
    
    def bug_report(self):
        url = QUrl("https://forms.gle/q2L2zdpP2uXHLhHj6")

        QDesktopServices.openUrl(url)

    def open_file_dialog(self):
        """Open a dialog for the user to choose a file from"""
        self.openFile = QFileDialog(
            self.ui.centralwidget,
            self.open_file_title,
            self.ui.settings.value("RecentOpenDir"),
            self.open_file_ext_desc,
        )
        self.openFile.setFileMode(QFileDialog.ExistingFile)
        self.openFile.setAcceptMode(QFileDialog.AcceptOpen)

        if self.openFile.exec():
            self.open_file_name = self.openFile.selectedFiles()[0]
            self.ui.settings.setValue(
                "RecentOpenDir", f'{self.open_file_name}'  # I removed .split(".")[0] from this because it was making me have to re-select the file every time
            )

            current_index = self.ui.stackedWidget.currentIndex()

            self.open_files[ current_index ] = self.open_file_name

            match current_index:
                case 0:
                    self.DOE.doe_file_reader(self.open_file_name)
                    self.update_doe_table(self.DOE.num_vars)
                case 1:
                    self.ui.mmdFileLabel.setText(
                        f"Reading {self.open_file_name.split('/')[-1]}"
                    )
                    self.MMD.read_design_file(self.open_file_name)
                case 2:
                    self.ui.optFileLabel.setText(
                        f"Reading {self.open_file_name.split('/')[-1]}"
                    )
                case 3:
                    with open(self.open_file_name) as f:
                        self.ui.wrtEdit.setPlainText(f.read())
                case 4:
                    if self.FML.fnc_file_reader(self.open_file_name) == -1:
                        QMessageBox.critical(
                            self.ui.centralwidget,
                            "Error",
                            "There was an error reading the selected file.",
                            QMessageBox.Ok,
                        )
                    else:
                        self.OPT.result_file_is_str = False
                case 5:
                    self.ui.plotFileLabel.setText(
                        f"Reading {self.open_file_name.split('/')[-1]}"
                    )
                case 6:
                    try:
                        with open(self.open_file_name, 'r', encoding='utf-8') as file:
                            content = file.read()
                            self.ui.gradientOutput.setPlainText(content)
                    except FileNotFoundError:
                        self.ui.gradientOutput.setPlainText("Error: File not found.")
                    except IOError as e:
                        self.ui.gradientOutput.setPlainText(f"Error: {e}")
                    except Exception as e:
                        self.ui.gradientOutput.setPlainText(f"An unexpected error occurred: {e}")
                        
    def save_file_dialog(self):
        """Open a dialog for the user to choose a save directory"""
        self.saveFile = QFileDialog(
            self.ui.centralwidget,
            self.save_file_title,
            self.ui.settings.value("RecentSaveDir"),
            self.save_file_ext_desc,
        )
        self.saveFile.setFileMode(QFileDialog.AnyFile)
        self.saveFile.setAcceptMode(QFileDialog.AcceptSave)

        if self.saveFile.exec():
            self.save_file_name = self.saveFile.selectedFiles()[0]
            self.ui.settings.setValue(
                "RecentSaveDir", f'{self.save_file_name.split(".")[0]}'
            )

            with open(
                f'{self.save_file_name.split(".")[0]}.{self.save_file_name.split(".")[1] if len(self.save_file_name) > 1 else self.save_file_ext[0]}',
                "w",
            ) as file:
                if self.ui.stackedWidget.currentIndex() == 0:
                    file.write(self.DOE.display_des_matrix())
                elif self.ui.stackedWidget.currentIndex() == 1:
                    file.write(self.MMD.mmd_full_func_file_str())
                elif self.ui.stackedWidget.currentIndex() == 4:
                    file.write(self.FML.get_file_str())
                elif self.ui.stackedWidget.currentIndex() == 6:
                    file.write(self.GRAD.gen_file())
                else:
                    file.write(self.textOutput.document().toPlainText())

    def cut_handler(self):
        """Cut the text from the current text output object"""
        self.textOutput.cut()

    def copy_handler(self):
        """Copy the text from the current text output object"""
        self.textOutput.copy()

    def paste_handler(self):
        """Paste the text from the current text output object"""
        self.textOutput.paste()

    def delete_handler(self):
        """Clear the text from the current text output object"""
        self.textOutput.clear()

    def undo_handler(self):
        """Undo the previous action on the current text output object"""
        self.textOutput.undo()

    def redo_handler(self):
        """Redo the previous action on the current text output object"""
        self.textOutput.redo()

    def about_to_close(self):
        """Remember the user's last opened tab and attach removed components"""
        self.ui.settings.setValue("Tab", self.ui.stackedWidget.currentIndex())
        self.ui.population_lay_2.setParent(self.ui.centralwidget)
        self.ui.weights_lay_2.setParent(self.ui.centralwidget)
        self.ui.inner_lay_2.setParent(self.ui.centralwidget)
        self.ui.outer_lay_2.setParent(self.ui.centralwidget)
        self.ui.crossover_lay_2.setParent(self.ui.centralwidget)
        self.ui.mutation_lay_2.setParent(self.ui.centralwidget)
        self.ui.grid_lay_2.setParent(self.ui.centralwidget)
        self.ui.weight_increment_widget.setParent(self.ui.centralwidget)

    def mmd_data_status_change(self, hasData: bool):
        """Enable/Disable MMD function evaluation buttons"""
        enable = True if hasData else False
        self.ui.funcValBtn.setEnabled(enable)
        self.ui.oneFuncBtn.setEnabled(enable)

    def handle_error(self, message: str):
        QMessageBox.critical(
            self.ui.centralwidget,
            "Error",
            str(message),
            QMessageBox.Ok,
        )
    
    def open_settings(self):
        # Create a QDialog as a popup
        popup = QDialog()
        popup.setWindowTitle("Settings")
        popup.setWindowIcon(QIcon(resource_path("PyPROE.ico")))

        popup.setFixedWidth(300)

        # Apply a stylesheet to the popup
        popup.setStyleSheet("""
            QDialog {
                background-color: #2E3440;  /* Dark background */
                color: #D8DEE9;  /* Light text color */
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #ECEFF4;
            }
            QComboBox {
                font-size: 12px;
                color: #ECEFF4;
                background-color: #3B4252;
                border: 1px solid #4C566A;
                padding: 4px;
                border-radius: 4px;
            }
            QPushButton {
                font-size: 12px;
                color: #ECEFF4;
                background-color: #5E81AC;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #81A1C1;  /* Lighter blue on hover */
            }
            QPushButton:pressed {
                background-color: #4C566A;  /* Darker blue on press */
            }
        """)

        # Layout for the dialog
        layout = QVBoxLayout()

        # Dropdown for themes
        layout.addWidget(QLabel("Select Theme:"))
        theme_dropdown = QComboBox()
        themes = list(PALETTES)  # Example themes
        theme_dropdown.addItems(themes)
        layout.addWidget(theme_dropdown)
        theme_dropdown.setCurrentIndex(themes.index(self.ui.settings.value("Theme")))

        color_label = QLabel("Select Color:")
        color_drop = QComboBox()
        color_drop.addItems(list(NEON_COLORS))
        layout.addWidget(color_label)
        layout.addWidget(color_drop)

        white_label = QLabel("Version:")
        white_drop = QComboBox()
        white_drop.addItems(["Default", "Simplified"])
        layout.addWidget(white_label)
        layout.addWidget(white_drop)

        if "White" not in self.ui.settings.value("Theme") and "Dark" not in self.ui.settings.value("Theme"):
            white_label.hide()
            white_drop.hide()
        elif self.ui.settings.value("ThemeColor") in ["Default", "Simplified"]:
            white_drop.setCurrentIndex(["Default", "Simplified"].index(self.ui.settings.value("ThemeColor")))

        if "Neon" not in self.ui.settings.value("Theme"):
            color_label.hide()
            color_drop.hide()
        elif self.ui.settings.value("ThemeColor") in list(NEON_COLORS):
            color_drop.setCurrentIndex(list(NEON_COLORS).index(self.ui.settings.value("ThemeColor")))

        # Connect dropdown change event
        def on_theme_change():
            selected_theme = theme_dropdown.currentText()
            self.ui.settings.setValue("Theme", selected_theme)
            self.ui.settings.setValue("ThemeColor", color_drop.currentText() if selected_theme == "Neon" else white_drop.currentText() if selected_theme in ["White", "Dark"] else "")
            self.set_themes()
            if "White" in selected_theme or "Dark" in selected_theme:
                white_label.show()
                white_drop.show()
            else:
                white_label.hide()
                white_drop.hide()   

            if "Neon" in selected_theme:
                color_label.show()
                color_drop.show()
            else:
                color_label.hide()
                color_drop.hide()

        theme_dropdown.currentIndexChanged.connect(on_theme_change)
        color_drop.currentIndexChanged.connect(on_theme_change)
        white_drop.currentIndexChanged.connect(on_theme_change)

        # Horizontal layout for label and checkbox
        clear_confirm_layout = QHBoxLayout()
        label = QLabel("Confirm before clearing data: ")
        label.setToolTip("If checked, attempting to clear data will prompt the user to confirm before clearing any data.")
        clear_confirm = QCheckBox()
        clear_confirm.setChecked(self.ui.settings.value("ClearConfirm") == 'true')  # Set initial state

        # Add label and checkbox to the horizontal layout
        clear_confirm_layout.addWidget(label)
        clear_confirm_layout.addWidget(clear_confirm)

        # Add horizontal layout to the main layout
        layout.addLayout(clear_confirm_layout)

        def clear_confirm_change():
            self.ui.settings.setValue("ClearConfirm", clear_confirm.isChecked())

        # Connect the checkbox state change to a slot
        clear_confirm.stateChanged.connect(clear_confirm_change)

        # Horizontal layout for label and checkbox
        mmd_replace_layout = QHBoxLayout()
        label = QLabel("Replace MMD functions in Formulation: ")
        label.setToolTip("If checked, sending function from Metamodeling will replace the MMD functions in Formuation. If unchecked, sending functions will add more functions in Formulation.")
        mmd_replace = QCheckBox()
        mmd_replace.setChecked(self.ui.settings.value("ReplaceMMD") == 'true')  # Set initial state

        # Add label and checkbox to the horizontal layout
        mmd_replace_layout.addWidget(label)
        mmd_replace_layout.addWidget(mmd_replace)

        # Add horizontal layout to the main layout
        layout.addLayout(mmd_replace_layout)

        def mmd_replace_change():
            self.ui.settings.setValue("ReplaceMMD", mmd_replace.isChecked())

        # Connect the checkbox state change to a slot
        mmd_replace.stateChanged.connect(mmd_replace_change)

        # Close button
        close_button = QPushButton("Close")
        layout.addWidget(close_button)

        # Close dialog on button click
        close_button.clicked.connect(popup.accept)

        # Set the layout
        popup.setLayout(layout)

        # add CTRL+W
        close_shortcut = QShortcut(QKeySequence("Ctrl+W"), popup)
        close_shortcut.activated.connect(popup.accept)

        # Show the popup
        popup.exec()

    def move_tab_left(self):
        order = [0, 1, 4, 2, 5, 6, 3]
        i = order.index(self.ui.stackedWidget.currentIndex())
        self.ui.stackedWidget.setCurrentIndex(order[i - 1])
        self.setup_tab_handlers()

    def move_tab_right(self):
        order = [0, 1, 4, 2, 5, 6, 3]
        i = order.index(self.ui.stackedWidget.currentIndex())
        self.ui.stackedWidget.setCurrentIndex(order[(i + 1) % len(order)])
        self.setup_tab_handlers()
    
    def change_tab(self, tab: int):
        self.ui.stackedWidget.setCurrentIndex(tab)
        self.setup_tab_handlers()
    
    def close_application(self):
        QApplication.instance().quit()
    
    def advanced_mode(self):
        self.ui.tabEditBtn.hide() if self.in_advanced_mode else self.ui.tabEditBtn.show()
        self.in_advanced_mode ^= True  # flips the boolean value
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        # Update font size based on the new window height
        self.update_tab_sizes()
        
        # update the size of the open file buttons so that the other buttons automatically scale correctly
        w = int(self.width() * (223 / 800))
        self.ui.openDoeFile.setFixedWidth(w)
        self.ui.mmdDoeButton.setFixedWidth(w)
        self.ui.optFncBtn.setFixedWidth(w)
        self.ui.form_load_file.setFixedWidth(w)
        self.ui.plotOpenFile.setFixedWidth(w)
        self.ui.gradientOpenFile.setFixedWidth(w)

        self.set_themes()

    def update_tab_sizes(self):
        # Calculate the font size as a percentage of the window height
        font_size = max(10, int(self.height() * 0.018))  # 1.8% of the window height

        style = f"font-size: {font_size}px;"

        for btn in [self.ui.tabEditBtn, self.ui.tabFormulationBtn, self.ui.tabGradientBtn, self.ui.tabMMDBtn, self.ui.tabMatpltBtn, self.ui.tabOptBtn, self.ui.tabWriterBtn]:
            btn.setStyleSheet(style)
    
    def toggle_fullscreen(self):
        self.showNormal() if self.is_fullscreen else self.showFullScreen()
        self.is_fullscreen ^= True
    
    def disable_fullscreen(self):
        self.showNormal()
        self.is_fullscreen = False
    
    def submit(self):
        if self.ui.stackedWidget.currentIndex() == 2:  # optimization tab
            self.opt_start()

    def kon_check(self, key):
        self.pressed_keys.append(key)
        if len(self.pressed_keys) > 11:
            self.pressed_keys.pop(0)

        if self.pressed_keys == list("uuddlrlrbae"):
            print("YOU WIN!!")
    
    def set_themes(self):
        theme = self.ui.settings.value("Theme")
        color = self.ui.settings.value("ThemeColor")

        width = self.width()

        def map_value(x, x_min=922, x_max=1920, y_min=12, y_max=20):
            return ((x - x_min) * (y_max - y_min)) / (x_max - x_min) + y_min
        
        sizes = {
            "ButtonSize": map_value(width), 
            "LabelSize": map_value(width), 
            "BoxSize": map_value(width), 
            "TextEditSize": map_value(width)
        }

        self.setStyleSheet(load_stylesheet(palette=theme, color=color, sizes=sizes))
        self.update_icon_color(color=ICON_COLORS.get(theme if theme != "Neon" else f"Neon {color}", "white"))
    
    def cycle_theme(self):
        themes = list(PALETTES)
        theme = self.ui.settings.value("Theme")

        i = themes.index(theme)
        theme = themes[(i + 1) % len(themes)]
        self.ui.settings.setValue("Theme", theme)
        self.set_themes()

    def update_icon_color(self, color="white", size: int=16):
        """Set the taskbar icons and hover/click actions"""
        self.openSettings.setIcon(
            qta.icon("fa5s.cog", color=color, size=size)
        )
        self.openAction.setIcon(
            qta.icon("fa5s.folder-open", color=color, size=size)
        )
        self.saveAction.setIcon(
            qta.icon("fa5s.save", color=color, size=size)
        )
        self.fileAction.setIcon(
            qta.icon("fa5s.file", color=color, size=size)
        )
        self.undoAction.setIcon(
            qta.icon("fa5s.undo", color=color, size=size)
        )
        self.redoAction.setIcon(
            qta.icon("fa5s.redo", color=color, size=size)
        )
        self.copyAction.setIcon(
            qta.icon("fa5s.copy", color=color, size=size)
        )
        self.pasteAction.setIcon(
            qta.icon("fa5s.paste", color=color, size=size)
        )
        self.cutAction.setIcon(
            qta.icon("fa5s.cut", color=color, size=size)
        )
        self.infoAction.setIcon(
            qta.icon("fa5s.info-circle", color=color, size=size)
        )
        self.aboutAction.setIcon(
            qta.icon("fa5s.question-circle", color=color, size=size)
        )
        self.bugAction.setIcon(
            qta.icon("fa5s.bug", color=color, size=size)
        )

    def closeEvent(self, event):
        # Check if the process is running when closing the window
        if self.OPT.process and self.OPT.process.is_alive():
            self.OPT.process.terminate()  # Terminate the process if still running
            self.OPT.process.join()  # Wait for the process to fully terminate
        event.accept()  # Allow the window to close after process is terminated


# https://gis.stackexchange.com/questions/350148/qcombobox-multiple-selection-pyqt5
