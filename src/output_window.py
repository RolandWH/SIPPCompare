from PyQt6.QtWidgets import QWidget
from PyQt6 import uic

import datetime
import os


class OutputWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("gui/output_window.ui", self)

        # Initialise class variables
        self.results_str = ""
        self.platform_name = ""

        # Handle events
        self.res_save_but.clicked.connect(self.save_results)

    def save_results(self):
        # Use datatime for txt filename
        cur_time = datetime.datetime.now()
        if not os.path.exists("output"):
            os.makedirs("output")
        filename_str = f"output/{self.platform_name}-{cur_time.year}.{cur_time.month}.{cur_time.day}.txt"
        output_file = open(filename_str, "wt")
        output_file.write(self.results_str)

    # Display fees in output window as plaintext readout
    def display_output(self, fund_plat_fees: float, fund_deal_fees: float,
                       share_plat_fees: float, share_deal_fees: float, plat_name: str):
        self.platform_name = plat_name
        self.results_str = f"Fees breakdown (Platform \"{self.platform_name}\"):"

        self.results_str += "\n\nPlatform fees:"
        # :.2f is used in order to display 2 decimal places (currency form)
        self.results_str += f"\n\tFund platform fees: £{round(fund_plat_fees, 2):.2f}"
        self.results_str += f"\n\tShare platform fees: £{round(share_plat_fees, 2):.2f}"
        total_plat_fees = fund_plat_fees + share_plat_fees
        self.results_str += f"\n\tTotal platform fees: £{round(total_plat_fees, 2):.2f}"

        self.results_str += "\n\nDealing fees:"
        self.results_str += f"\n\tFund dealing fees: £{round(fund_deal_fees, 2):.2f}"
        self.results_str += f"\n\tShare dealing fees: £{round(share_deal_fees, 2):.2f}"
        total_deal_fees = fund_deal_fees + share_deal_fees
        self.results_str += f"\n\tTotal dealing fees: £{round(total_deal_fees, 2):.2f}"

        total_fees = total_plat_fees + total_deal_fees
        self.results_str += f"\n\nTotal fees: £{round(total_fees, 2):.2f}"

        self.output.setText(self.results_str)
