from PySide6.QtWidgets import QDialog, QVBoxLayout, QPlainTextEdit, QLineEdit, QListWidget
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import QProcess, Qt, QEvent

from pages.mainwindow import Ui_MainWindow

import re


def is_valid_hex_color(code):
    return bool(re.fullmatch(r"#?[0-9A-Fa-f]{6}", code))

colors = {
    "red": "#FF3A2C",
    "orange": "#FF7E33",
    "yellow": "#F9FF42",
    "green": "#36BF63",
    "blue": "#4DDEEE",
    "royal blue": "#4169E1",
    "purple": "#B344EB",
    "pink": "#F043C7",
    "black": "#141414",
    "white": "#FFFFFF"
}

display = {
    "finish-popup": "Usage: finish-popup [enable/disable]\n - enable\n - disable",
    "popup-color": "Usage: popup-color [color/hexcode]\n - white\n - #ffffff",
    "theme": "Usage: theme [main_theme] [sub_theme]\n - white, dark\n    - default, simplified\n\n - navy, crimson, raspberry\n\n - neon\n     - " + "\n     - ".join(['red', 'orange', 'yellow', 'green', 'blue', 'royal / royal-blue', 'purple', 'pink']),
    "tolerance": "Usage: tolerance [float]\n - 1e-20",
    "wsfmaxiter": "Usage: wsfmaxiter [int]\n - 100",
    "wsftol": "Usage: wsftol [float]\n - 1e-6",
}


class CommandConsole(QDialog):
    def __init__(self, parent=None, ui: Ui_MainWindow=None, set_theme_func: callable=None):
        super().__init__(parent)
        self.setWindowTitle("Dev Console")
        self.resize(600, 400)

        # Set UI
        self.ui = ui

        # Layout
        self.layout = QVBoxLayout(self)

        # Set Theme Function
        self.set_theme_func = set_theme_func

        # Output Display
        self.output_display = QPlainTextEdit(self)
        self.output_display.setReadOnly(True)
        self.layout.addWidget(self.output_display)

        # Command Input
        self.input_line = QLineEdit(self)
        self.input_line.setPlaceholderText("Enter command...")
        self.input_line.textChanged.connect(self.update_suggestions)  # Live command suggestion
        self.input_line.returnPressed.connect(self.process_input)
        self.layout.addWidget(self.input_line)
        self.input_line.installEventFilter(self)

        # Command Suggestions List
        self.suggestion_list = QListWidget(self)
        self.suggestion_list.setVisible(False)
        self.suggestion_list.itemClicked.connect(self.select_suggestion)
        self.layout.addWidget(self.suggestion_list)

        # Custom Commands
        self.commands = {
            "help":  { "valid_args": [], "args": "", "function": self.command_help },
            "set":   { "valid_args": ["finish-popup", "popup-color", "theme", "tolerance", "wsfmaxiter", "wsftol"], "args": "<key> <value>", "function": self.command_set },
            "get":   { "valid_args": ["finish-popup", "popup-color", "theme", "tolerance", "wsfmaxiter", "wsftol"], "args": "<key>", "function": self.command_get },
            "reset": { "valid_args": ["confirm"], "args": "confirm", "function": self.command_reset },
            "clear": { "valid_args": [], "args": "", "function": self.command_clear },
            "exit":  { "valid_args": [], "args": "", "function": self.command_exit },
        }

        # Process for running system commands
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)

        # Add CTRL+W to close the window
        close_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_shortcut.activated.connect(self.close)

        self.setStyleSheet("QPlainTextEdit, QListWidget, QLineEdit, QListWidget::item { font-size: 12px; }")

    def process_input(self):
        """Handle command execution (custom or system)."""
        command_text = self.input_line.text().strip()
        self.output_display.appendPlainText(f"> {command_text}")
        self.input_line.clear()
        self.suggestion_list.setVisible(False)  # Hide suggestions on execution

        if not command_text:
            return

        parts = command_text.split()
        cmd, args = parts[0], parts[1:]

        if cmd in self.commands:
            self.commands[cmd]['function'](args)
        else:
            self.process.start(command_text)
        
        self.output_display.verticalScrollBar().setValue(self.output_display.verticalScrollBar().maximum())

    # Custom Commands
    def command_reset(self, args):
        """Resets all the settings (except theme) to default."""
        if len(args) == 1:
            if args[0].lower() == "confirm":
                self.ui.settings.setValue('Tolerance', 1e-20)
                self.ui.settings.setValue('Popup-Color', "#051923")
                self.ui.settings.setValue("WSFTol", 1e-6)
                self.ui.settings.setValue("WSFMaxIter", 100)
                self.output_display.appendPlainText("Settings successfully reset.")
                return
            
        self.output_display.appendPlainText("Usage: reset confirm")

    def command_clear(self, args):
        """Custom command to clear the console output."""
        self.output_display.clear()

    def command_help(self, args):
        """Displays available commands."""
        if len(args) == 0:
            self.output_display.appendPlainText("Available commands:\n - " + "\n - ".join(self.commands.keys()) + "\nEnter a command without any additional arguments for more detailed help.")

    def command_exit(self, args):
        """Exits the command console."""
        self.close()
    
    def command_get(self, args):
        """Gets a value."""
        if len(args) != 1:
            self.output_display.appendPlainText(self.__get_set_keys().replace("set <key> <value>", "get <key>"))
            return
        
        args[0] = args[0].replace('-', '_')

        match args[0].lower():
            case 'tolerance':
                self.output_display.appendPlainText(f"Tolerance: {self.ui.settings.value('Tolerance')}")
            case 'wsftol':
                self.output_display.appendPlainText(f"WSF Ftol: {self.ui.settings.value('WSFTol')}")
            case 'wsfmaxiter':
                self.output_display.appendPlainText(f"WSF Max Iterations: {self.ui.settings.value('WSFMaxIter')}")
            case 'popup_color':
                self.output_display.appendPlainText(f"Popup-Color: {self.ui.settings.value('Popup-Color')}")
            case 'theme':
                self.output_display.appendPlainText(f"Theme: {self.ui.settings.value('Theme')} {self.ui.settings.value('ThemeColor')}".strip())
            case 'finish_popup':
                self.output_display.appendPlainText(f"Popup-Finish: {'enabled' if self.ui.settings.value('Popup-Finish') == 'true' else 'disabled'}")
            case _:
                self.output_display.appendPlainText("Unknown key entered.")
    
    def command_set(self, args):
        """Sets a value."""
        if len(args) == 1:
            self.output_display.appendPlainText(display.get(args[0], "Argument not found."))
            return
        elif len(args) == 0 or (args[0].lower() != "theme" and len(args) != 2) or (args[0].lower() == "theme" and (len(args) not in [2, 3])):
            self.output_display.appendPlainText(self.__get_set_keys())
            return
        
        while len(args) < 3: args += [""]

        key, value, value2 = args
        key = key.replace('-', '_')

        match key.lower():
            case 'tolerance':
                try:
                    set_val = float(value) if (value.lower() != 'default' and float(value) < 1) else 1e-20
                    self.ui.settings.setValue('Tolerance', set_val)
                    self.output_display.appendPlainText(f"Tolerance set to {set_val}.")
                except Exception as e:
                    self.output_display.appendPlainText(f"Unable to set {key}.\nError: {e}")
            case 'wsftol':
                try:
                    set_val = float(value) if (value.lower() != 'default' and float(value) < 1) else 1e-6
                    self.ui.settings.setValue('WSFTol', set_val)
                    self.output_display.appendPlainText(f"WSF-Ftol set to {set_val}.")
                except Exception as e:
                    self.output_display.appendPlainText(f"Unable to set WSF-Ftol to {key}.\nError: {e}")
            case 'wsfmaxiter':
                try:
                    set_val = int(value) if (value.lower() != 'default' and int(value) > 1) else 100
                    self.ui.settings.setValue('WSFMaxIter', set_val)
                    self.output_display.appendPlainText(f"WSF Max Iterations set to {set_val}.")
                except Exception as e:
                    self.output_display.appendPlainText(f"Unable to set WSF Max Iterations to {key}.\nError: {e}")
            case 'popup_color':
                try:
                    if value == 'default':
                        value = '#051923'
                    elif value in list(colors.keys()):
                        value = colors.get(value, '#051923')
                    elif len(value) == 6 and not value.startswith('#') and is_valid_hex_color('#' + value):
                        value = '#' + value
                    elif len(value) == 7 and value.startswith('#') and is_valid_hex_color(value):
                        pass
                    else:
                        raise ValueError
                    self.ui.settings.setValue('Popup-Color', value)
                    self.output_display.appendPlainText(f"Popup-Color set to {value}.")
                except Exception as e:
                    self.output_display.appendPlainText(f"Unable to set popup color to {value}.")
            case 'theme':
                value  = value.lower()
                value2 = value2.lower()
                if value == "default":
                    self.ui.settings.setValue("Theme", "White")
                    self.ui.settings.setValue("ThemeColor", "")
                elif value in ["navy", "crimson", "raspberry"]:
                    self.ui.settings.setValue("Theme", value.capitalize())
                    self.ui.settings.setValue("ThemeColor", "")
                elif value in ["white", "dark"]:
                    if value2 not in ['default', 'simplified']:
                        value2 = 'default'
                    self.ui.settings.setValue("Theme", value.capitalize())
                    self.ui.settings.setValue("ThemeColor", value2.capitalize())
                elif value == "neon":
                    if value2 not in ['red', 'orange', 'yellow', 'green', 'blue', 'royal', 'royal-blue', 'purple', 'pink']:
                        value2 = 'red'
                    elif value2 == 'royal-blue' or value2 == 'royal':
                        value2 = 'Royal Blue'
                    self.ui.settings.setValue("Theme", value.capitalize())
                    self.ui.settings.setValue("ThemeColor", value2 if value2 == "Royal Blue" else value2.capitalize())
                else:
                    self.output_display.appendPlainText("Failed to set the theme.")
                    return
                
                self.set_theme_func()
                self.output_display.appendPlainText("Theme set successfully.")
            case 'finish_popup':
                value = value.lower()
                if value == 'enable' or value == 'enabled' or value == 'true':
                    self.ui.settings.setValue("Popup-Finish", True)
                    self.output_display.appendPlainText("Popup-Finish successfully enabled.")
                elif value == 'disable' or value == 'disabled' or value == 'false':
                    self.ui.settings.setValue("Popup-Finish", False)
                    self.output_display.appendPlainText("Finish-Popup successfully disabled.")
                else:
                    self.output_display.appendPlainText("Failed to set the value of Finish-Popup.")
                    return
            case _:
                self.output_display.appendPlainText("Unknown key entered.")
    
    def __get_set_keys(self):
        return """
Usage: set <key> <value>

List of keys:
 - finish-popup [enable/disable] (Default: enable)
   - enables/disables the popup message when optimization finishes
 - popup-color [color/hexcode] (Default: #051923)
   - sets the color of the background of the graph popup windows
 - theme [text] [*text] (Default: White *Default)
   - set the theme of the application (* = optional)
 - tolerance [float] (Default: 1e-20)
   - sets the tolerance for the SLSQP optimization methods
 - wsfmaxiter [int] (Default: 100)
   - sets the maximum number of iterations for wsf calculation
 - wsftol [float] (Default: 1e-6)
   - sets the ftol for wsf calculation
"""

    def read_stdout(self):
        """Read and display standard output from system commands."""
        output = self.process.readAllStandardOutput().data().decode()
        self.output_display.appendPlainText(output)

    def read_stderr(self):
        """Read and display error output from system commands."""
        error_output = self.process.readAllStandardError().data().decode()
        self.output_display.appendPlainText(error_output)

    def update_suggestions(self):
        """Update command suggestions dynamically as the user types."""
        text = self.input_line.text().strip()
        self.suggestion_list.clear()

        if not text:
            self.suggestion_list.setVisible(False)
            return

        # Split input into command and arguments
        parts = text.split()
        command_part = parts[0].lower()
        additional_input = parts[1:] if len(parts) > 1 else []

        matching_suggestions = []

        if len(parts) == 1:
            # User is typing a command -> Suggest commands
            for cmd, details in self.commands.items():
                if cmd.startswith(command_part):
                    arg_hint = " " + details['args'] if isinstance(details, dict) and 'args' in details else ""
                    matching_suggestions.append(cmd + arg_hint)

        else:
            # User has entered a command and is typing an argument
            if command_part in self.commands and isinstance(self.commands[command_part], dict):
                valid_args = self.commands[command_part].get("valid_args", [])

                if valid_args:
                    # Filter argument suggestions based on user input
                    arg_input = additional_input[-1].lower() if additional_input else ""
                    matching_suggestions = [arg for arg in valid_args if arg.startswith(arg_input)]

        if matching_suggestions:
            self.suggestion_list.addItems(matching_suggestions)
            self.suggestion_list.setVisible(True)
            self.suggestion_list.setCurrentRow(0)  # Highlight first item

            # Adjust height dynamically (each row is ~30px high)
            row_height = 30
            max_height = 100  # Max height of suggestion list
            self.suggestion_list.setFixedHeight(max(min(len(matching_suggestions) * row_height, max_height), 60))

        else:
            self.suggestion_list.setVisible(False)

    def select_suggestion(self, item):
        """Set the clicked suggestion as the input text."""
        self.input_line.setText(item.text())
        self.input_line.setFocus()
        self.suggestion_list.setVisible(False)
    
    def eventFilter(self, obj, event):
        """Handle key events in the input line."""
        if obj == self.input_line and event.type() == QEvent.KeyPress:
            if self.suggestion_list.isVisible():
                if event.key() == Qt.Key_Down:
                    current_row = self.suggestion_list.currentRow()
                    self.suggestion_list.setCurrentRow(min(current_row + 1, self.suggestion_list.count() - 1))
                    return True  # Prevent default handling

                elif event.key() == Qt.Key_Up:
                    current_row = self.suggestion_list.currentRow()
                    self.suggestion_list.setCurrentRow(max(current_row - 1, 0))
                    return True  # Prevent default handling

                elif event.key() == Qt.Key_Tab:
                    selected_item = self.suggestion_list.currentItem()
                    if selected_item:
                        current_text = self.input_line.text().strip().split(" ")
                        current_text = " ".join(current_text[:-1])
                        selected_text = selected_item.text()

                        # Append the selected suggestion instead of replacing
                        if not current_text.endswith(" "):  # Ensure spacing before appending
                            current_text += " "

                        self.input_line.setText(current_text + selected_text)

                    self.suggestion_list.setVisible(False)  # Hide suggestions
                    return True  # Prevent default handling

        return super().eventFilter(obj, event)  # Pass unhandled events to default handler
