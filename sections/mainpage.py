from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from components.clickabletitle import ClickableTitleLabel
from sections.designofexperiments import DesignOfExperimentsPage
from sections.metamodeling import MetamodelPage
from sections.optimization import OptimizationPage


class MainPage(QWidget):
    def __init__(self, formpage=None, doepage: DesignOfExperimentsPage=None, metapage: MetamodelPage=None, optpage: OptimizationPage=None):
        super().__init__()
        self.setObjectName("Main")
        self.main = QVBoxLayout(self)

        self.formpage = formpage
        self.doepage: DesignOfExperimentsPage = doepage
        self.doepage.toggle_call = lambda: self.handle_collapse(page_name="doe")
        self.metapage: MetamodelPage = metapage
        self.metapage.toggle_call = lambda: self.handle_collapse(page_name="mmd")
        self.optpage = optpage

        self.doe_title = ClickableTitleLabel("Design of Experiments    ")  # this is DISGUSTING, but works so damn well for what I want
        self.doe_title.setVisible(False)
        self.doe_title.clicked.connect(self.doepage.toggle_collapse)
        self.meta_title = ClickableTitleLabel("Metamodeling")
        self.meta_title.setVisible(False)
        self.meta_title.clicked.connect(self.metapage.toggle_collapse)
        self.doe_title.setTextColor(QColor(90, 90, 90), QColor(221, 221, 221))
        self.meta_title.setTextColor(QColor(90, 90, 90), QColor(221, 221, 221))
    

        self.top = QHBoxLayout()
        self.bottom = QHBoxLayout()

        self.layout_a = QHBoxLayout()
        self.layout_a.setAlignment(Qt.AlignTop)
        self.layout_b = QHBoxLayout()
        self.layout_b.setAlignment(Qt.AlignTop)

        self.layout_a.addWidget(self.doe_title)
        self.layout_a.addWidget(self.doepage)
        self.layout_b.addWidget(self.meta_title)
        self.layout_b.addWidget(self.metapage)

        self.top.addLayout(self.layout_a)
        self.top.addSpacing(5)
        self.top.addLayout(self.layout_b)

        self.bottom.addWidget(self.optpage)
        
        self.top.setContentsMargins(0, 0, 0, 0)
        self.bottom.setContentsMargins(0, 0, 0, 0)
        self.top.setSpacing(0)
        self.bottom.setSpacing(0)

        self.main.addLayout(self.top)
        self.main.addLayout(self.bottom)

        self.optpage.section_title.clicked.connect(self.do_strech)
        self.do_strech()
    
    def handle_collapse(self, page_name: str):
        match page_name:
            case "doe":
                self.doe_title.setVisible(not self.doepage.showing)
            case "mmd":
                self.meta_title.setVisible(not self.metapage.showing)
        self.do_strech()
    
    def do_strech(self):
        self.top.setStretch(0, int(self.doepage.showing))
        self.top.setStretch(2, int(self.metapage.showing))
        self.main.setStretch(0, (self.doepage.showing or self.metapage.showing) and self.optpage.showing)
        self.main.setStretch(1, (self.doepage.showing or self.metapage.showing) and self.optpage.showing)
        self.top.setContentsMargins(0, 0, 0, 24 * (not((self.doepage.showing or self.metapage.showing) and self.optpage.showing)))
