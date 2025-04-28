import os
from datetime import datetime

from PyQt6 import uic
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QWidget, QFileDialog, QMessageBox, QDialogButtonBox

import resource_finder


class SaveFailure(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(resource_finder.get_res_path("icon2.ico")))
        self.setWindowTitle("Save failure")

        self.setIcon(QMessageBox.Icon.Critical)
        font = QFont()
        font.setPointSize(11)
        self.setFont(font)
        self.setText("Failed to save file")
        self.setDetailedText(
            "This could be due to a permissions issue, or the file being in use by another process"
        )

        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        font.setPointSize(10)
        self.findChild(QDialogButtonBox).setFont(font)


class OutputWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Import Qt Designer UI XML file
        uic.loadUi(resource_finder.get_res_path("gui/output_window.ui"), self)
        self.setWindowIcon(QIcon(resource_finder.get_res_path("icon2.ico")))

        # Define class variables
        self.save_err_dialog = SaveFailure()
        self.canvas = self.graphWidget.canvas
        self.ax = self.canvas.axes
        self.fig = self.canvas.figure
        self.results = []

        # Handle events
        self.save_graph_but.clicked.connect(self.save_graph)
        self.save_csv_but.clicked.connect(self.save_csv)
        self.time_slider.valueChanged.connect(self.change_time)

    def get_slider_position(self) -> int:
        return self.time_slider.value()

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

        names = sorted(names, key=lambda x: values[names.index(x)], reverse=True)
        values = sorted(values, reverse=True)

        h_bars = self.ax.barh(names, values)
        self.ax.bar_label(h_bars, label_type='center', labels=[f"£{x:,.2f}" for x in h_bars.datavalues])

    def save_graph(self):
        file_picker = QFileDialog(self)
        file_picker.setFileMode(QFileDialog.FileMode.AnyFile)
        file_picker.setDefaultSuffix("png")
        file_picker.setWindowTitle("Save results as PNG")
        file_picker.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_picker.setNameFilter("*.png")
        file_path = ""
        cur_time = datetime.now()
        filename_str = f"{file_path}/SIPPCompare-{cur_time.year}.{cur_time.month}.{cur_time.day}.png"
        file_picker.selectFile(filename_str)
        if file_picker.exec():
            file_path = file_picker.selectedFiles()[0]

        try:
            self.fig.savefig(file_path, dpi=150)
        except OSError:
            self.save_err_dialog.exec()

    def save_csv(self):
        # TODO: Sort CSV output, either alphabetically or by total fees
        file_picker = QFileDialog(self)
        file_picker.setFileMode(QFileDialog.FileMode.AnyFile)
        file_picker.setDefaultSuffix("csv")
        file_picker.setWindowTitle("Save results as CSV")
        file_picker.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        file_picker.setNameFilter("*.csv")
        file_path = ""
        cur_time = datetime.now()
        filename_str = f"{file_path}/SIPPCompare-{cur_time.year}.{cur_time.month}.{cur_time.day}.csv"
        file_picker.selectFile(filename_str)
        if file_picker.exec():
            file_path = file_picker.selectedFiles()[0]

        try:
            csvfile = open(file_path, "wt")
            csv_string = (
                "Platform Name,Fund Platform Fee,Share Platform Fee,Fund Dealing Fee,"
                "Share Dealing Fee,Total Platform Fees,Total Dealing Fees,Total Fund Fees,"
                "Total Share Fees,Total Fees"
            )

            for result in self.results:
                csv_string += '\n'
                pn = result[4]
                fpf = result[0]
                spf = result[2]
                fdf = result[1]
                sdf = result[3]

                tpf = fpf + spf
                tdf = sdf + fdf

                tff = fpf + fdf
                tsf = spf + sdf
                tf = tff + tsf
                csv_string += (
                    f"{pn},\"£{fpf:,.2f}\",\"£{spf:,.2f}\",\"£{fdf:,.2f}\",\"£{sdf:,.2f}\","
                    f"\"£{tpf:,.2f}\",\"£{tdf:,.2f}\",\"£{tff:,.2f}\",\"£{tsf:,.2f}\",\"£{tf:,.2f}\""
                )

            csvfile.write(csv_string)
            csvfile.close()
        except OSError:
            self.save_err_dialog.exec()

    def change_time(self):
        years: int = self.time_slider.value()
        self.time_lab.setText(f"Fees over {years} year(s) (assuming no change in value)")
        self.display_output(self.results, years)
