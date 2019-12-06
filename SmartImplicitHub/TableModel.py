import pandas as pd

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (Qt, pyqtSignal)


__copyright__ = "Copyright 2019, RISE Research Institutes of Sweden"
__author__ = "Naveed Anwar Bhatti and Martina Brachmann"


class PandasModel(QtCore.QAbstractTableModel):
    # parameters: value (bool), ip (str), host (str)
    pandas_signal = QtCore.pyqtSignal(object, object, object)

    def __init__(self, df = pd.DataFrame(), parent=None, checkbox=None, signal_values_of_interest=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._df = df
        self.checkbox_column = checkbox # The row which has a
        self.signal_values_of_interest = signal_values_of_interest

        if self.signal_values_of_interest is not None:
            if len(self.signal_values_of_interest) == 2:
                self.signal_values_of_interest = signal_values_of_interest
            else:
                print("WARNING: Adjust QtCore.pyqtSignal(object, object, object) for more")
                return

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if orientation == QtCore.Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()
        elif orientation == QtCore.Qt.Vertical:
            try:
                return self._df.index.tolist()[section]
            except (IndexError, ):
                return QtCore.QVariant()

    def update(self):
        print(self._df)
        self.layoutChanged.emit()

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        return QtCore.QVariant(str(self._df.ix[index.row(), index.column()])) #Most of the errors comes from this line

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if self.checkbox_column is not None:
            if index.column() == self.checkbox_column:
                self.dataChanged(index, value)
        self._df.at[row, col] = value
        return True

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending= order == QtCore.Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()

    def dataChanged(self, index, value, role=QtCore.Qt.DisplayRole):
        row = self._df.index[index.row()]
        if self.signal_values_of_interest is not None:
            self.pandas_signal.emit(value, self._df.loc[row, self.signal_values_of_interest[0]], self._df.loc[row, self.signal_values_of_interest[1]])

    def flags(self, index):
        if self.checkbox_column is not None:
            if index.column() == self.checkbox_column:
                return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled
            else:
                return QtCore.Qt.ItemIsEnabled
        else:
            return QtCore.Qt.ItemIsSelectable

    def print_df(self):
        print(id(self._df))
        print(self._df)


class CheckBoxDelegate(QtWidgets.QItemDelegate):
    """
    A delegate that places a fully functioning QCheckBox cell of the column to which it's applied.
    """
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)

    def createEditor(self, parent, option, index):
        """
        Important, otherwise an editor is created if the user clicks in this cell.
        """
        return None

    def paint(self, painter, option, index):
        """
        Paint a checkbox without the label.
        """
        check_box_style_option = QtWidgets.QStyleOptionViewItem()
        check_box_style_option.rect = self.getCheckBoxRect(option)

        self.drawCheck(painter, check_box_style_option, check_box_style_option.rect, QtCore.Qt.Unchecked if int(index.data()) == 0 else QtCore.Qt.Checked)

    def editorEvent(self, event, model, option, index):
        """
        Change the data in the model and the state of the checkbox
        if the user presses the left mousebutton and this cell is editable. Otherwise do nothing.
        """
        if not int(index.flags() & QtCore.Qt.ItemIsEditable) > 0:
            return False

        if event.type() == QtCore.QEvent.MouseButtonRelease and event.button() == QtCore.Qt.LeftButton:
            # Change the checkbox-state
            self.setModelData(None, model, index)
            return True

        return False

    def setModelData (self, editor, model, index):
        """
        The user wanted to change the old state in the opposite.
        """
        model.setData(index, 1 if int(index.data()) == 0 else 0, QtCore.Qt.EditRole)

    def getCheckBoxRect(self, option):
        check_box_style_option = QtWidgets.QStyleOptionButton()
        check_box_rect = QtWidgets.QApplication.style().subElementRect(QtWidgets.QStyle.SE_CheckBoxIndicator, check_box_style_option, None)
        check_box_point = QtCore.QPoint(option.rect.x() +
                            option.rect.width() / 2 -
                            check_box_rect.width() / 2,
                            option.rect.y() +
                            option.rect.height() / 2 -
                            check_box_rect.height() / 2)
        return QtCore.QRect(check_box_point, check_box_rect.size())


