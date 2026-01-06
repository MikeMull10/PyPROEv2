from PySide6.QtWidgets import QApplication, QFileDialog
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtCore import Qt, QSettings
from qfluentwidgets import (
    FluentWindow, setTheme, setThemeColor, Theme, theme,
    NavigationPushButton, NavigationItemPosition, FluentIcon as FI
)

from sections.designofexperiments import DesignOfExperimentsPage
from sections.optimization import OptimizationPage
from sections.formulation import FormulationPage
from sections.metamodeling import MetamodelPage
from sections.settingspage import SettingsPage, is_valid_hex_color
from sections.mainpage import MainPage
from sections.plotting import PlottingPage, GraphIcon

from components.inputfnc2 import InputFile
from stylesheet.accents import ACCENT_COLORS

from components.helppopup import DocumentationPopup
from components.savetypepopup import SavePopup, SaveType
from components.basicpopup import BasicPopup
from fixpath import app_root

import sys, ctypes, traceback


class App(FluentWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PyPROE X")
        self.setWindowIcon(QIcon((app_root() / "assets" / "logo.png").as_posix()))
        if sys.platform == "win32": ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PyPROE X.v0")
        self.resize(1400, 900)
        self.showMaximized()

        self.version = "0.0.0"

        # --- SETTINGS ---
        self.page_settings = SettingsPage(self.trigger_theme_change)
        self.settings = QSettings("PyPROE", "PyPROE App")
        self.set_app_theme()

        # --- PAGES ---
        self.frm = FormulationPage(parent=self)
        self.doe = DesignOfExperimentsPage(parent=self)
        self.mmd = MetamodelPage(parent=self, doe_table=self.doe.table)
        self.opt = OptimizationPage(self.frm)
        self.main_page = MainPage(formpage=self.frm, doepage=self.doe, metapage=self.mmd, optpage=self.opt)
        self.plotting = PlottingPage(parent=self)

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
        self.addSubInterface(self.plotting, GraphIcon(), "Plotting")
        self.navigationInterface.addSeparator()
        self.navigationInterface.addSeparator(position=NavigationItemPosition.BOTTOM)
        view_documentation = NavigationPushButton(FI.QUESTION, "View Documentation", isSelectable=False)
        view_documentation.clicked.connect(self.show_documentation)
        self.navigationInterface.addWidget(
            routeKey="show-help",
            widget=view_documentation,
            position=NavigationItemPosition.BOTTOM,
        )
        self.addSubInterface(self.page_settings, FI.SETTING, "Settings", NavigationItemPosition.BOTTOM)

        # --- Change Cursor on Hover ---
        open_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setCursor(Qt.PointingHandCursor)
        self.navigationInterface.setCursor(Qt.PointingHandCursor)

    def init_shortcuts(self):
        QApplication.instance().quit()
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self._close_application)
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self._open_file)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self._save_file)
        QShortcut(QKeySequence("Ctrl+1"), self, activated=lambda: self.switch_to_page(self.main_page))
        QShortcut(QKeySequence("Ctrl+2"), self, activated=lambda: self.switch_to_page(self.plotting))

    def _close_application(self):
        p = self.opt.process
        if p and p.is_alive():
            p.terminate()
            p.join()

        QApplication.instance().quit()

    def _open_file(self):
        dlg = QFileDialog(self,
                          "Open File",
                          self.settings.value("previous_open_file_dir"),
                          "Supported files (*.doe *.fnc);;Optimization function files (*.fnc);;Design of experiment files (*.doe)")

        dlg.setFileMode(QFileDialog.ExistingFile)
        dlg.setAcceptMode(QFileDialog.AcceptOpen)
        
        if dlg.exec():
            try:
                filename = dlg.selectedFiles()[0]
                self.settings.setValue('previous_open_file_dir', filename)

                if filename.endswith(".fnc"):
                    if self.stackedWidget.currentIndex() == 0:
                        self.frm.load_from_file(file_path=filename)
                    elif self.stackedWidget.currentIndex() == 1:
                        self.plotting.formpage.load_from_file(file_path=filename)
                
                elif filename.endswith(".doe"):
                    self.doe.load_from_file(file_path=filename)

                else:
                    pop = BasicPopup(self, "Unknown File Extension", f".{filename.split('.')[1]} extension is unknown. Please use .doe for a Design of Experiment file and .fnc for Forumation file.")
                    pop.exec()
            except Exception as e:
                pop = BasicPopup(self, "ERROR", f"{e}\n\n{traceback.format_exc()}")
                pop.exec()
    
    def _save_file(self):
        save_type: SaveType | None = None
        # --- Both DOE Table and Formulation are empty ---
        if self.doe.is_empty() and self.frm.is_empty():
            pop = BasicPopup(parent=self, title="Nothing to Save", message="There is nothing to save. Please put data into the DOE Table or Formulation Section.")
            pop.exec()
            return
        # --- Only DOE TABLE is empty, so Formulation should be saved ---
        elif self.doe.is_empty():
            save_type = SaveType.FNC
        # --- Only Formulation is empty, so the DOE Table should be saved ---
        elif self.frm.is_empty():
            save_type = SaveType.DOE
        # --- Both are filled, so ask user which one they want to save ---
        else:
            pop = SavePopup(parent=self)
            ok, save_type = pop.exec()
            if not ok: return

        saveFile = QFileDialog(
            self,
            "Save File",
            self.settings.value("previous_open_file_dir"),
            "Optimization function files (*.fnc)" if save_type == SaveType.FNC else "Design of experiment files (*.doe)"
        )
        saveFile.setFileMode(QFileDialog.AnyFile)
        saveFile.setAcceptMode(QFileDialog.AcceptSave)

        if saveFile.exec():
            with open(saveFile.selectedFiles()[0], 'w') as file:
                file.write(self.frm.convert_to_fnc() if save_type == SaveType.FNC else self.doe.save_to_file())

    def _start_opt(self):
        fnc = self.frm.convert_to_fnc()

        file = InputFile(fnc, is_file=False)
        if file.error:
            pop = BasicPopup(self, title="ERROR", message=f"Error with Formulation: {file.error_message}")
            pop.exec()
            return

        self.opt._solve(fnc)

    def show_documentation(self) -> None:
        try:
            popup = DocumentationPopup(self)
            popup.exec()
        except Exception as e:
            pop = BasicPopup(self, "ERROR", f"{e}\n\n{traceback.format_exc()}\n\n{app_root()}\n\n{getattr(sys, "frozen", False)}\n\n{getattr(sys, "frozen", False) != False}")
            pop.exec()
    
    def set_app_theme(self) -> None:
        setTheme(Theme.DARK if self.settings.value("theme") == "Dark" else Theme.LIGHT)

        if self.settings.value("accent") == "Custom":
            valid = is_valid_hex_color(self.settings.value("custom_accent"))

            if valid:
                setThemeColor(self.settings.value("custom_accent"))
                return
            
            setThemeColor("#000000")
            return

        setThemeColor(ACCENT_COLORS.get(self.settings.value("accent"), ACCENT_COLORS.get("Red")))

    def trigger_theme_change(self) -> None:
        self.doe.table.on_selection_changed()
        self.frm.divider.style = theme()
        self.frm.divider.update_style()
    
    def switch_to_page(self, page_widget):
        self.stackedWidget.setCurrentWidget(page_widget)
