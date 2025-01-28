from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic
import platform_edit
import output_window


class SIPPCompare(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("gui/main_gui.ui", self)

        # Define class variables
        self.tiered_fees = [
            [0,     250000,     1000000,    2000000],
            [0,     0.25,       0.1,        0.05]
        ]
        self.fund_deal_fee = 1.5
        self.share_plat_fee = 0.0025
        self.share_plat_max_fee = 3.5
        self.share_deal_fee = 5
        self.share_deal_reduce_trades = 10
        self.share_deal_reduce_amount = 3.5

        self.result = None
        self.platform_win = None
        self.output_win = None

        # Handle events
        self.calc_but.clicked.connect(self.calculate_fee)
        self.actionEdit_Platforms.triggered.connect(self.show_platform_edit)
        self.mix_slider.valueChanged.connect(self.update_slider_lab)

    # Display slider position as mix between two nums (funds/shares)
    def update_slider_lab(self):
        slider_val = self.mix_slider.value()
        self.mix_lab.setText(f"Investment mix (funds {slider_val}% / shares {100 - slider_val}%)")
        #mix_percent_lab_str = f"{slider_val}% / {100 - slider_val}%"
        #self.mix_percent_lab.setText(mix_percent_lab_str)

    # Calculate fees
    def calculate_fee(self):
        value_num = float(self.value_input.text()[1:])
        slider_val = self.mix_slider.value()
        funds_value = (slider_val / 100) * value_num
        fund_trades_num = int(self.fund_trades_combo.currentText())
        fund_deal_fees = fund_trades_num * self.fund_deal_fee
        fund_plat_fees = 0
        remaining = funds_value

        for i in range(1, len(self.tiered_fees[0])):
            band = self.tiered_fees[0][i]
            prev_band = self.tiered_fees[0][i - 1]
            fee = self.tiered_fees[1][i]
            gap = (band - prev_band)

            if remaining > gap:
                fund_plat_fees += gap * (fee / 100)
                remaining -= gap
            else:
                fund_plat_fees += remaining * (fee / 100)
                break

        shares_value = (1 - (slider_val / 100)) * value_num
        share_plat_fees = self.share_plat_fee * shares_value
        if (share_plat_fees / 12) > self.share_plat_max_fee:
            share_plat_fees = self.share_plat_max_fee * 12
        share_trades_num = int(self.share_trades_combo.currentText())
        share_deal_fees = self.share_deal_fee * share_trades_num
        if (share_trades_num / 12) > self.share_deal_reduce_trades:
            share_deal_fees = self.share_deal_reduce_amount * share_trades_num

        self.show_output_win(fund_plat_fees, fund_deal_fees, share_plat_fees, share_deal_fees)

    # Show the output window - this func is called from calculate_fee()
    def show_output_win(self, fund_plat_fees, fund_deal_fees, share_plat_fees, share_deal_fees):
        # Check window isn't already open
        if self.output_win is None:
            self.output_win = output_window.OutputWindow()
        # Refresh the results when new fees are calculated
        self.output_win.display_output(fund_plat_fees, fund_deal_fees, share_plat_fees, share_deal_fees)
        self.output_win.show()

    # Show the platform editor window (currently useless)
    def show_platform_edit(self):
        # Check window isn't already open
        if self.platform_win is None:
            self.platform_win = platform_edit.PlatformEdit()
        self.platform_win.show()
