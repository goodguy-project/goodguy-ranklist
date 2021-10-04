import json
import os
import sys
from functools import partial
from typing import List, Dict

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QTableWidget,
    QVBoxLayout,
    QTableWidgetItem,
    QAbstractItemView,
    QPushButton,
    QLabel,
    QLineEdit,
)
from PyQt5.QtCore import Qt
from pydantic import BaseModel

from const import ROOT

DATA_PATH = os.path.join(ROOT, 'manager', '.json')
TEXT_FONT = QFont()
TEXT_FONT.setPointSize(12)


class UpdateObject(BaseModel):
    confirm: bool = False
    index: int = -1
    data: Dict[str, str] = {}


class UpdateDialog(QWidget):
    def __init__(self, p: 'TableGUI', columns: List[str]):
        super().__init__()
        self.setFont(TEXT_FONT)
        self.__obj = UpdateObject()
        self.__parent = p
        self.__editor: Dict[str, QLineEdit] = {}
        layout = QVBoxLayout()
        for column in columns:
            label = QLabel(f'{column}:')
            editor = QLineEdit()
            layout.addWidget(label)
            layout.addWidget(editor)
            self.__editor[column] = editor
        button_ok = QPushButton('OK')
        button_ok.clicked.connect(self.__confirm)
        layout.addWidget(button_ok)
        self.setLayout(layout)
        # 锁定主QWidget
        self.setWindowModality(Qt.ApplicationModal)

    def call(self, index: int, data: Dict[str, str]):
        self.__obj = UpdateObject()
        self.__obj.index = index
        for editor in self.__editor.values():
            editor.setText('')
        for column, value in data.items():
            self.__editor[column].setText(value)
        self.show()

    def __confirm(self):
        self.__obj.confirm = True
        self.__obj.data = {column: editor.text() for column, editor in self.__editor.items()}
        self.setVisible(False)
        self.__parent.data_update(self.__obj)


class TableGUI(QTableWidget):
    def __init__(self, table_path: str):
        super().__init__()
        self.__column = ['name', 'atcoder', 'codeforces', 'nowcoder', 'leetcode', 'luogu', 'vjudge']
        self.__operator = {'delete': self.__delete, 'update': self.__update}
        self.__header_label = self.__column + list(self.__operator.keys())
        self.__header_label_map = {v: i for i, v in enumerate(self.__header_label)}
        self.__table_path = table_path
        self.__data: List[Dict[str, str]] = []
        self.dialog = UpdateDialog(self, self.__column)
        self.setFont(TEXT_FONT)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.reload()

    def reload(self):
        self.setColumnCount(len(self.__header_label))
        self.setHorizontalHeaderLabels(self.__header_label)
        self.setRowCount(0)
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as file:
                self.__data: List[Dict[str, str]] = json.loads(file.read())
            length = len(self.__data)
            self.setRowCount(length)
            # data
            for row, people in enumerate(self.__data):
                for key, value in people.items():
                    col = self.__header_label_map[key]
                    self.setItem(row, col, QTableWidgetItem(value))
            # delete
            for row in range(length):
                col = self.__header_label_map['delete']
                button = QPushButton('delete')
                button.clicked.connect(partial(self.__delete, index=row))
                self.setCellWidget(row, col, button)
            # update
            for row in range(length):
                col = self.__header_label_map['update']
                button = QPushButton('update')
                button.clicked.connect(partial(self.__update, index=row))
                self.setCellWidget(row, col, button)
        except FileNotFoundError:
            pass

    def __delete(self, index: int):
        self.__data.pop(index)
        self.__save()
        self.reload()

    def __save(self):
        with open(self.__table_path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(self.__data))

    def __update(self, index: int):
        self.dialog.call(index, self.__data[index])

    def data_update(self, update_object: UpdateObject):
        if update_object.confirm:
            if update_object.index == -1:
                self.__data.append(update_object.data)
            else:
                self.__data[update_object.index] = update_object.data
            self.__save()
            self.reload()


class RankListGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Friend Manager')
        layout = QVBoxLayout()
        table = TableGUI(DATA_PATH)
        layout.addWidget(table)
        button_add = QPushButton('Add')
        button_add.clicked.connect(partial(table.dialog.call, index=-1, data={}))
        button_add.setFont(TEXT_FONT)
        layout.addWidget(button_add)
        self.setLayout(layout)
        self.resize(1024, 768)


if __name__ == '__main__':
    APP = QApplication(sys.argv)
    GUI = RankListGUI()
    GUI.show()
    sys.exit(APP.exec_())
