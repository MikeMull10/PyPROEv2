from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QSettings
from qfluentwidgets import PushButton, ComboBox, TitleLabel, SubtitleLabel, setTheme, Theme

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("settings")  # required for addSubInterface
        self.settings = QSettings("PyPROE", "PyPROE App")

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

        layout.addStretch()

    def update_theme(self):
        self.settings.setValue("theme", self.theme_combo.currentText())
        setTheme(Theme.DARK if self.theme_combo.currentIndex() else Theme.LIGHT)
