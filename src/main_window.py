from PyQt6 import uic
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QIntValidator, QIcon
from PyQt6.QtWidgets import QMainWindow, QApplication

import resource_finder
from db_handler import DBHandler
from platform_list import PlatformList
from output_window import OutputWindow


class SIPPCompare(QMainWindow):
    def __init__(self):
        super().__init__()
        # Import Qt Designer UI XML file
        uic.loadUi(resource_finder.get_res_path("gui/main_gui.ui"), self)
        self.setWindowIcon(QIcon(resource_finder.get_res_path("icon2.ico")))

        ## Initialise class variables
        # Results
        self.fund_plat_fees     = 0.0
        self.fund_deal_fees     = 0.0
        self.share_plat_fees    = 0.0
        self.share_deal_fees    = 0.0
        self.results = []

        # Create window objects
        self.db = DBHandler()
        self.platform_list_win = PlatformList(self.db)
        if len(self.platform_list_win.plat_name_list) == 0:
            QTimer.singleShot(1, self.platform_list_win.show)
        self.output_win = None

        ## Handle events
        self.calc_but.clicked.connect(self.indicate_loading)
        # Menu bar entry (File -> Platform List)
        self.actionList_Platforms.triggered.connect(self.show_platform_list)
        # Update percentage mix label when slider moved
        self.mix_slider.valueChanged.connect(self.update_slider_lab)
        self.value_input.valueChanged.connect(self.check_valid)
        # Validate input
        self.share_trades_box.valueChanged.connect(self.check_valid)
        self.fund_trades_box.valueChanged.connect(self.check_valid)

        ## Restore last session
        prev_session_data = self.db.retrieve_user_details()
        if "NO_RECORD" not in prev_session_data:
            self.value_input.setValue(prev_session_data["pension_val"])
            self.mix_slider.setValue(prev_session_data["slider_val"])
            self.share_trades_box.setValue(prev_session_data["share_trades"])
            self.fund_trades_box.setValue(prev_session_data["fund_trades"])
            self.calc_but.setFocus()

    # Display slider position as mix between two nums (funds/shares)
    def update_slider_lab(self):
        slider_val = self.mix_slider.value()
        mix_lab_str = f"Investment mix (funds {slider_val}% / shares {100 - slider_val}%)"
        self.mix_lab.setText(mix_lab_str)

    # Ensure that trade fields aren't blank and pension value > 0
    def check_valid(self):
        if self.value_input.value() != 0:
            self.calc_but.setEnabled(True)
        else:
            self.calc_but.setEnabled(False)

    def indicate_loading(self):
        self.calc_but.setText("Working...")
        QTimer.singleShot(1, self.calculate_fees)

    # Calculate fees for all active platforms
    def calculate_fees(self):
        # Set to empty list each time to avoid persistence
        self.results = []

        # Get user input
        value_num = float(self.value_input.value())
        slider_val: int = self.mix_slider.value()
        fund_trades_num = int(self.fund_trades_box.value())
        share_trades_num = int(self.share_trades_box.value())
        shares_value = (1 - (slider_val / 100)) * value_num
        index = 0

        for platform in self.platform_list_win.plat_list:
            if not platform.enabled:
                continue

            fund_plat_fees = 0.0
            fund_deal_fees = 0.0
            share_plat_fees = 0.0
            share_deal_fees = 0.0
            plat_name = platform.plat_name
            if plat_name is None or plat_name == "":
                plat_name = f"Unnamed [ID: {index}]"

            if platform.fund_deal_fee is not None:
                fund_deal_fees = fund_trades_num * platform.fund_deal_fee

            funds_value = (slider_val / 100) * value_num
            for i in range(1, len(platform.fund_plat_fee[0])):
                band = platform.fund_plat_fee[0][i]
                prev_band = platform.fund_plat_fee[0][i - 1]
                fee = platform.fund_plat_fee[1][i]
                gap = (band - prev_band)

                if funds_value > gap:
                    fund_plat_fees += gap * (fee / 100)
                    funds_value -= gap
                else:
                    fund_plat_fees += funds_value * (fee / 100)
                    break

            if platform.share_plat_max_fee is not None:
                if (platform.share_plat_fee * shares_value / 12) > platform.share_plat_max_fee:
                    share_plat_fees = platform.share_plat_max_fee * 12
                else:
                    share_plat_fees = platform.share_plat_fee * shares_value

            if platform.share_deal_reduce_trades is not None:
                if (share_trades_num / 12) >= platform.share_deal_reduce_trades:
                    share_deal_fees = platform.share_deal_reduce_amount * share_trades_num
                else:
                    share_deal_fees = platform.share_deal_fee * share_trades_num

            self.results.append([fund_plat_fees, fund_deal_fees, share_plat_fees, share_deal_fees, plat_name])
            index += 1

        # Save details entered by user for next session
        self.db.write_user_details(value_num, slider_val, share_trades_num, fund_trades_num)
        self.show_output_win()

    # Show the output window - this func is called from calculate_fee()
    def show_output_win(self):
        # Refresh the results when new fees are calculated
        if self.output_win is None:
            self.output_win = OutputWindow()
        years = self.output_win.get_slider_position()
        self.output_win.display_output(self.results, years)
        self.calc_but.setText("Calculate")
        self.output_win.activateWindow()
        self.output_win.raise_()
        self.output_win.show()
        QApplication.alert(self.output_win)

    def show_platform_list(self):
        self.platform_list_win.show()
