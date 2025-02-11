from PyQt6.QtCore import QRegularExpression, QEvent, QObject, QTimer
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QWidget, QLayout
from PyQt6 import uic

import main_window


class PlatformEdit(QWidget):
    def __init__(self, autofill: bool):
        super().__init__()
        # Import Qt Designer UI XML file
        uic.loadUi("gui/platform_edit.ui", self)

        # Initialise class variables
        # TODO: Make fund_plat_fee user-defined
        self.fund_plat_fee = [
            [0, 250000, 1000000, 2000000],
            [0, 0.25, 0.1, 0.05]
        ]
        self.plat_name = ""
        self.fund_deal_fee = 0.0
        self.share_plat_fee = 0.0
        self.share_plat_max_fee = 0.0
        self.share_deal_fee = 0.0
        self.share_deal_reduce_trades = 0.0
        self.share_deal_reduce_amount = 0.0
        # Debugging feature: set with "--DEBUG_AUTOFILL" cmd argument
        self.autofill = autofill
        if autofill:
            self.save_but.setEnabled(True)

        self.required_fields = [
            self.fund_deal_fee_box,
            self.share_plat_fee_box,
            self.share_deal_fee_box
        ]

        self.optional_fields = [
            self.plat_name_box,
            self.share_plat_max_fee_box,
            self.share_deal_reduce_trades_box,
            self.share_deal_reduce_amount_box
        ]

        self.optional_check_boxes = [
            self.plat_name_check,
            self.share_plat_max_fee_check,
            self.share_deal_reduce_trades_check,
            self.share_deal_reduce_amount_check
        ]

        # Create main window object, passing this instance as param
        self.main_win = main_window.SIPPCompare(self)

        # Handle events
        # NOTE: Signal defined in UI file to close window when save button clicked
        self.save_but.clicked.connect(self.init_variables)

        for field in self.required_fields:
            field.valueChanged.connect(self.check_valid)

        for field in self.optional_fields:
            if field.staticMetaObject.className() == "QLineEdit":
                field.textChanged.connect(self.check_valid)
            elif field.staticMetaObject.className() == "QDoubleSpinBox":
                field.valueChanged.connect(self.check_valid)

        for check_box in self.optional_check_boxes:
            check_box.checkStateChanged.connect(self.check_valid)

        # Install event filter on input boxes in order to select all text on focus
        self.fund_deal_fee_box.installEventFilter(self)
        self.share_plat_fee_box.installEventFilter(self)
        self.share_plat_max_fee_box.installEventFilter(self)
        self.share_deal_fee_box.installEventFilter(self)
        self.share_deal_reduce_trades_box.installEventFilter(self)
        self.share_deal_reduce_amount_box.installEventFilter(self)

        #for check_box in self.optional_check_boxes:
        #    check_box.installEventFilter(self)

        # Set validators
        # Regex accepts any characters that match [a-Z], [0-9] or _
        self.plat_name_box.setValidator(
            QRegularExpressionValidator(QRegularExpression("\\w*"))
        )

    # Get fee structure variables from user input when "Save" clicked
    def init_variables(self):
        # If debugging, save time by hardcoding
        if self.autofill:
            self.plat_name                  = "AJBell"
            self.fund_deal_fee              = 1.50
            self.share_plat_fee             = 0.0025
            self.share_plat_max_fee         = 3.50
            self.share_deal_fee             = 5.00
            self.share_deal_reduce_trades   = 10
            self.share_deal_reduce_amount   = 3.50
        else:
            self.plat_name                  = self.plat_name_box.text()
            self.fund_deal_fee              = float(self.fund_deal_fee_box.value())
            self.share_plat_fee             = float(self.share_plat_fee_box.value()) / 100
            self.share_plat_max_fee         = float(self.share_plat_max_fee_box.value())
            self.share_deal_fee             = float(self.share_deal_fee_box.value())
            self.share_deal_reduce_trades   = float(self.share_deal_reduce_trades_box.value())
            self.share_deal_reduce_amount   = float(self.share_deal_reduce_amount_box.value())

        # Once user input is received show main window
        self.main_win.show()

    # When focus is given to an input box, select all text in it (easier to edit)
    def eventFilter(self, obj: QObject, event: QEvent):
        if event.type() == QEvent.Type.FocusIn:
            # Alternative condition for % suffix - currently unused
            #if obj.value() == 0 or obj == self.share_plat_fee_box:
            QTimer.singleShot(0, obj.selectAll)
        return False

    # Check if all required fields have valid (non-zero) input
    def check_valid(self):
        valid = True

        for field in self.required_fields:
            if field.value() == 0:
                valid = False

        for check_box in self.optional_check_boxes:
            check_box_pos = self.gridLayout.getItemPosition(self.gridLayout.indexOf(check_box))
            input_box_pos = list(check_box_pos)[:2]
            input_box_pos[1] -= 1
            input_box_item = self.gridLayout.itemAtPosition(input_box_pos[0], input_box_pos[1]).widget()
            if check_box.isChecked():
                input_box_item.setEnabled(True)
                input_box_type = input_box_item.staticMetaObject.className()
                if input_box_type == "QLineEdit":
                    if input_box_item.text() == "":
                        valid = False
                elif input_box_type == "QDoubleSpinBox" or input_box_type == "QSpinBox":
                    if input_box_item.value() == 0:
                        valid = False
            else:
                input_box_item.setEnabled(False)

        if valid:
            self.save_but.setEnabled(True)
        else:
            self.save_but.setEnabled(False)

    # Getter functions (is this necessary? maybe directly reading class vars would be best...)
    def get_plat_name(self):
        return self.plat_name

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
