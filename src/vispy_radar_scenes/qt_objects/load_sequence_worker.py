#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Loads RadarScenes data and provides to Qt nodes
"""

import sys

from PyQt5 import QtCore
from radar_scenes.sequence import Sequence


class LoadSequenceWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    loading_done = QtCore.pyqtSignal(object, object)
    loading_failed = QtCore.pyqtSignal()

    def __init__(self, filename):
        super().__init__()
        self.filename = filename

    def load(self):
        try:
            sequence = Sequence.from_json(self.filename)
            cur_timestamp = sequence.first_timestamp
            timestamps = [cur_timestamp]
            while True:
                cur_timestamp = sequence.next_timestamp_after(cur_timestamp)
                if cur_timestamp is None:
                    break
                timestamps.append(cur_timestamp)
            self.loading_done.emit(sequence, timestamps)

            self.finished.emit()
        except:
            (type_, value, traceback) = sys.exc_info()
            sys.excepthook(type_, value, traceback)
            self.loading_failed.emit()
            self.finished.emit()
