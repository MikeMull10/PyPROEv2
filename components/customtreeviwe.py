from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeView


class NewTreeView(QTreeView):
    """A hackneyed subclass of QTreeView for the sole purpose of changing the cursor to the pointy hand when an item is hovered over"""

    def __init__(self, widget):
        super(NewTreeView, self).__init__(widget)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, e):
        """Update the mouse cursor if the mouse is on a valid element"""
        target = self.indexAt(e.pos())
        if target.column() > 0 and target.data() != None:
            self.setCursor(Qt.PointingHandCursor)  # set to pointing hand
        else:
            self.setCursor(Qt.ArrowCursor)
