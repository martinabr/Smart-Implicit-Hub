from PyQt5 import QtCore, QtGui, QtWidgets
from module import Ui_module
import glob
from pathlib import Path
import os


__copyright__ = "Copyright 2019, RISE Research Institutes of Sweden"
__author__ = "Naveed Anwar Bhatti and Martina Brachmann"


class mainmodule(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.parent = parent
        self.ui = Ui_module()
        self.ui.setupUi(self)
        self.selected_module = ""

        modules = glob.glob(os.path.join("Modules", "*.py"))  # Add all python files in Module directory as items

        for module in modules:
            item = QtWidgets.QListWidgetItem(module)  # create an item with a caption
            self.ui.listWidget.addItem(item)
            # item.setCheckable(True)  # add a checkbox to it
            # model.appendRow(item)  # Add the item to the model

        # self.listWidget.setModel(model)  # Apply the model to the list view
        self.ui.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.ui.saveModules.clicked.connect(self.return_modules)

    def return_modules(self):
        items = self.ui.listWidget.selectedItems()
        x = []
        for i in range(len(items)):
            x.append(str(self.ui.listWidget.selectedItems()[i].text()))
        if len(items)>0:
            if "/" in x[0]:
               self.selected_module = str(x[0]).split("/")[1].split(".")[0]
               print(x[0])
            else:
                self.selected_module = str(x[0]).split("\\")[1].split(".")[0]
                print(x[0])
        self.parent.selected_module=self.selected_module
        self.close()
