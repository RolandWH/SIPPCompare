import datetime
import os

from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget

import resource_finder


class OutputWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Import Qt Designer UI XML file
        uic.loadUi(resource_finder.get_res_path("gui/output_window.ui"), self)
        self.setWindowIcon(QIcon(resource_finder.get_res_path("icon2.ico")))

    def display_output(self, results: list):
        ax = self.graphWidget.canvas.axes
        ax.clear()
        ax.cla()
        self.graphWidget.canvas.draw_idle()

        names = []
        values = []
        for result in results:
            names.append(result[4])
            values.append(sum(result[:4]))

        h_bars = ax.barh(names, values)
        ax.bar_label(h_bars, label_type='center', labels=[f"£{x:,.2f}" for x in h_bars.datavalues])
