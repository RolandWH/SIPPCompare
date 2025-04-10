from PyQt6.QtGui import QIntValidator, QIcon
from PyQt6.QtWidgets import QMainWindow, QWidget
from PyQt6 import uic

import output_window
import resource_finder


class SIPPCompare(QMainWindow):
    # Receive instance of PlatformEdit() as parameter
    def __init__(self, plat_edit_win: QWidget):
        super().__init__()
        # Import Qt Designer UI XML file
        uic.loadUi(resource_finder.get_res_path("gui/main_gui.ui"), self)
        self.setWindowIcon(QIcon(resource_finder.get_res_path("icon2.ico")))

        # Initialise class variables
        # Inputs
        self.optional_boxes             = []
        self.fund_plat_fee              = 0.0
        self.plat_name                  = ""
        self.fund_deal_fee              = 0.0
        self.share_plat_fee             = 0.0
        self.share_plat_max_fee         = 0.0
        self.share_deal_fee             = 0.0
        self.share_deal_reduce_trades   = 0.0
        self.share_deal_reduce_amount   = 0.0

        # Results
        self.fund_plat_fees     = 0.0
        self.fund_deal_fees     = 0.0
        self.share_plat_fees    = 0.0
        self.share_deal_fees    = 0.0

        # Create window objects
        self.platform_win = plat_edit_win
        self.output_win = output_window.OutputWindow()

        # Handle events
        self.calc_but.clicked.connect(self.calculate_fees)
        # Menu bar entry (File -> Edit Platforms)
        self.actionEdit_Platforms.triggered.connect(self.show_platform_edit)
        # Update percentage mix label when slider moved
        self.mix_slider.valueChanged.connect(self.update_slider_lab)
        self.value_input.valueChanged.connect(self.check_valid)
        self.share_trades_combo.currentTextChanged.connect(self.check_valid)
        self.fund_trades_combo.currentTextChanged.connect(self.check_valid)

        # Set validators
        self.share_trades_combo.setValidator(QIntValidator(0, 999))
        self.fund_trades_combo.setValidator(QIntValidator(0, 99))

    # Display slider position as mix between two nums (funds/shares)
    def update_slider_lab(self):
        slider_val = self.mix_slider.value()
        mix_lab_str = f"Investment mix (funds {slider_val}% / shares {100 - slider_val}%)"
        self.mix_lab.setText(mix_lab_str)

    def check_valid(self):
        if self.share_trades_combo.currentText() != "" \
        and self.fund_trades_combo.currentText() != "" \
        and self.value_input.value() != 0:
            self.calc_but.setEnabled(True)
        else:
            self.calc_but.setEnabled(False)

    # Get variables from platform editor input fields
    def init_variables(self):
        self.optional_boxes     = self.platform_win.get_optional_boxes()
        self.fund_plat_fee      = self.platform_win.get_fund_plat_fee()
        self.share_plat_fee     = self.platform_win.get_share_plat_fee()
        self.share_deal_fee     = self.platform_win.get_share_deal_fee()

        # TODO: This is HORRIBLE - find better way of doing it! (maybe enums?)
        if self.optional_boxes[0]:
            self.plat_name = self.platform_win.get_plat_name()
        else:
            self.plat_name = None

        if self.optional_boxes[1]:
            self.fund_deal_fee = self.platform_win.get_fund_deal_fee()
        else:
            self.fund_deal_fee = None

        if self.optional_boxes[2]:
            self.share_plat_max_fee = self.platform_win.get_share_plat_max_fee()
        else:
            self.share_plat_max_fee = None

        if self.optional_boxes[3]:
            self.share_deal_reduce_trades = self.platform_win.get_share_deal_reduce_trades()
        else:
            self.share_deal_reduce_trades = None

        if self.optional_boxes[4]:
            self.share_deal_reduce_amount = self.platform_win.get_share_deal_reduce_amount()
        else:
            self.share_deal_reduce_amount = None

    # Calculate fees
    def calculate_fees(self):
        self.init_variables()
        # Set to zero each time to avoid persistence
        self.fund_plat_fees = 0
        value_num = float(self.value_input.value())
        # Funds/shares mix
        slider_val: int = self.mix_slider.value()
        funds_value = (slider_val / 100) * value_num
        fund_trades_num = int(self.fund_trades_combo.currentText())
        if self.fund_deal_fee is not None:
            self.fund_deal_fees = fund_trades_num * self.fund_deal_fee

        for i in range(1, len(self.fund_plat_fee[0])):
            band = self.fund_plat_fee[0][i]
            prev_band = self.fund_plat_fee[0][i - 1]
            fee = self.fund_plat_fee[1][i]
            gap = (band - prev_band)

            if funds_value > gap:
                self.fund_plat_fees += gap * (fee / 100)
                funds_value -= gap
            else:
                self.fund_plat_fees += funds_value * (fee / 100)
                break

        shares_value = (1 - (slider_val / 100)) * value_num
        if self.share_plat_max_fee is not None:
            if (self.share_plat_fee * shares_value / 12) > self.share_plat_max_fee:
                self.share_plat_fees = self.share_plat_max_fee * 12
            else:
                self.share_plat_fees = self.share_plat_fee * shares_value

        share_trades_num = int(self.share_trades_combo.currentText())
        if self.share_deal_reduce_trades is not None:
            if (share_trades_num / 12) >= self.share_deal_reduce_trades:
                self.share_deal_fees = self.share_deal_reduce_amount * share_trades_num
            else:
                self.share_deal_fees = self.share_deal_fee * share_trades_num

        self.show_output_win()

    # Show the output window - this func is called from calculate_fee()
    def show_output_win(self):
        # Refresh the results when new fees are calculated
        self.output_win.display_output(self.fund_plat_fees, self.fund_deal_fees,
                                       self.share_plat_fees, self.share_deal_fees,
                                       self.plat_name
                                       )
        self.output_win.show()

    # Show the platform editor window (currently run-time only)
    def show_platform_edit(self):
        self.platform_win.show()
