from PySide6.QtWidgets import (
    QApplication, QFileDialog, QWidget, QHBoxLayout, QVBoxLayout
)
from PySide6.QtGui import QIcon, QKeySequence, QAction, QShortcut
from PySide6.QtCore import Qt, QSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from qfluentwidgets import (
    FluentWindow, setTheme, setThemeColor, Theme, CommandBar, Action, FluentTitleBar, PushButton, FlyoutView,
    NavigationPushButton, LineEdit, PrimaryPushButton, ToolButton, NavigationItemPosition, FluentIcon as FI
)

from sections.designofexperiments import DesignOfExperimentsPage
from sections.optimization import OptimizationPage
from sections.formulation import FormulationPage
from sections.metamodeling import MetamodelPage
from sections.settingspage import SettingsPage, is_valid_hex_color
from sections.mainpage import MainPage

from testing.inputfnc2 import InputFile
from stylesheet.accents import ACCENT_COLORS

from components.helppopup import DocumentationPopup

import sys, ctypes


class App(FluentWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PyPROE X")
        self.setWindowIcon(QIcon("assets/pyproe-logo.png"))
        if sys.platform == "win32": ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PyPROE X.v0")
        self.resize(1400, 900)
        self.showMaximized()

        # --- SETTINGS ---
        self.settings = QSettings("PyPROE", "PyPROE App")
        self.set_app_theme()

        # --- PAGES ---
        self.frm = FormulationPage(self)
        self.doe = DesignOfExperimentsPage()
        self.mmd = MetamodelPage()
        self.opt = OptimizationPage()
        self.page_settings = SettingsPage(self.trigger_theme_change)
        self.main_page = MainPage(formpage=self.frm, doepage=self.doe, metapage=self.mmd, optpage=self.opt)

        # Connect Optimization
        self.opt.start.pressed.connect(self._start_opt)

        # --- NAVIGATION ---
        self.init_navigation()

        # --- MENU & SHORTCUTS ---
        self.init_shortcuts()

    def init_navigation(self):
        """ Correct way to add sub-pages in FluentWindow """
        open_btn = NavigationPushButton(FI.FOLDER_ADD, "Open File", isSelectable=False)
        save_btn = NavigationPushButton(FI.SAVE_AS, "Save File", isSelectable=False)
        open_btn.clicked.connect(self._open_file)
        save_btn.clicked.connect(self._save_file)
        self.navigationInterface.addWidget(
            routeKey="open-file",
            widget=open_btn
        )
        self.navigationInterface.addWidget(
            routeKey="save-file",
            widget=save_btn
        )
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.main_page, FI.HOME, "Main")
        self.navigationInterface.addSeparator()
        self.navigationInterface.addSeparator(position=NavigationItemPosition.BOTTOM)
        self.navigationInterface.addItem(
            routeKey="show-help",
            icon=FI.QUESTION,
            text="View Documentation",
            onClick=self.show_documentation,
            position=NavigationItemPosition.BOTTOM,
        )
        self.addSubInterface(self.page_settings, FI.SETTING, "Settings", NavigationItemPosition.BOTTOM)

    # Shortcuts / Menus
    def init_shortcuts(self):
        QApplication.instance().quit()
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self._close_application)
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self._open_file)

    # Functional Logic
    def _close_application(self):
        # Close threaded optimization process if running
        p = self.opt.process
        if p and p.is_alive():
            p.terminate()
            p.join()

        QApplication.instance().quit()

    def _open_file(self):
        dlg = QFileDialog(self,
                          "Open File",
                          self.settings.value("previous_open_file_dir"),
                          "Optimization function files (*.fnc)")

        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setAcceptMode(QFileDialog.AcceptOpen)

        if dlg.exec():
            filename = dlg.selectedFiles()[0]
            self.settings.setValue('previous_open_file_dir', filename)

            if filename.endswith(".fnc"):
                self.frm.load_from_file(file_path=filename)
    
    def _save_file(self):
        saveFile = QFileDialog(
            self,
            "Save File",
            self.settings.value("previous_open_file_dir"),
            "Optimization function files (*.fnc)"
        )
        saveFile.setFileMode(QFileDialog.AnyFile)
        saveFile.setAcceptMode(QFileDialog.AcceptSave)

        if saveFile.exec():
            with open(saveFile.selectedFiles()[0], 'w') as file:
                file.write(self.frm.convert_to_fnc())

    def _start_opt(self):
        fnc = self.frm.convert_to_fnc()

        file = InputFile(fnc, is_file=False)
        if file.error:
            print(f"ERROR: {file.error_message}")
            return

        self.opt._solve(fnc)

    def show_documentation(self):
        popup = DocumentationPopup(self)
        popup.exec()
    
    def set_app_theme(self):
        setTheme(Theme.DARK if self.settings.value("theme") == "Dark" else Theme.LIGHT)

        if self.settings.value("accent") == "Custom":
            valid = is_valid_hex_color(self.settings.value("custom_accent"))

            if valid:
                setThemeColor(self.settings.value("custom_accent"))
                return
            
            setThemeColor("#000000")
            return

        setThemeColor(ACCENT_COLORS.get(self.settings.value("accent"), ACCENT_COLORS.get("Red")))

    def trigger_theme_change(self):
        self.doe.table.on_selection_changed()
