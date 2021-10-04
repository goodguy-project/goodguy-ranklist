import asyncio
import json
import logging
import os
import sys
from functools import partial
from typing import List, Dict, Callable

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
    QHeaderView,
)
from PyQt5.QtCore import Qt

from crawl_service.crawl_service_impl import CrawlServiceImpl
from crawl_service.crawl_service_pb2 import (
    GetUserContestRecordRequest,
    GetRecentContestRequest,
    GetUserSubmitRecordRequest,
)
from crawl_service.util.go import go

from const import ROOT

DATA_PATH = os.path.join(ROOT, 'manager', '.json')
TEXT_FONT = QFont()
TEXT_FONT.setPointSize(12)


@go(daemon=True)
def rating_crawler(platform: str, name: str, func: Callable) -> None:
    func('Loading...')
    try:
        data = CrawlServiceImpl.GetUserContestRecord(GetUserContestRecordRequest(
            platform=platform,
            handle=name,
        ), None)
        func(data.rating)
    except Exception as e:
        logging.exception(e)
        func('CRAWLING FAILED')


@go(daemon=True)
def length_crawler(platform: str, name: str, func: Callable) -> None:
    func('Loading...')
    try:
        data = CrawlServiceImpl.GetUserContestRecord(GetUserContestRecordRequest(
            platform=platform,
            handle=name,
        ), None)
        func(data.length)
    except Exception as e:
        logging.exception(e)
        func('CRAWLING FAILED')


@go(daemon=True)
def count_crawler(platform: str, name: str, func: Callable) -> None:
    func('Loading...')
    try:
        data = CrawlServiceImpl.GetUserSubmitRecord(GetUserSubmitRecordRequest(
            platform=platform,
            handle=name,
        ), None)
        func(f'{data.accept_count}/{data.submit_count}')
    except Exception as e:
        logging.exception(e)
        func('CRAWLING FAILED')


class RanklistTableGUI(QTableWidget):
    def __init__(self):
        super().__init__()
        self.__column = [
            'name',
            'atcoder', 'atcoder rating', 'atcoder 场次',
            'codeforces', 'codeforces rating', 'codeforces 场次', 'codeforces 做题数',
            'nowcoder', 'nowcoder rating', 'nowcoder 场次',
            'leetcode', 'leetcode rating', 'leetcode 场次',
            'luogu', 'luogu 做题数',
            'vjudge', 'vjudge 做题数',
        ]
        self.__column_map = {v: i for i, v in enumerate(self.__column)}
        print(self.__column_map)
        self.setColumnCount(len(self.__column))
        self.setHorizontalHeaderLabels(self.__column)
        self.setFont(TEXT_FONT)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.reload()

    def reload(self):
        self.setRowCount(0)
        try:
            with open(DATA_PATH, 'r', encoding='utf-8') as file:
                data: List[Dict[str, str]] = json.loads(file.read())
            self.setRowCount(len(data))
            # data
            for row, people in enumerate(data):
                for oj, value in people.items():
                    if not value:
                        continue
                    col = self.__column_map[oj]
                    self.setItem(row, col, QTableWidgetItem(value))
                    if oj == 'name':
                        continue
                    # rating
                    rating_col = self.__column_map.get(f'{oj} rating')
                    if rating_col:
                        rating_crawler(oj, value, partial(self.set_string_item, row=row, col=rating_col))
                    # length
                    length_col = self.__column_map.get(f'{oj} 场次')
                    if length_col:
                        length_crawler(oj, value, partial(self.set_string_item, row=row, col=length_col))
                    # count
                    count_col = self.__column_map.get(f'{oj} 做题数')
                    if count_col:
                        count_crawler(oj, value, partial(self.set_string_item, row=row, col=count_col))
        except FileNotFoundError:
            pass

    def set_string_item(self, value, row: int, col: int):
        self.setItem(row, col, QTableWidgetItem(str(value)))


class RankListGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1024, 768)
        self.setWindowTitle('Friend Ranklist')
        layout = QVBoxLayout()
        table = RanklistTableGUI()
        layout.addWidget(table)
        self.setLayout(layout)


if __name__ == '__main__':
    APP = QApplication(sys.argv)
    GUI = RankListGUI()
    GUI.show()
    sys.exit(APP.exec_())
