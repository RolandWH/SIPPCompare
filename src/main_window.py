from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic

import output_window


class SIPPCompare(QMainWindow):
    # Receive instance of PlatformEdit() as parameter
    def __init__(self, plat_edit_win):
        super().__init__()
        uic.loadUi("gui/main_gui.ui", self)

        # Initialise class variables
        self.fund_plat_fee              = 0.0
        self.plat_name                  = ""
        self.fund_deal_fee              = 0.0
        self.share_plat_fee             = 0.0
        self.share_plat_max_fee         = 0.0
        self.share_deal_fee             = 0.0
        self.share_deal_reduce_trades   = 0.0
        self.share_deal_reduce_amount   = 0.0

        self.fund_plat_fees     = 0.0
        self.fund_deal_fees     = 0.0
        self.share_plat_fees    = 0.0
        self.share_deal_fees    = 0.0

        # Create window objects
        self.platform_win = plat_edit_win
        self.output_win = output_window.OutputWindow()

        # Handle events
        self.calc_but.clicked.connect(self.calculate_fees)
        self.actionEdit_Platforms.triggered.connect(self.show_platform_edit)
        self.mix_slider.valueChanged.connect(self.update_slider_lab)

    # Display slider position as mix between two nums (funds/shares)
    def update_slider_lab(self):
        slider_val = self.mix_slider.value()
        mix_lab_str = f"Investment mix (funds {slider_val}% / shares {100 - slider_val}%)"
        self.mix_lab.setText(mix_lab_str)

    # Get local variables from user input
    def init_variables(self):
        self.plat_name                  = self.platform_win.get_plat_name()
        self.fund_plat_fee              = self.platform_win.get_fund_plat_fee()
        self.fund_deal_fee              = self.platform_win.get_fund_deal_fee()
        self.share_plat_fee             = self.platform_win.get_share_plat_fee()
        self.share_plat_max_fee         = self.platform_win.get_share_plat_max_fee()
        self.share_deal_fee             = self.platform_win.get_share_deal_fee()
        self.share_deal_reduce_trades   = self.platform_win.get_share_deal_reduce_trades()
        self.share_deal_reduce_amount   = self.platform_win.get_share_deal_reduce_amount()

    # Calculate fees
    def calculate_fees(self):
        self.init_variables()
        self.fund_plat_fees = 0
        value_num = float(self.value_input.text()[1:]) # Filter out '£' symbol
        slider_val = self.mix_slider.value()
        funds_value = (slider_val / 100) * value_num
        fund_trades_num = int(self.fund_trades_combo.currentText())
        self.fund_deal_fees = fund_trades_num * self.fund_deal_fee
        remaining = funds_value

        for i in range(1, len(self.fund_plat_fee[0])):
            band = self.fund_plat_fee[0][i]
            prev_band = self.fund_plat_fee[0][i - 1]
            fee = self.fund_plat_fee[1][i]
            gap = (band - prev_band)

            if remaining > gap:
                self.fund_plat_fees += gap * (fee / 100)
                remaining -= gap
            else:
                self.fund_plat_fees += remaining * (fee / 100)
                break

        shares_value = (1 - (slider_val / 100)) * value_num
        if (self.share_plat_fee * shares_value / 12) > self.share_plat_max_fee:
            self.share_plat_fees = self.share_plat_max_fee * 12
        else:
            self.share_plat_fees = self.share_plat_fee * shares_value

        share_trades_num = int(self.share_trades_combo.currentText())
        if (share_trades_num / 12) >= self.share_deal_reduce_trades:
            self.share_deal_fees = self.share_deal_reduce_amount * share_trades_num
        else:
            self.share_deal_fees = self.share_deal_fee * share_trades_num

        self.show_output_win()

    # Show the output window - this func is called from calculate_fee()
    def show_output_win(self):
        # Refresh the results when new fees are calculated
        self.output_win.display_output(self.fund_plat_fees, self.fund_deal_fees,
                                       self.share_plat_fees, self.share_deal_fees, self.plat_name)
        self.output_win.show()

    # Show the platform editor window (currently run-time only)
    def show_platform_edit(self):
        self.platform_win.show()
