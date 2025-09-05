from PySide6.QtCore import QSettings, Signal, QObject
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QFormLayout, QLabel, QComboBox, QSpinBox, QCheckBox, QLineEdit, QDialogButtonBox, QVBoxLayout

from basics.basic_function import resource_path

all_settings = {
    "menu_pos": {
        "category": None,
        "default": "Top",
        "type": str,
        "values": ["Top", "Left", "Right", "Bottom"],
    },
    "theme": {
        "category": None,
        "default": "Light",
        "type": str,
        "values": ["Light", "Dark"],
    },
    "subtheme": {
        "category": None,
        "default": "Default",
        "type": str,
        "values": ['Default', 'Red', 'Orange', 'Yellow', 'Green', 'Light Blue', 'Blue', 'Purple', 'Pink']
    },
    "previous_open_file_dir": {
        "category": None,
        "default": "",
        "type": str,
    }
}

class SettingsManager(QObject):
    setting_changed = Signal(str, object)

    def __init__(self, ui):
        super().__init__(None)
        self.settings = QSettings("Porus", "Interface")
        self.__setup_settings()
        self.ui = ui

    def __setup_settings(self):
        """Intialize all of the settings in the application."""
        try:
            for key in list(all_settings.keys()):
                if not self.settings.contains(key):
                    self.settings.setValue(key, all_settings[key]['default'])
        except:
            self.settings.clear()
            self.settings.sync()
    
    def settings_popup(self):
        dlg = QDialog()
        dlg.setWindowTitle("Settings")
        dlg.setWindowIcon(QIcon(resource_path("assets/pyproe-logo.png")))

        form = QFormLayout(dlg)
        widgets = {}  # to hold the input widgets by key

        # --- dynamically build one row per setting ---
        for key, meta in all_settings.items():
            typ     = meta["type"]
            default = meta["default"]
            val     = typ(self.settings.value(key, default))

            if typ is str and meta.get("values"):
                # finite choices → combo
                cb = QComboBox()
                cb.addItems(meta["values"])
                if val in meta["values"]:
                    cb.setCurrentText(val)
                form.addRow(QLabel(key.replace("_"," ").title()), cb)
                widgets[key] = cb

            elif typ is int:
                # integer → spinbox
                sb = QSpinBox()
                sb.setRange(meta.get("min", -999999), meta.get("max", 999999))
                sb.setValue(val)
                form.addRow(QLabel(key.replace("_"," ").title()), sb)
                widgets[key] = sb

            elif typ is bool:
                # boolean → checkbox
                chk = QCheckBox()
                chk.setChecked(bool(val))
                form.addRow(QLabel(key.replace("_"," ").title()), chk)
                widgets[key] = chk

            else:
                # fallback: plain text entry
                le = QLineEdit(str(val))
                form.addRow(QLabel(key.replace("_"," ").title()), le)
                widgets[key] = le

        # --- OK / Cancel buttons ---
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=dlg
        )
        form.addRow(buttons)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)

        if dlg.exec() == QDialog.Accepted:
            # write back each widget’s value to QSettings
            for key, w in widgets.items():
                meta = all_settings[key]
                if isinstance(w, QComboBox):
                    self.set(key, w.currentText())
                elif isinstance(w, QSpinBox):
                    self.set(key, w.value())
                elif isinstance(w, QCheckBox):
                    self.set(key, w.isChecked())
                else:  # QLineEdit or others
                    text = w.text()
                    # cast back to the declared type
                    try:
                        self.set(key, meta["type"](text))
                    except:
                        self.set(key, text)
            self.settings.sync()

    #–– Convenience API ––
    def get(self, key: str, default=None, typ=None):
        v = self.settings.value(key, default)
        if typ is not None and v is not None:
            try: return typ(v)
            except: return default
        return v

    def set(self, key: str, value) -> None:
        self.settings.setValue(key, f"{value}")
        self.setting_changed.emit(key, f"{value}")

    def __call__(self, *args, **kwds):
        return self.get(key=args[0])
    
    def __getitem__(self, key):
        return self.get(key=key)
    
    def __setitem__(self, key: str, value):
        self.set(key=key, value=value)

    def child_groups(self, prefix: str="") -> list[str]:
        # if you want only groups under prefix, you can filter
        groups = self.settings.childGroups()
        if prefix:
            return [g for g in groups if g.startswith(prefix + "/")]
        return groups

    def child_keys(self, prefix: str="") -> list[str]:
        # return keys under a given group
        if prefix:
            self.settings.beginGroup(prefix)
            keys = self.settings.childKeys()
            self.settings.endGroup()
            return keys
        return self.settings.allKeys()
    
    def create_popup(self, parent):
        dlg = QDialog()
        dlg.setWindowTitle("Settings")
        dlg.setWindowIcon(QIcon(resource_path("assets/pyproe-logo.png")))

        form = QFormLayout(dlg)

        ### --- Items ---
        theme_layout = QVBoxLayout()
        theme_layout.addWidget(QLabel("Theme"))
        theme_drop = QComboBox()
        theme_drop.addItems(['Light', 'Dark'])
        theme_drop.setCurrentText(self.get('theme'))
        theme_layout.addWidget(theme_drop)
        theme_drop.currentTextChanged.connect(
            lambda text: (self.set('theme', text), parent._update_stylesheet())
        )

        subtheme_layout = QVBoxLayout()
        subtheme_layout.addWidget(QLabel("Subtheme"))
        subtheme_drop = QComboBox()
        subtheme_drop.addItems(all_settings['subtheme']['values'])
        subtheme_drop.setCurrentText(self.get('subtheme'))
        subtheme_layout.addWidget(subtheme_drop)
        subtheme_drop.currentTextChanged.connect(
            lambda text: (self.set('subtheme', text), parent._update_stylesheet())
        )

        form.addRow(theme_layout)
        form.addRow(subtheme_layout)

        # --- OK / Cancel buttons ---
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=dlg
        )
        form.addRow(buttons)
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)

        if dlg.exec() == QDialog.Accepted:
            pass