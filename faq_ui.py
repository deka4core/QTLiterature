# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'faq_ui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FAQ(object):
    def setupUi(self, FAQ):
        FAQ.setObjectName("FAQ")
        FAQ.resize(766, 450)
        self.widget = QtWidgets.QWidget(FAQ)
        self.widget.setGeometry(QtCore.QRect(10, 0, 751, 441))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.widget)
        font = QtGui.QFont()
        font.setFamily("Clear Sans")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.faqTextEdit = QtWidgets.QPlainTextEdit(self.widget)
        font = QtGui.QFont()
        font.setFamily("Clear Sans")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.faqTextEdit.setFont(font)
        self.faqTextEdit.setReadOnly(True)
        self.faqTextEdit.setObjectName("faqTextEdit")
        self.gridLayout.addWidget(self.faqTextEdit, 1, 0, 1, 1)

        self.retranslateUi(FAQ)
        QtCore.QMetaObject.connectSlotsByName(FAQ)

    def retranslateUi(self, FAQ):
        _translate = QtCore.QCoreApplication.translate
        FAQ.setWindowTitle(_translate("FAQ", "FAQ"))
        self.label.setText(_translate("FAQ", "СПРАВКА"))
