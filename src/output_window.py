import os
from datetime import datetime

from PyQt6 import uic
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QFileDialog

import resource_finder
from widgets.mpl_widget import MplWidget


class OutputWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Import Qt Designer UI XML file
        uic.loadUi(resource_finder.get_res_path("gui/output_window.ui"), self)
        self.setWindowIcon(QIcon(resource_finder.get_res_path("icon2.ico")))

        # Define class variables
        self.canvas = self.graphWidget.canvas
        self.ax = self.canvas.axes
        self.fig = self.canvas.figure
        self.results = []

        # Handle events
        self.save_graph_but.clicked.connect(self.save_graph)
        self.time_slider.valueChanged.connect(self.change_time)

    def display_output(self, results: list, years: int):
        self.results = results
        self.ax.clear()
        self.ax.cla()
        self.canvas.draw_idle()

        names = []
        values = []
        for result in results:
            names.append(result[4])
            values.append(sum(result[:4]) * years)

        h_bars = self.ax.barh(names, values)
        self.ax.bar_label(h_bars, label_type='center', labels=[f"£{x:,.2f}" for x in h_bars.datavalues])

    def save_graph(self):
        file_picker = QFileDialog(self)
        file_picker.setFileMode(QFileDialog.FileMode.Directory)
        folder_path = ""
        if file_picker.exec():
            folder_path = file_picker.selectedFiles()[0]

        cur_time = datetime.now()
        filename_str = f"{folder_path}/SIPPCompare-{cur_time.year}.{cur_time.month}.{cur_time.day}.png"
        self.fig.savefig(filename_str, dpi=150)

    def change_time(self):
        years: int = self.time_slider.value()
        self.time_lab.setText(f"Fees over {years} year(s) (assuming no change in value)")
        self.display_output(self.results, years)
