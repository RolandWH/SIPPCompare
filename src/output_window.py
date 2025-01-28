from PyQt6.QtWidgets import QWidget
from PyQt6 import uic

class OutputWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("gui/output_window.ui", self)

    def display_output(self, fund_plat_fees: float, fund_deal_fees: float,
                       share_plat_fees: float, share_deal_fees: float):
        results_str = "Fees breakdown:"

        results_str += "\n\nPlatform fees:"
        results_str += f"\n\tFund platform fees: £{round(fund_plat_fees, 2):.2f}"
        results_str += f"\n\tShare platform fees: £{round(share_plat_fees, 2):.2f}"
        total_plat_fees = fund_plat_fees + share_plat_fees
        results_str += f"\n\tTotal platform fees: £{round(total_plat_fees, 2):.2f}"

        results_str += "\n\nDealing fees:"
        results_str += f"\n\tFund dealing fees: £{round(fund_deal_fees, 2):.2f}"
        results_str += f"\n\tShare dealing fees: £{round(share_deal_fees, 2):.2f}"
        total_deal_fees = fund_deal_fees + share_deal_fees
        results_str += f"\n\tTotal dealing fees: £{round(total_deal_fees, 2):.2f}"

        total_fees = total_plat_fees + total_deal_fees
        results_str += f"\n\nTotal fees: £{round(total_fees, 2):.2f}"

        self.output.setText(results_str)
