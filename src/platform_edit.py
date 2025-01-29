from PyQt6.QtWidgets import QWidget
from PyQt6 import uic


class PlatformEdit(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("gui/platform_edit.ui", self)

        self.fund_plat_fee = [
            [0, 250000, 1000000, 2000000],
            [0, 0.25, 0.1, 0.05]
        ]
        self.fund_deal_fee = 0.0
        self.share_plat_fee = 0.0
        self.share_plat_max_fee = 0.0
        self.share_deal_fee = 0.0
        self.share_deal_reduce_trades = 0.0
        self.share_deal_reduce_amount = 0.0

        self.save_but.clicked.connect(self.init_variables)

    def init_variables(self):
        self.fund_deal_fee = float(self.fund_deal_fee_box.text())
        self.share_plat_fee = float(self.share_plat_fee_box.text()) / 100
        self.share_plat_max_fee = float(self.share_plat_max_fee_box.text())
        self.share_deal_fee = float(self.share_deal_fee_box.text())
        self.share_deal_reduce_trades = float(self.share_deal_reduce_trades_box.text())
        self.share_deal_reduce_amount = float(self.share_deal_reduce_amount_box.text())

    def get_fund_plat_fee(self):
        return self.fund_plat_fee

    def get_fund_deal_fee(self):
        return self.fund_deal_fee

    def get_share_plat_fee(self):
        return self.share_plat_fee

    def get_share_plat_max_fee(self):
        return self.share_plat_max_fee

    def get_share_deal_fee(self):
        return self.share_deal_fee

    def get_share_deal_reduce_trades(self):
        return self.share_deal_reduce_trades

    def get_share_deal_reduce_amount(self):
        return self.share_deal_reduce_amount
