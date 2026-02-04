from PySide6.QtWidgets import QWidget, QHBoxLayout, QTreeWidgetItem
from PySide6.QtGui import QKeySequence, QShortcut, QTextBlockFormat, QTextCursor, QFont
from PySide6.QtCore import QSize, Qt

from qfluentwidgets import TextBrowser, MessageBoxBase, TreeWidget
from fixpath import app_root
from pathlib import Path
import resources_rc


DOC_MAP = {
    "Getting Started": "docs/getting_started.md",
    "Plotting": "docs/plotting.md",
    "Design of Experiments": "docs/doe.md",
    "How To (Tutorial)": "docs/howto.md",
    "Shortcuts": "docs/shortcuts.md",
    "Optimization": "docs/optimization.md",
    "Formulation": "docs/formulation.md",
    "Metamodeling": "docs/metamodel.md",
}

class DocumentationPopup(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        content = QWidget()
        layout = QHBoxLayout(content)

        self.list = TreeWidget()
        self.list.setHeaderHidden(True)

        getting_started = QTreeWidgetItem(["Getting Started"])
        how_to = QTreeWidgetItem(["How To (Tutorial)"])

        doe = QTreeWidgetItem(["Design of Experiments"])
        mmd = QTreeWidgetItem(["Metamodeling"])
        shortcuts = QTreeWidgetItem(["Shortcuts"])
        optimization = QTreeWidgetItem(["Optimization"])
        formulation = QTreeWidgetItem(["Formulation"])
        optimization.addChild(formulation)

        self.list.setCursor(Qt.PointingHandCursor)
        self.list.addTopLevelItems([getting_started, how_to, doe, mmd, optimization, shortcuts])
        layout.addWidget(self.list)

        self.md = TextBrowser()

        font = QFont()
        font.setPointSize(14)
        self.md.setFont(font)

        layout.addWidget(self.md)

        base_size: QSize = parent.size()
        base_x, base_y = map(int, [0.85 * base_size.width(), 0.8 * base_size.height()])
        self.md.setFixedWidth(base_x)
        self.md.setFixedHeight(base_y)

        self.viewLayout.addWidget(content)

        self.yesButton.setText("Close")
        self.yesButton.setCursor(Qt.PointingHandCursor)
        self.cancelButton.setCursor(Qt.PointingHandCursor)
        self.cancelButton.hide()

        QShortcut(QKeySequence("Ctrl+Return"), self, activated=self.yesButton.click)
        QShortcut(QKeySequence("Ctrl+Enter"), self, activated=self.yesButton.click)

        self.list.expandAll()
        first_item = self.list.topLevelItem(0)
        self.list.setCurrentItem(first_item)
        self.list.itemClicked.connect(self.load_doc)
        self.load_doc(first_item)
    
    def load_doc(self, item):
        name = item.text(0)
        if name in DOC_MAP:
            with open(app_root() / Path(DOC_MAP[name]), "r", encoding="utf-8") as f:
                text = f.read()
                self.md.setMarkdown(text)

                # --- Formatting ---
                cursor = self.md.textCursor()
                cursor.select(QTextCursor.Document)

                fmt = QTextBlockFormat()
                fmt.setLineHeight(110.0, QTextBlockFormat.LineHeightTypes.ProportionalHeight.value)
                fmt.setTopMargin(6)
                fmt.setBottomMargin(6)

                cursor.mergeBlockFormat(fmt)
