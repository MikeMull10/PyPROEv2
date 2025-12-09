from PySide6.QtWidgets import (
    QApplication, QFileDialog, QWidget, QHBoxLayout, QVBoxLayout
)
from PySide6.QtGui import QIcon, QKeySequence, QAction, QShortcut
from PySide6.QtCore import Qt, QSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from qfluentwidgets import (
    FluentWindow, setTheme, setThemeColor, Theme, CommandBar, Action, FluentTitleBar, PushButton, FlyoutView,
    Dialog, LineEdit, PrimaryPushButton, ToolButton, NavigationItemPosition, FluentIcon as FI
)

from sections.designofexperiments import DesignOfExperimentsPage
from sections.optimization import OptimizationPage
from sections.formulation import FormulationPage
from sections.metamodelling import MetamodelPage
from sections.settingspage import SettingsPage
from sections.mainpage import MainPage

from testing.inputfnc2 import InputFile
from stylesheet.accents import ACCENT_COLORS


class App(FluentWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PyPROE X")
        self.setWindowIcon(QIcon("assets/pyproe-logo.png"))
        self.resize(1400, 900)
        self.showMaximized()

        # --- SETTINGS ---
        self.settings = QSettings("PyPROE", "PyPROE App")
        setTheme(Theme.DARK if self.settings.value("theme") == "Dark" else Theme.LIGHT)
        setThemeColor(ACCENT_COLORS.get(self.settings.value("accent"), ACCENT_COLORS.get("Red")))

        # --- PAGES ---
        self.frm = FormulationPage(self)
        self.doe = DesignOfExperimentsPage()
        self.mmd = MetamodelPage()
        self.opt = OptimizationPage()
        self.page_settings = SettingsPage()
        self.main_page = MainPage(formpage=self.frm, doepage=self.doe, metapage=self.mmd, optpage=self.opt)

        # Connect Optimization
        self.opt.start.pressed.connect(self._start_opt)

        # --- NAVIGATION ---
        self.init_navigation()

        # --- MENU & SHORTCUTS ---
        self.init_shortcuts()

    def init_navigation(self):
        """ Correct way to add sub-pages in FluentWindow """
        self.navigationInterface.addItem(
            routeKey="open-file",
            icon=FI.FOLDER_ADD,
            text="Open File",
            onClick=self._open_file
        )
        self.navigationInterface.addItem(
            routeKey="save-file",
            icon=FI.SAVE_AS,
            text="Save File",
            onClick=self._save_file
        )
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.main_page, FI.HOME, "Main")
        # self.addSubInterface(self.frm, FI.EDIT, "Formulation")
        # self.addSubInterface(self.doe, FI.APPLICATION, "DOE")
        # self.addSubInterface(self.mmd, FI.HOME, "Metamodeling")
        # self.addSubInterface(self.opt, FI.GAME, "Optimization")
        self.navigationInterface.addSeparator()
        self.navigationInterface.addItem(
            routeKey="show-help",
            icon=FI.QUESTION,
            text="View Documentation",
            onClick=self.create_help_popup
        )
        self.addSubInterface(self.page_settings, FI.SETTING, "Settings", NavigationItemPosition.BOTTOM)

    # Shortcuts / Menus
    def init_shortcuts(self):
        QApplication.instance().quit()
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.close_application)
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self._open_file)

    # Functional Logic
    def close_application(self):
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
        ...

    def _start_opt(self):
        fnc = self.frm.layout.toPlainText()

        file = InputFile(fnc, is_file=False)
        if file.error:
            print(f"ERROR: {file.error_message}")
            return

        self.opt._solve(fnc)

    def create_help_popup(self):
        # --- QFluent Dialog ---
        view = FlyoutView(
            title='PyPROE Documentation',
            content="",
            isClosable=True
        )
        popup = Dialog(self)
        popup.setWindowTitle("PyPROE Documentation")

        popup.resize(1200, 800)
        popup.showFullScreen()

        # --- WebEngineView ---
        with open("html/help.html", "r") as file:
            html_content = file.read()

        web = QWebEngineView()
        web.setHtml(html_content)

        # --- Search Bar (QFluent LineEdit) ---
        search_bar = LineEdit()
        search_bar.setPlaceholderText("Search...")

        # --- Fluent Buttons ---
        search_btn = PrimaryPushButton("Search", FI.SEARCH)
        next_btn   = ToolButton(FI.CARET_RIGHT)
        prev_btn   = ToolButton(FI.CARET_LEFT)

        # Track last search
        current_term = {"text": ""}

        # --- Search Functions ---
        def do_search():
            term = search_bar.text().strip()
            if term:
                current_term["text"] = term
                web.findText(term, QWebEnginePage.FindFlag(0))

        def do_next():
            if current_term["text"]:
                web.findText(current_term["text"], QWebEnginePage.FindFlag(0))

        def do_prev():
            if current_term["text"]:
                web.findText(current_term["text"], QWebEnginePage.FindBackward)

        # Wire up
        search_btn.clicked.connect(do_search)
        next_btn.clicked.connect(do_next)
        prev_btn.clicked.connect(do_prev)

        # --- Layouts ---
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)
        search_layout.addWidget(search_bar, 2)
        search_layout.addWidget(search_btn, 1)
        search_layout.addWidget(prev_btn)
        search_layout.addWidget(next_btn)

        layout = QVBoxLayout()
        layout.addLayout(search_layout)
        layout.addWidget(web)

        popup.setLayout(layout)

        popup.show()
        return popup
