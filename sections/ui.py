import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QStatusBar, QToolBar, QPushButton, QGridLayout,
    QWidget, QVBoxLayout, QScrollArea, QHBoxLayout, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QShortcut, QKeySequence, QAction

from basics.basic_function import resource_path
from stylesheet.colors import *
from stylesheet.stylesheet import get_stylesheet

from sections.designofexperiments import DesignOfExperimentsPage
from sections.optimization import OptimizationPage
from sections.formulation import FormulationPage
from sections.metamodelling import MetamodelPage

from basics.settings import SettingsManager

class MiniPage(QWidget):
    """A simple mini-page widget with a title and placeholder content."""
    def __init__(self, title: str, color: str):
        super().__init__()

        self.setStyleSheet(f"background-color: {color}; border: none;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)  # remove padding inside the widget
        layout.setSpacing(0)                   # remove spacing between items in layout
        
        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        btn = QPushButton("Test Button")
        btn.setStyleSheet(get_stylesheet('Light'))
        layout.addWidget(btn)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- Window setup ---
        self.setWindowTitle("PyPROE X")
        self.setWindowIcon(QIcon(resource_path("assets/pyproe-logo.png")))
        self.resize(1200, 800)  # width, height
        self.showMaximized()

        self.settings = SettingsManager(self)

        # --- Pages ---
        self.frm = FormulationPage()
        self.doe = DesignOfExperimentsPage()
        self.mmd = MetamodelPage()
        self.opt = OptimizationPage()

        # --- Central widget with scrollable pages ---
        container = QWidget()
        v_container = QWidget()
        hbox = QHBoxLayout(container)
        vbox = QVBoxLayout(v_container)
        hbox.setContentsMargins(0, 0, 0, 0)
        vbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.setSpacing(0)

        vbox.addWidget(self.doe)
        vbox.addWidget(self.mmd)
        vbox.addWidget(self.opt)

        hbox.addWidget(self.frm)
        hbox.addWidget(v_container)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(container)

        self.setCentralWidget(scroll)

        # --- Setup ---
        # self.setStyleSheet(get_stylesheet(self.settings["theme"]))
        self.setStyleSheet(get_stylesheet('Dark'))
        self._setup_commands()
        self._setup_menu()
    
    def _setup_commands(self) -> None:
        # Close the Application
        self.ctrl_q = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.ctrl_q.activated.connect(self.close_application)

        # Open file shortcut
        self.ctrl_o = QShortcut(QKeySequence("Ctrl+O"), self)
        self.ctrl_o.activated.connect(self._open_file)

    def _setup_menu(self) -> None:
        menu_bar = self.menuBar()

        # File Menu
        file_menu = menu_bar.addMenu("File")

        new_action = QAction("New", self)
        open_action = QAction("Open", self)
        open_action.triggered.connect(self._open_file)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close_application)

        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction(QAction("Copy", self))
        edit_menu.addAction(QAction("Paste", self))

        # Preferences
        pref_menu = menu_bar.addMenu("Preferences")
        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.show_settings)
        pref_menu.addAction(settings_action)
    
    def close_application(self) -> None:
        QApplication.instance().quit()

    def show_settings(self):
        QMessageBox.information(self, "Settings", "Preferences dialog would appear here.")

    def _open_file(self):
        self.open_file_dialog = QFileDialog(self, 
                                            "Open File", 
                                            self.settings['previous_open_file_dir'],
                                            "Optimization function files (*.fnc)"
                                            )
        
        self.open_file_dialog.setFileMode(QFileDialog.ExistingFile)
        self.open_file_dialog.setAcceptMode(QFileDialog.AcceptOpen)

        if self.open_file_dialog.exec():
            self.open_file_name = self.open_file_dialog.selectedFiles()[0]
            self.settings.set('previous_open_file_dir', self.open_file_name)

            try:
                with open('testing/Binh&Korn.fnc', 'r') as file:
                    data = file.read()

                self.frm.layout.setText(data)
            except:
                print("FAIL")
