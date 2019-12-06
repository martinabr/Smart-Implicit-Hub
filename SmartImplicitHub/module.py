# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'module.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import sys



class Ui_module(object):
    def setupUi(self, module):
        module.setObjectName("module")
        module.resize(279, 300)
        self.saveModules = QtWidgets.QPushButton(module)
        self.saveModules.setGeometry(QtCore.QRect(100, 270, 75, 23))
        self.saveModules.setObjectName("saveModules")
        self.label = QtWidgets.QLabel(module)
        self.label.setGeometry(QtCore.QRect(10, 10, 81, 16))
        self.label.setObjectName("label")
        self.listWidget = QtWidgets.QListWidget(module)
        self.listWidget.setGeometry(QtCore.QRect(10, 30, 261, 231))
        self.listWidget.setObjectName("listWidget")



        self.retranslateUi(module)
        QtCore.QMetaObject.connectSlotsByName(module)




    def retranslateUi(self, module):
        _translate = QtCore.QCoreApplication.translate
        module.setWindowTitle(_translate("module", "Module Selection"))
        self.saveModules.setText(_translate("module", "Save"))
        self.label.setText(_translate("module", "Select Modules"))

