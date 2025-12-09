from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QSettings
from qfluentwidgets import LineEdit, ComboBox, TitleLabel, SubtitleLabel, setTheme, setThemeColor, Theme

from stylesheet.accents import ACCENT_COLORS
import webcolors


def is_valid_hex_color(s):
    try:
        webcolors.hex_to_rgb(s)
        return True
    except ValueError:
        return False

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("settings")  # required for addSubInterface
        self.settings = QSettings("PyPROE", "PyPROE App")
        self.init_setting_values()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = TitleLabel("Settings")
        layout.addWidget(title)

        # Theme selection
        theme_label = SubtitleLabel("Select Theme:")
        layout.addWidget(theme_label)

        self.theme_combo = ComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.setCurrentIndex(int(self.settings.value("theme") == "Dark"))
        layout.addWidget(self.theme_combo)
        self.theme_combo.currentTextChanged.connect(self.update_theme)

        accent_label = SubtitleLabel("Select Accent Color:")
        layout.addWidget(accent_label)

        self.accent_combo = ComboBox()
        self.accent_combo.addItems(list(ACCENT_COLORS.keys()))
        self.accent_combo.setCurrentIndex(list(ACCENT_COLORS).index(self.settings.value("accent")))
        layout.addWidget(self.accent_combo)
        self.accent_combo.currentTextChanged.connect(self.update_accent)

        self.custom_label = SubtitleLabel("Enter Custom Hexcode:")
        self.custom_box = LineEdit()
        self.custom_box.setText(self.settings.value("custom_accent"))
        self.custom_box.textChanged.connect(self.update_accent)
        self.custom_box.setPlaceholderText("#000000")

        layout.addWidget(self.custom_label)
        layout.addWidget(self.custom_box)
        self.custom_label.setToolTip("Enter Hexcode (Ex. #000000). White and Black colors will automatically contrast with the main theme.")
        self.custom_box.setToolTip("Enter Hexcode (Ex. #000000). White and Black colors will automatically contrast with the main theme.")

        if self.accent_combo.currentText() != "Custom":
            self.custom_label.hide()
            self.custom_box.hide()

        layout.addStretch()
    
    def init_setting_values(self):
        keys = ["theme", "accent", "custom_accent"]
        defaults = ["Light", "Red", "#000000"]
        for key, default in zip(keys, defaults):
            if self.settings.value(key) is None:
                self.settings.setValue(key, default)

        if self.settings.value("accent") not in ACCENT_COLORS.keys():
            self.settings.setValue("accent", list(ACCENT_COLORS.keys())[0])

    def update_theme(self):
        self.settings.setValue("theme", self.theme_combo.currentText())
        setTheme(Theme.DARK if self.theme_combo.currentIndex() else Theme.LIGHT)

    def update_accent(self):
        if self.accent_combo.currentText() != "Custom":
            self.custom_label.hide()
            self.custom_box.hide()
        else:
            self.custom_label.show()
            self.custom_box.show()
            self.settings.setValue("custom_accent", self.custom_box.text())

        self.settings.setValue("accent", self.accent_combo.currentText())

        if self.accent_combo.currentText() == "Custom":
            hex = "#000000"
            if is_valid_hex_color(self.custom_box.text()):
                hex = self.custom_box.text()
            
            try:
                setThemeColor(hex)
            except Exception as e:
                print(e)
        else:
            setThemeColor(ACCENT_COLORS.get(self.settings.value("accent"), ACCENT_COLORS.get("Red")))
