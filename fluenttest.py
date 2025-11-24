from PySide6.QtWidgets import QApplication
from qfluentwidgets import FluentWindow, setTheme, Theme, NavigationItemPosition
from qfluentwidgets import FluentIcon as FI

app = QApplication([])

setTheme(Theme.DARK)

window = FluentWindow()

# Use the built-in navigationInterface
nav = window.navigationInterface

nav.addSeparator()
nav.addItem(
    routeKey="home",
    icon=FI.HOME,
    text="Home",
    onClick=lambda: print("Home clicked"),
    position=NavigationItemPosition.TOP
)

window.resize(1200, 800)
window.show()

app.exec()
