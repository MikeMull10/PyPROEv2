# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'PyPROE.ui'
##
## Created by: Qt User Interface Compiler version 6.7.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QHBoxLayout, QHeaderView, QLabel, QLayout,
    QLineEdit, QListWidget, QListWidgetItem, QMainWindow,
    QMenuBar, QPlainTextEdit, QPushButton, QSizePolicy,
    QSpacerItem, QSpinBox, QStackedWidget, QTableView,
    QTextEdit, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setWindowModality(Qt.WindowModality.NonModal)
        MainWindow.resize(922, 779)
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(8)
        MainWindow.setFont(font)
        MainWindow.setAutoFillBackground(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_3 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.tabBtns = QHBoxLayout()
        self.tabBtns.setSpacing(0)
        self.tabBtns.setObjectName(u"tabBtns")
        self.tabEditBtn = QPushButton(self.centralwidget)
        self.tabEditBtn.setObjectName(u"tabEditBtn")
        self.tabEditBtn.setCheckable(True)

        self.tabBtns.addWidget(self.tabEditBtn)

        self.tabMMDBtn = QPushButton(self.centralwidget)
        self.tabMMDBtn.setObjectName(u"tabMMDBtn")
        self.tabMMDBtn.setCheckable(True)

        self.tabBtns.addWidget(self.tabMMDBtn)

        self.tabFormulationBtn = QPushButton(self.centralwidget)
        self.tabFormulationBtn.setObjectName(u"tabFormulationBtn")
        self.tabFormulationBtn.setCheckable(True)

        self.tabBtns.addWidget(self.tabFormulationBtn)

        self.tabOptBtn = QPushButton(self.centralwidget)
        self.tabOptBtn.setObjectName(u"tabOptBtn")
        self.tabOptBtn.setCheckable(True)

        self.tabBtns.addWidget(self.tabOptBtn)

        self.tabMatpltBtn = QPushButton(self.centralwidget)
        self.tabMatpltBtn.setObjectName(u"tabMatpltBtn")
        self.tabMatpltBtn.setCheckable(True)

        self.tabBtns.addWidget(self.tabMatpltBtn)

        self.tabGradientBtn = QPushButton(self.centralwidget)
        self.tabGradientBtn.setObjectName(u"tabGradientBtn")
        self.tabGradientBtn.setCheckable(True)

        self.tabBtns.addWidget(self.tabGradientBtn)

        self.tabWriterBtn = QPushButton(self.centralwidget)
        self.tabWriterBtn.setObjectName(u"tabWriterBtn")
        self.tabWriterBtn.setCheckable(True)

        self.tabBtns.addWidget(self.tabWriterBtn)


        self.verticalLayout_3.addLayout(self.tabBtns)

        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setEnabled(True)
        self.tabEdit = QWidget()
        self.tabEdit.setObjectName(u"tabEdit")
        self.horizontalLayout_2 = QHBoxLayout(self.tabEdit)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setSpacing(8)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(8, 8, 8, 8)
        self.openDoeFile = QPushButton(self.tabEdit)
        self.openDoeFile.setObjectName(u"openDoeFile")

        self.verticalLayout_11.addWidget(self.openDoeFile)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label_5 = QLabel(self.tabEdit)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.verticalLayout_7.addWidget(self.label_5)

        self.methodCombo = QComboBox(self.tabEdit)
        self.methodCombo.setObjectName(u"methodCombo")
        self.methodCombo.setFrame(False)

        self.verticalLayout_7.addWidget(self.methodCombo)


        self.verticalLayout_11.addLayout(self.verticalLayout_7)

        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.label_4 = QLabel(self.tabEdit)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_10.addWidget(self.label_4)

        self.designVarNum = QSpinBox(self.tabEdit)
        self.designVarNum.setObjectName(u"designVarNum")
        self.designVarNum.setFrame(False)
        self.designVarNum.setMinimum(1)

        self.verticalLayout_10.addWidget(self.designVarNum)


        self.verticalLayout_11.addLayout(self.verticalLayout_10)

        self.verticalLayout_9 = QVBoxLayout()
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.label_10 = QLabel(self.tabEdit)
        self.label_10.setObjectName(u"label_10")

        self.verticalLayout_9.addWidget(self.label_10)

        self.levelCombo = QSpinBox(self.tabEdit)
        self.levelCombo.setObjectName(u"levelCombo")
        self.levelCombo.setFrame(False)
        self.levelCombo.setMinimum(2)
        self.levelCombo.setMaximum(20)
        self.levelCombo.setValue(2)

        self.verticalLayout_9.addWidget(self.levelCombo)


        self.verticalLayout_11.addLayout(self.verticalLayout_9)

        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label_9 = QLabel(self.tabEdit)
        self.label_9.setObjectName(u"label_9")
        self.label_9.setEnabled(False)

        self.verticalLayout_8.addWidget(self.label_9)

        self.designPointNum = QSpinBox(self.tabEdit)
        self.designPointNum.setObjectName(u"designPointNum")
        self.designPointNum.setEnabled(False)
        self.designPointNum.setFrame(False)
        self.designPointNum.setMinimum(1)

        self.verticalLayout_8.addWidget(self.designPointNum)


        self.verticalLayout_11.addLayout(self.verticalLayout_8)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_8 = QLabel(self.tabEdit)
        self.label_8.setObjectName(u"label_8")

        self.verticalLayout_2.addWidget(self.label_8)

        self.functionNum = QSpinBox(self.tabEdit)
        self.functionNum.setObjectName(u"functionNum")
        self.functionNum.setFrame(False)

        self.verticalLayout_2.addWidget(self.functionNum)


        self.verticalLayout_11.addLayout(self.verticalLayout_2)

        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(8)
        self.gridLayout.setObjectName(u"gridLayout")
        self.doeDesignBtn = QPushButton(self.tabEdit)
        self.doeDesignBtn.setObjectName(u"doeDesignBtn")

        self.gridLayout.addWidget(self.doeDesignBtn, 1, 1, 1, 2)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 5, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(8, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.verticalSpacer, 0, 1, 1, 1)

        self.doe_edit_vals = QPushButton(self.tabEdit)
        self.doe_edit_vals.setObjectName(u"doe_edit_vals")

        self.gridLayout.addWidget(self.doe_edit_vals, 2, 1, 1, 1)

        self.doe_add_point = QPushButton(self.tabEdit)
        self.doe_add_point.setObjectName(u"doe_add_point")

        self.gridLayout.addWidget(self.doe_add_point, 2, 2, 1, 1)

        self.doe_clearBtn = QPushButton(self.tabEdit)
        self.doe_clearBtn.setObjectName(u"doe_clearBtn")

        self.gridLayout.addWidget(self.doe_clearBtn, 3, 1, 1, 1)

        self.doeMetamodel = QPushButton(self.tabEdit)
        self.doeMetamodel.setObjectName(u"doeMetamodel")

        self.gridLayout.addWidget(self.doeMetamodel, 4, 1, 1, 2)

        self.doe_rmv_point = QPushButton(self.tabEdit)
        self.doe_rmv_point.setObjectName(u"doe_rmv_point")

        self.gridLayout.addWidget(self.doe_rmv_point, 3, 2, 1, 1)


        self.verticalLayout_11.addLayout(self.gridLayout)


        self.horizontalLayout_2.addLayout(self.verticalLayout_11)

        self.doeTable = QTableView(self.tabEdit)
        self.doeTable.setObjectName(u"doeTable")
        self.doeTable.setFrameShape(QFrame.Shape.Box)

        self.horizontalLayout_2.addWidget(self.doeTable)

        self.stackedWidget.addWidget(self.tabEdit)
        self.tabMMD = QWidget()
        self.tabMMD.setObjectName(u"tabMMD")
        self.horizontalLayout_3 = QHBoxLayout(self.tabMMD)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.mmdLayout = QVBoxLayout()
        self.mmdLayout.setSpacing(8)
        self.mmdLayout.setObjectName(u"mmdLayout")
        self.mmdLayout.setContentsMargins(8, 8, 8, 8)
        self.mmdFileLabel = QLabel(self.tabMMD)
        self.mmdFileLabel.setObjectName(u"mmdFileLabel")

        self.mmdLayout.addWidget(self.mmdFileLabel)

        self.mmdDoeButton = QPushButton(self.tabMMD)
        self.mmdDoeButton.setObjectName(u"mmdDoeButton")

        self.mmdLayout.addWidget(self.mmdDoeButton)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_6 = QLabel(self.tabMMD)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.verticalLayout.addWidget(self.label_6)

        self.mmdMethodCombo = QComboBox(self.tabMMD)
        self.mmdMethodCombo.setObjectName(u"mmdMethodCombo")

        self.verticalLayout.addWidget(self.mmdMethodCombo)


        self.mmdLayout.addLayout(self.verticalLayout)

        self.verticalLayout_16 = QVBoxLayout()
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.text_2 = QLabel(self.tabMMD)
        self.text_2.setObjectName(u"text_2")

        self.verticalLayout_16.addWidget(self.text_2)

        self.mmdFuncCombo = QComboBox(self.tabMMD)
        self.mmdFuncCombo.setObjectName(u"mmdFuncCombo")

        self.verticalLayout_16.addWidget(self.mmdFuncCombo)


        self.mmdLayout.addLayout(self.verticalLayout_16)

        self.verticalLayout_17 = QVBoxLayout()
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.label_11 = QLabel(self.tabMMD)
        self.label_11.setObjectName(u"label_11")

        self.verticalLayout_17.addWidget(self.label_11)

        self.mmdOrderCombo = QComboBox(self.tabMMD)
        self.mmdOrderCombo.setObjectName(u"mmdOrderCombo")

        self.verticalLayout_17.addWidget(self.mmdOrderCombo)


        self.mmdLayout.addLayout(self.verticalLayout_17)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setSpacing(8)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.oneFuncBtn = QPushButton(self.tabMMD)
        self.oneFuncBtn.setObjectName(u"oneFuncBtn")

        self.gridLayout_4.addWidget(self.oneFuncBtn, 1, 1, 1, 1)

        self.mmdFormBtn = QPushButton(self.tabMMD)
        self.mmdFormBtn.setObjectName(u"mmdFormBtn")

        self.gridLayout_4.addWidget(self.mmdFormBtn, 2, 1, 1, 1)

        self.funcValBtn = QPushButton(self.tabMMD)
        self.funcValBtn.setObjectName(u"funcValBtn")

        self.gridLayout_4.addWidget(self.funcValBtn, 1, 0, 1, 1)

        self.clearDispBtn = QPushButton(self.tabMMD)
        self.clearDispBtn.setObjectName(u"clearDispBtn")

        self.gridLayout_4.addWidget(self.clearDispBtn, 2, 0, 1, 1)

        self.verticalSpacer_3 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.verticalSpacer_3, 0, 0, 1, 1)


        self.mmdLayout.addLayout(self.gridLayout_4)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.mmdLayout.addItem(self.verticalSpacer_4)


        self.horizontalLayout_3.addLayout(self.mmdLayout)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(8)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.mmdTableView = QTableView(self.tabMMD)
        self.mmdTableView.setObjectName(u"mmdTableView")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mmdTableView.sizePolicy().hasHeightForWidth())
        self.mmdTableView.setSizePolicy(sizePolicy)
        self.mmdTableView.setMaximumSize(QSize(16777215, 200))

        self.verticalLayout_4.addWidget(self.mmdTableView)

        self.mmdEdit = QTextEdit(self.tabMMD)
        self.mmdEdit.setObjectName(u"mmdEdit")
        self.mmdEdit.setReadOnly(True)

        self.verticalLayout_4.addWidget(self.mmdEdit)


        self.horizontalLayout_3.addLayout(self.verticalLayout_4)

        self.stackedWidget.addWidget(self.tabMMD)
        self.tabOpt = QWidget()
        self.tabOpt.setObjectName(u"tabOpt")
        self.horizontalLayout = QHBoxLayout(self.tabOpt)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.optLayout = QVBoxLayout()
        self.optLayout.setSpacing(8)
        self.optLayout.setObjectName(u"optLayout")
        self.optLayout.setContentsMargins(8, 8, 8, 8)
        self.optFileLabel = QLabel(self.tabOpt)
        self.optFileLabel.setObjectName(u"optFileLabel")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.optFileLabel.sizePolicy().hasHeightForWidth())
        self.optFileLabel.setSizePolicy(sizePolicy1)

        self.optLayout.addWidget(self.optFileLabel)

        self.optFncBtn = QPushButton(self.tabOpt)
        self.optFncBtn.setObjectName(u"optFncBtn")

        self.optLayout.addWidget(self.optFncBtn)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_7 = QLabel(self.tabOpt)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.verticalLayout_6.addWidget(self.label_7)

        self.opt_solverCombo = QComboBox(self.tabOpt)
        self.opt_solverCombo.setObjectName(u"opt_solverCombo")

        self.verticalLayout_6.addWidget(self.opt_solverCombo)


        self.optLayout.addLayout(self.verticalLayout_6)

        self.grid_lay_2 = QWidget(self.tabOpt)
        self.grid_lay_2.setObjectName(u"grid_lay_2")
        self.verticalLayout_14 = QVBoxLayout(self.grid_lay_2)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.label_18 = QLabel(self.grid_lay_2)
        self.label_18.setObjectName(u"label_18")

        self.verticalLayout_14.addWidget(self.label_18)

        self.opt_grid_size = QSpinBox(self.grid_lay_2)
        self.opt_grid_size.setObjectName(u"opt_grid_size")
        self.opt_grid_size.setMinimum(1)
        self.opt_grid_size.setMaximum(100)
        self.opt_grid_size.setValue(5)

        self.verticalLayout_14.addWidget(self.opt_grid_size)


        self.optLayout.addWidget(self.grid_lay_2)

        self.iterations_lay = QWidget(self.tabOpt)
        self.iterations_lay.setObjectName(u"iterations_lay")
        self.verticalLayout_19 = QVBoxLayout(self.iterations_lay)
        self.verticalLayout_19.setSpacing(4)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_19.setContentsMargins(0, 0, 0, 0)
        self.mmdFuncCombo_2 = QLabel(self.iterations_lay)
        self.mmdFuncCombo_2.setObjectName(u"mmdFuncCombo_2")

        self.verticalLayout_19.addWidget(self.mmdFuncCombo_2)

        self.opt_solverData = QSpinBox(self.iterations_lay)
        self.opt_solverData.setObjectName(u"opt_solverData")
        self.opt_solverData.setMinimum(1)
        self.opt_solverData.setMaximum(10000)
        self.opt_solverData.setValue(100)

        self.verticalLayout_19.addWidget(self.opt_solverData)


        self.optLayout.addWidget(self.iterations_lay)

        self.weights_lay_2 = QWidget(self.tabOpt)
        self.weights_lay_2.setObjectName(u"weights_lay_2")
        self.weights_lay = QVBoxLayout(self.weights_lay_2)
        self.weights_lay.setObjectName(u"weights_lay")
        self.weights_lay.setContentsMargins(0, 0, 0, 0)
        self.label_12 = QLabel(self.weights_lay_2)
        self.label_12.setObjectName(u"label_12")

        self.weights_lay.addWidget(self.label_12)

        self.weights = QLineEdit(self.weights_lay_2)
        self.weights.setObjectName(u"weights")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.weights.sizePolicy().hasHeightForWidth())
        self.weights.setSizePolicy(sizePolicy2)
        self.weights.setToolTipDuration(-3)

        self.weights_lay.addWidget(self.weights)


        self.optLayout.addWidget(self.weights_lay_2)

        self.weight_increment_widget = QWidget(self.tabOpt)
        self.weight_increment_widget.setObjectName(u"weight_increment_widget")
        self.verticalLayout_21 = QVBoxLayout(self.weight_increment_widget)
        self.verticalLayout_21.setObjectName(u"verticalLayout_21")
        self.verticalLayout_21.setContentsMargins(0, 0, 0, 0)
        self.label_21 = QLabel(self.weight_increment_widget)
        self.label_21.setObjectName(u"label_21")
        self.label_21.setMaximumSize(QSize(389, 16777215))

        self.verticalLayout_21.addWidget(self.label_21)

        self.weight_increment = QLineEdit(self.weight_increment_widget)
        self.weight_increment.setObjectName(u"weight_increment")
        sizePolicy2.setHeightForWidth(self.weight_increment.sizePolicy().hasHeightForWidth())
        self.weight_increment.setSizePolicy(sizePolicy2)

        self.verticalLayout_21.addWidget(self.weight_increment)


        self.optLayout.addWidget(self.weight_increment_widget)

        self.population_lay_2 = QWidget(self.tabOpt)
        self.population_lay_2.setObjectName(u"population_lay_2")
        self.population_lay = QVBoxLayout(self.population_lay_2)
        self.population_lay.setObjectName(u"population_lay")
        self.population_lay.setContentsMargins(0, 0, 0, 0)
        self.label_16 = QLabel(self.population_lay_2)
        self.label_16.setObjectName(u"label_16")

        self.population_lay.addWidget(self.label_16)

        self.population = QSpinBox(self.population_lay_2)
        self.population.setObjectName(u"population")
        self.population.setMinimum(1)
        self.population.setMaximum(100000)
        self.population.setValue(100)

        self.population_lay.addWidget(self.population)


        self.optLayout.addWidget(self.population_lay_2)

        self.mutation_lay_2 = QWidget(self.tabOpt)
        self.mutation_lay_2.setObjectName(u"mutation_lay_2")
        self.mutation_lay = QVBoxLayout(self.mutation_lay_2)
        self.mutation_lay.setObjectName(u"mutation_lay")
        self.mutation_lay.setContentsMargins(0, 0, 0, 0)
        self.label_19 = QLabel(self.mutation_lay_2)
        self.label_19.setObjectName(u"label_19")

        self.mutation_lay.addWidget(self.label_19)

        self.mutation = QSpinBox(self.mutation_lay_2)
        self.mutation.setObjectName(u"mutation")
        self.mutation.setMinimum(1)
        self.mutation.setMaximum(100)
        self.mutation.setValue(1)

        self.mutation_lay.addWidget(self.mutation)


        self.optLayout.addWidget(self.mutation_lay_2)

        self.crossover_lay_2 = QWidget(self.tabOpt)
        self.crossover_lay_2.setObjectName(u"crossover_lay_2")
        self.crossover_lay = QVBoxLayout(self.crossover_lay_2)
        self.crossover_lay.setObjectName(u"crossover_lay")
        self.crossover_lay.setContentsMargins(0, 0, 0, 0)
        self.label_20 = QLabel(self.crossover_lay_2)
        self.label_20.setObjectName(u"label_20")

        self.crossover_lay.addWidget(self.label_20)

        self.crossover = QSpinBox(self.crossover_lay_2)
        self.crossover.setObjectName(u"crossover")
        self.crossover.setMinimum(1)
        self.crossover.setMaximum(100)
        self.crossover.setValue(90)

        self.crossover_lay.addWidget(self.crossover)


        self.optLayout.addWidget(self.crossover_lay_2)

        self.outer_lay_2 = QWidget(self.tabOpt)
        self.outer_lay_2.setObjectName(u"outer_lay_2")
        self.outer_lay = QVBoxLayout(self.outer_lay_2)
        self.outer_lay.setObjectName(u"outer_lay")
        self.outer_lay.setContentsMargins(0, 0, 0, 0)
        self.label_17 = QLabel(self.outer_lay_2)
        self.label_17.setObjectName(u"label_17")

        self.outer_lay.addWidget(self.label_17)

        self.nParts = QSpinBox(self.outer_lay_2)
        self.nParts.setObjectName(u"nParts")
        self.nParts.setMaximum(100000)
        self.nParts.setValue(100)

        self.outer_lay.addWidget(self.nParts)


        self.optLayout.addWidget(self.outer_lay_2)

        self.inner_lay_2 = QWidget(self.tabOpt)
        self.inner_lay_2.setObjectName(u"inner_lay_2")
        self.inner_lay = QVBoxLayout(self.inner_lay_2)
        self.inner_lay.setObjectName(u"inner_lay")
        self.inner_lay.setContentsMargins(0, 0, 0, 0)
        self.label_14 = QLabel(self.inner_lay_2)
        self.label_14.setObjectName(u"label_14")

        self.inner_lay.addWidget(self.label_14)


        self.optLayout.addWidget(self.inner_lay_2)

        self.normalize_lay = QWidget(self.tabOpt)
        self.normalize_lay.setObjectName(u"normalize_lay")
        self.verticalLayout_23 = QVBoxLayout(self.normalize_lay)
        self.verticalLayout_23.setSpacing(6)
        self.verticalLayout_23.setObjectName(u"verticalLayout_23")
        self.verticalLayout_23.setContentsMargins(0, 0, 0, 0)
        self.label_22 = QLabel(self.normalize_lay)
        self.label_22.setObjectName(u"label_22")

        self.verticalLayout_23.addWidget(self.label_22)

        self.normalize_function = QComboBox(self.normalize_lay)
        self.normalize_function.setObjectName(u"normalize_function")

        self.verticalLayout_23.addWidget(self.normalize_function)


        self.optLayout.addWidget(self.normalize_lay)

        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setSpacing(8)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.opt_clearBtn = QPushButton(self.tabOpt)
        self.opt_clearBtn.setObjectName(u"opt_clearBtn")

        self.gridLayout_6.addWidget(self.opt_clearBtn, 1, 2, 1, 1)

        self.optStopBtn = QPushButton(self.tabOpt)
        self.optStopBtn.setObjectName(u"optStopBtn")

        self.gridLayout_6.addWidget(self.optStopBtn, 1, 1, 1, 1)

        self.opt_startBtn = QPushButton(self.tabOpt)
        self.opt_startBtn.setObjectName(u"opt_startBtn")

        self.gridLayout_6.addWidget(self.opt_startBtn, 1, 0, 1, 1)


        self.optLayout.addLayout(self.gridLayout_6)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.optLayout.addItem(self.verticalSpacer_5)


        self.horizontalLayout.addLayout(self.optLayout)

        self.optOutputLayout = QVBoxLayout()
        self.optOutputLayout.setSpacing(8)
        self.optOutputLayout.setObjectName(u"optOutputLayout")
        self.optEdit = QTextEdit(self.tabOpt)
        self.optEdit.setObjectName(u"optEdit")
        self.optEdit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        self.optOutputLayout.addWidget(self.optEdit)

        self.optOutputLayout.setStretch(0, 2)

        self.horizontalLayout.addLayout(self.optOutputLayout)

        self.stackedWidget.addWidget(self.tabOpt)
        self.tabWriter = QWidget()
        self.tabWriter.setObjectName(u"tabWriter")
        self.gridLayout_5 = QGridLayout(self.tabWriter)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.wrtEdit = QTextEdit(self.tabWriter)
        self.wrtEdit.setObjectName(u"wrtEdit")

        self.gridLayout_5.addWidget(self.wrtEdit, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.tabWriter)
        self.tabForm = QWidget()
        self.tabForm.setObjectName(u"tabForm")
        self.horizontalLayout_6 = QHBoxLayout(self.tabForm)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.verticalLayout_18 = QVBoxLayout()
        self.verticalLayout_18.setSpacing(8)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setSizeConstraint(QLayout.SizeConstraint.SetMaximumSize)
        self.verticalLayout_18.setContentsMargins(8, 8, 8, 8)
        self.form_load_file = QPushButton(self.tabForm)
        self.form_load_file.setObjectName(u"form_load_file")

        self.verticalLayout_18.addWidget(self.form_load_file)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label = QLabel(self.tabForm)
        self.label.setObjectName(u"label")

        self.verticalLayout_5.addWidget(self.label)


        self.verticalLayout_18.addLayout(self.verticalLayout_5)

        self.verticalLayout_12 = QVBoxLayout()
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.label_2 = QLabel(self.tabForm)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_12.addWidget(self.label_2)


        self.verticalLayout_18.addLayout(self.verticalLayout_12)

        self.verticalLayout_13 = QVBoxLayout()
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.label_3 = QLabel(self.tabForm)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_13.addWidget(self.label_3)


        self.verticalLayout_18.addLayout(self.verticalLayout_13)

        self.verticalLayout_15 = QVBoxLayout()
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.label_13 = QLabel(self.tabForm)
        self.label_13.setObjectName(u"label_13")

        self.verticalLayout_15.addWidget(self.label_13)


        self.verticalLayout_18.addLayout(self.verticalLayout_15)

        self.form_constr_mods = QPushButton(self.tabForm)
        self.form_constr_mods.setObjectName(u"form_constr_mods")

        self.verticalLayout_18.addWidget(self.form_constr_mods)

        self.form_grad_policy = QPushButton(self.tabForm)
        self.form_grad_policy.setObjectName(u"form_grad_policy")

        self.verticalLayout_18.addWidget(self.form_grad_policy)

        self.view_latex = QPushButton(self.tabForm)
        self.view_latex.setObjectName(u"view_latex")

        self.verticalLayout_18.addWidget(self.view_latex)

        self.formResetEnv = QPushButton(self.tabForm)
        self.formResetEnv.setObjectName(u"formResetEnv")

        self.verticalLayout_18.addWidget(self.formResetEnv)

        self.verticalSpacer_7 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.verticalLayout_18.addItem(self.verticalSpacer_7)

        self.formOptBtn = QPushButton(self.tabForm)
        self.formOptBtn.setObjectName(u"formOptBtn")

        self.verticalLayout_18.addWidget(self.formOptBtn)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_18.addItem(self.verticalSpacer_6)


        self.horizontalLayout_5.addLayout(self.verticalLayout_18)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setSpacing(8)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(8, 8, 8, 8)
        self.verticalLayout_20 = QVBoxLayout()
        self.verticalLayout_20.setSpacing(0)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(8)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer_2 = QSpacerItem(8, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)

        self.lineEdit = QLineEdit(self.tabForm)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setFrame(False)
        self.lineEdit.setClearButtonEnabled(True)

        self.horizontalLayout_4.addWidget(self.lineEdit)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.formSaveBtn = QPushButton(self.tabForm)
        self.formSaveBtn.setObjectName(u"formSaveBtn")

        self.horizontalLayout_4.addWidget(self.formSaveBtn)

        self.formNewBtn = QPushButton(self.tabForm)
        self.formNewBtn.setObjectName(u"formNewBtn")

        self.horizontalLayout_4.addWidget(self.formNewBtn)

        self.formResetBtn = QPushButton(self.tabForm)
        self.formResetBtn.setObjectName(u"formResetBtn")

        self.horizontalLayout_4.addWidget(self.formResetBtn)

        self.horizontalSpacer_3 = QSpacerItem(8, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)


        self.verticalLayout_20.addLayout(self.horizontalLayout_4)

        self.formFuncEdit = QPlainTextEdit(self.tabForm)
        self.formFuncEdit.setObjectName(u"formFuncEdit")

        self.verticalLayout_20.addWidget(self.formFuncEdit)


        self.gridLayout_2.addLayout(self.verticalLayout_20, 2, 0, 1, 2)

        self.formFuncPreview = QPlainTextEdit(self.tabForm)
        self.formFuncPreview.setObjectName(u"formFuncPreview")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.formFuncPreview.sizePolicy().hasHeightForWidth())
        self.formFuncPreview.setSizePolicy(sizePolicy3)
        self.formFuncPreview.setReadOnly(True)

        self.gridLayout_2.addWidget(self.formFuncPreview, 0, 1, 1, 1)

        self.verticalSpacer_8 = QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.gridLayout_2.addItem(self.verticalSpacer_8, 1, 0, 1, 1)

        self.gridLayout_2.setRowStretch(0, 2)
        self.gridLayout_2.setRowStretch(2, 1)

        self.horizontalLayout_5.addLayout(self.gridLayout_2)


        self.horizontalLayout_6.addLayout(self.horizontalLayout_5)

        self.stackedWidget.addWidget(self.tabForm)
        self.tabPlot = QWidget()
        self.tabPlot.setObjectName(u"tabPlot")
        self.horizontalLayout_9 = QHBoxLayout(self.tabPlot)
        self.horizontalLayout_9.setSpacing(6)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(9, 9, 9, 9)
        self.plotSettings = QVBoxLayout()
        self.plotSettings.setSpacing(8)
        self.plotSettings.setObjectName(u"plotSettings")
        self.plotSettings.setContentsMargins(8, 8, 8, 8)
        self.plotFileLabel = QLabel(self.tabPlot)
        self.plotFileLabel.setObjectName(u"plotFileLabel")

        self.plotSettings.addWidget(self.plotFileLabel)

        self.plotOpenFile = QPushButton(self.tabPlot)
        self.plotOpenFile.setObjectName(u"plotOpenFile")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(2)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.plotOpenFile.sizePolicy().hasHeightForWidth())
        self.plotOpenFile.setSizePolicy(sizePolicy4)
        self.plotOpenFile.setMinimumSize(QSize(150, 0))

        self.plotSettings.addWidget(self.plotOpenFile)

        self.genPlot = QPushButton(self.tabPlot)
        self.genPlot.setObjectName(u"genPlot")

        self.plotSettings.addWidget(self.genPlot)

        self.genSurface = QPushButton(self.tabPlot)
        self.genSurface.setObjectName(u"genSurface")

        self.plotSettings.addWidget(self.genSurface)

        self.verticalSpacer_9 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.plotSettings.addItem(self.verticalSpacer_9)


        self.horizontalLayout_9.addLayout(self.plotSettings)

        self.plotGraphContainer = QListWidget(self.tabPlot)
        self.plotGraphContainer.setObjectName(u"plotGraphContainer")

        self.horizontalLayout_9.addWidget(self.plotGraphContainer)

        self.stackedWidget.addWidget(self.tabPlot)
        self.tabGradients = QWidget()
        self.tabGradients.setObjectName(u"tabGradients")
        self.verticalLayout_25 = QVBoxLayout(self.tabGradients)
        self.verticalLayout_25.setObjectName(u"verticalLayout_25")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.gradientSettings = QVBoxLayout()
        self.gradientSettings.setSpacing(8)
        self.gradientSettings.setObjectName(u"gradientSettings")
        self.gradientSettings.setContentsMargins(8, 8, 8, 8)
        self.gradientOpenFile = QPushButton(self.tabGradients)
        self.gradientOpenFile.setObjectName(u"gradientOpenFile")
        self.gradientOpenFile.setMinimumSize(QSize(150, 0))

        self.gradientSettings.addWidget(self.gradientOpenFile)

        self.genBlankTemplate = QPushButton(self.tabGradients)
        self.genBlankTemplate.setObjectName(u"genBlankTemplate")

        self.gradientSettings.addWidget(self.genBlankTemplate)

        self.verticalSpacer_10 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.gradientSettings.addItem(self.verticalSpacer_10)

        self.genGradientsBtn = QPushButton(self.tabGradients)
        self.genGradientsBtn.setObjectName(u"genGradientsBtn")

        self.gradientSettings.addWidget(self.genGradientsBtn)

        self.normalizeFNC = QPushButton(self.tabGradients)
        self.normalizeFNC.setObjectName(u"normalizeFNC")

        self.gradientSettings.addWidget(self.normalizeFNC)

        self.gradientSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gradientSettings.addItem(self.gradientSpacer)


        self.horizontalLayout_8.addLayout(self.gradientSettings)

        self.verticalLayout_22 = QVBoxLayout()
        self.verticalLayout_22.setSpacing(8)
        self.verticalLayout_22.setObjectName(u"verticalLayout_22")
        self.verticalLayout_22.setContentsMargins(8, 8, 8, 8)
        self.gradientOutput = QPlainTextEdit(self.tabGradients)
        self.gradientOutput.setObjectName(u"gradientOutput")

        self.verticalLayout_22.addWidget(self.gradientOutput)


        self.horizontalLayout_8.addLayout(self.verticalLayout_22)


        self.verticalLayout_25.addLayout(self.horizontalLayout_8)

        self.stackedWidget.addWidget(self.tabGradients)

        self.verticalLayout_3.addWidget(self.stackedWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 922, 33))
        MainWindow.setMenuBar(self.menubar)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(4)
        self.methodCombo.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"PyPROE", None))
        self.tabEditBtn.setText(QCoreApplication.translate("MainWindow", u"Design of Experiments", None))
        self.tabMMDBtn.setText(QCoreApplication.translate("MainWindow", u"Metamodeling", None))
        self.tabFormulationBtn.setText(QCoreApplication.translate("MainWindow", u"Formulation", None))
        self.tabOptBtn.setText(QCoreApplication.translate("MainWindow", u"Optimization", None))
        self.tabMatpltBtn.setText(QCoreApplication.translate("MainWindow", u"Plotting", None))
        self.tabGradientBtn.setText(QCoreApplication.translate("MainWindow", u"Gradients", None))
        self.tabWriterBtn.setText(QCoreApplication.translate("MainWindow", u"Writer", None))
        self.openDoeFile.setText(QCoreApplication.translate("MainWindow", u"Open DOE File", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Method", None))
#if QT_CONFIG(tooltip)
        self.methodCombo.setToolTip(QCoreApplication.translate("MainWindow", u"Choose a design method", None))
#endif // QT_CONFIG(tooltip)
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Variable Count", None))
#if QT_CONFIG(tooltip)
        self.designVarNum.setToolTip(QCoreApplication.translate("MainWindow", u"Enter a digit between 1 and 99", None))
#endif // QT_CONFIG(tooltip)
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Level Count", None))
#if QT_CONFIG(tooltip)
        self.levelCombo.setToolTip(QCoreApplication.translate("MainWindow", u"Enter a digit between 2 and 20.", None))
#endif // QT_CONFIG(tooltip)
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Data Points", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Function Count", None))
        self.doeDesignBtn.setText(QCoreApplication.translate("MainWindow", u"Get Design", None))
        self.doe_edit_vals.setText(QCoreApplication.translate("MainWindow", u"Edit Values", None))
        self.doe_add_point.setText(QCoreApplication.translate("MainWindow", u"Add Point", None))
        self.doe_clearBtn.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.doeMetamodel.setText(QCoreApplication.translate("MainWindow", u"Metamodel", None))
        self.doe_rmv_point.setText(QCoreApplication.translate("MainWindow", u"Delete Point", None))
        self.mmdFileLabel.setText(QCoreApplication.translate("MainWindow", u"No file selected.", None))
        self.mmdDoeButton.setText(QCoreApplication.translate("MainWindow", u"Open DOE File", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Method", None))
        self.text_2.setText(QCoreApplication.translate("MainWindow", u"Function", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Polynomial Order", None))
        self.oneFuncBtn.setText(QCoreApplication.translate("MainWindow", u"Generate", None))
        self.mmdFormBtn.setText(QCoreApplication.translate("MainWindow", u"Formulate", None))
        self.funcValBtn.setText(QCoreApplication.translate("MainWindow", u"Evaluate", None))
        self.clearDispBtn.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.mmdEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Metamodeling output is generated here.", None))
        self.optFileLabel.setText(QCoreApplication.translate("MainWindow", u"No file selected.", None))
        self.optFncBtn.setText(QCoreApplication.translate("MainWindow", u"Open FNC File", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"OPT Solver", None))
#if QT_CONFIG(tooltip)
        self.label_18.setToolTip(QCoreApplication.translate("MainWindow", u"Determines the number of equally spaced samples generated along each dimension in the grid. A higher grid size increases the number of guesses by creating a finer grid, while a lower grid size reduces the number of guesses by creating a coarser grid.", None))
#endif // QT_CONFIG(tooltip)
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"Grid Size", None))
#if QT_CONFIG(tooltip)
        self.mmdFuncCombo_2.setToolTip(QCoreApplication.translate("MainWindow", u"Defines the number of cycles the algorithm will run.", None))
#endif // QT_CONFIG(tooltip)
        self.mmdFuncCombo_2.setText(QCoreApplication.translate("MainWindow", u"Iterations/Generations", None))
#if QT_CONFIG(tooltip)
        self.opt_solverData.setToolTip("")
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.label_12.setToolTip(QCoreApplication.translate("MainWindow", u"Defines the lower bound for weights in weighted formulations.", None))
#endif // QT_CONFIG(tooltip)
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Min-Weight", None))
        self.weights.setText(QCoreApplication.translate("MainWindow", u"0.01", None))
#if QT_CONFIG(tooltip)
        self.label_21.setToolTip(QCoreApplication.translate("MainWindow", u"Defines the adjustment interval for weights.", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.label_21.setStatusTip("")
#endif // QT_CONFIG(statustip)
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"Weight Increment", None))
        self.weight_increment.setText(QCoreApplication.translate("MainWindow", u"0.01", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Population Size", None))
#if QT_CONFIG(tooltip)
        self.label_19.setToolTip(QCoreApplication.translate("MainWindow", u"Controls the probability of recombination.", None))
#endif // QT_CONFIG(tooltip)
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"Mutation Rate", None))
        self.mutation.setSuffix(QCoreApplication.translate("MainWindow", u"%", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"Crossover Rate", None))
        self.crossover.setSuffix(QCoreApplication.translate("MainWindow", u"%", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Partition Count", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Inner Divisions", None))
#if QT_CONFIG(tooltip)
        self.label_22.setToolTip(QCoreApplication.translate("MainWindow", u"Determines whether functions and gradients will be normalized before optimization.", None))
#endif // QT_CONFIG(tooltip)
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"Normalize function?", None))
        self.normalize_function.setCurrentText("")
        self.opt_clearBtn.setText(QCoreApplication.translate("MainWindow", u"Clear", None))
        self.optStopBtn.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.opt_startBtn.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.optEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Optimization output is generated here.", None))
        self.wrtEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Use this space as free thinking area.", None))
        self.form_load_file.setText(QCoreApplication.translate("MainWindow", u"Load FNC File", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Objective Functions (=)", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Variable Ranges (low, high)", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Equality Constraints (=)", None))
#if QT_CONFIG(tooltip)
        self.label_13.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Gradient Functions must be named after their associated variable (i.e., GF1-X1, GF2-X1)</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Inequality Constraints (<=)", None))
        self.form_constr_mods.setText(QCoreApplication.translate("MainWindow", u"Constraint Adjustments", None))
        self.form_grad_policy.setText(QCoreApplication.translate("MainWindow", u"Gradient Policy", None))
        self.view_latex.setText(QCoreApplication.translate("MainWindow", u"View LaTeX Equations", None))
        self.formResetEnv.setText(QCoreApplication.translate("MainWindow", u"Reset Environment", None))
        self.formOptBtn.setText(QCoreApplication.translate("MainWindow", u"Optimize", None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Function/Variable Name", None))
        self.formSaveBtn.setText(QCoreApplication.translate("MainWindow", u"Save", None))
        self.formNewBtn.setText(QCoreApplication.translate("MainWindow", u"New", None))
        self.formResetBtn.setText(QCoreApplication.translate("MainWindow", u"Reset", None))
        self.formFuncEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Define a function or variable here.", None))
        self.formFuncPreview.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Preview a function here", None))
        self.plotFileLabel.setText(QCoreApplication.translate("MainWindow", u"No file open.", None))
        self.plotOpenFile.setText(QCoreApplication.translate("MainWindow", u"Open FNC File", None))
        self.genPlot.setText(QCoreApplication.translate("MainWindow", u"Generate Contour", None))
        self.genSurface.setText(QCoreApplication.translate("MainWindow", u"Generate Surface", None))
        self.gradientOpenFile.setText(QCoreApplication.translate("MainWindow", u"Open FNC File", None))
        self.genBlankTemplate.setText(QCoreApplication.translate("MainWindow", u"Generate Blank Template", None))
        self.genGradientsBtn.setText(QCoreApplication.translate("MainWindow", u"Generate Gradients", None))
        self.normalizeFNC.setText(QCoreApplication.translate("MainWindow", u"Normalize", None))
        self.gradientOutput.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Gradients will be output here.", None))
    # retranslateUi

