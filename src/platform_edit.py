from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator, QFont, QIcon
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6 import uic

from widgets.fastedit_spinbox import FastEditQDoubleSpinBox
import main_window
import resource_finder


class PlatformEdit(QWidget):
    def __init__(self, autofill: bool):
        super().__init__()
        # Import Qt Designer UI XML file
        uic.loadUi(resource_finder.get_res_path("gui/platform_edit.ui"), self)
        self.setWindowIcon(QIcon(resource_finder.get_res_path("icon2.ico")))

        # Initialise class variables
        # Create main window object, passing this instance as param
        self.main_win = main_window.SIPPCompare(self)

        self.fund_plat_fee = []
        self.plat_name = ""
        self.fund_deal_fee = 0.0
        self.share_plat_fee = 0.0
        self.share_plat_max_fee = 0.0
        self.share_deal_fee = 0.0
        self.share_deal_reduce_trades = 0.0
        self.share_deal_reduce_amount = 0.0
        self.widgets_list_list = []

        self.fund_fee_rows = 1
        # Debugging feature: set with "--DEBUG_AUTOFILL" cmd argument
        self.autofill = autofill
        if autofill:
            self.save_but.setEnabled(True)

        self.required_fields = [
            self.share_plat_fee_box,
            self.share_deal_fee_box
        ]

        self.optional_fields = [
            self.plat_name_box,
            self.fund_deal_fee_box,
            self.share_plat_max_fee_box,
            self.share_deal_reduce_trades_box,
            self.share_deal_reduce_amount_box
        ]

        self.optional_check_boxes = [
            self.plat_name_check,
            self.fund_deal_fee_check,
            self.share_plat_max_fee_check,
            self.share_deal_reduce_trades_check,
            self.share_deal_reduce_amount_check
        ]

        self.check_boxes_ticked = [
            True,
            True,
            False,
            False,
            False
        ]

        # Handle events
        for field in self.required_fields:
            field.valueChanged.connect(self.check_valid)

        for field in self.optional_fields:
            field_type = field.staticMetaObject.className()
            if field_type == "QLineEdit":
                field.textChanged.connect(self.check_valid)
            elif field_type == "FastEditQDoubleSpinBox" or field_type == "FastEditQSpinBox":
                field.valueChanged.connect(self.check_valid)

        for check_box in self.optional_check_boxes:
            check_box.checkStateChanged.connect(self.check_valid)

        self.first_tier_box.valueChanged.connect(self.check_valid)
        self.first_tier_fee_box.valueChanged.connect(self.check_valid)
        self.first_tier_box.valueChanged.connect(self.update_tier_labels)

        # NOTE: Signal defined in UI file to close window when save button clicked
        self.save_but.clicked.connect(self.init_variables)
        self.add_row_but.clicked.connect(self.add_row)
        self.del_row_but.clicked.connect(self.remove_row)

        # Set validators
        # Regex accepts any characters that match [a-Z], [0-9] or _
        self.plat_name_box.setValidator(
            QRegularExpressionValidator(QRegularExpression("\\w*"))
        )

    def create_plat_fee_struct(self):
        plat_fee_struct = [[0], [0]]
        plat_fee_struct[0].append(self.first_tier_box.value())
        plat_fee_struct[1].append(self.first_tier_fee_box.value())

        for i in range(len(self.widgets_list_list)):
            band = self.widgets_list_list[i][1].value()
            fee = self.widgets_list_list[i][3].value()
            plat_fee_struct[0].append(band)
            plat_fee_struct[1].append(fee)

        return plat_fee_struct

    # Get fee structure variables from user input when "Save" clicked
    def init_variables(self):
        # If debugging, save time by hardcoding
        if self.autofill:
            self.plat_name                  = "AJBell"
            self.fund_plat_fee              = [
                                            [0, 250000,     1000000,    2000000],
                                            [0, 0.25,       0.1,        0.05]
                                        ]
            self.fund_deal_fee              = 1.50
            self.share_plat_fee             = 0.0025
            self.share_plat_max_fee         = 3.50
            self.share_deal_fee             = 5.00
            self.share_deal_reduce_trades   = 10
            self.share_deal_reduce_amount   = 3.50
        else:
            self.plat_name                  = self.plat_name_box.text()
            self.fund_plat_fee              = self.create_plat_fee_struct()
            self.fund_deal_fee              = float(self.fund_deal_fee_box.value())
            self.share_plat_fee             = float(self.share_plat_fee_box.value()) / 100
            self.share_plat_max_fee         = float(self.share_plat_max_fee_box.value())
            self.share_deal_fee             = float(self.share_deal_fee_box.value())
            self.share_deal_reduce_trades   = float(self.share_deal_reduce_trades_box.value())
            self.share_deal_reduce_amount   = float(self.share_deal_reduce_amount_box.value())

        # Once user input is received show main window
        self.main_win.show()

    # This method does multiple things in order to validate the user's inputs:
    # 1) Check all required fields have a non-zero value
    # 2) If an optional checkbox is toggled: toggle editing of the corresponding field
    # 3) Check all optional fields the user has picked have a non-zero value
    # 4) If the above two conditions are met (1 & 3), make the 'Save' button clickable
    # 5) Keep a record of which optional fields the user has chosen to fill in
    # It's called when an optional check box emits a checkStateChanged() signal
    # It's also called when any field emits a textChanged() or valueChanged() signal
    def check_valid(self):
        valid = True
        tiers_valid = True

        # Check all required fields have a non-zero value
        for field in self.required_fields:
            if field.value() == 0:
                valid = False

        for i in range(len(self.optional_check_boxes)):
            # Find the coordinates of the input box corresponding to the checkbox
            # It will be on the same row, in the column to the left (-1)
            check_box_idx = self.gridLayout.indexOf(self.optional_check_boxes[i])
            check_box_pos = self.gridLayout.getItemPosition(check_box_idx)
            input_box_pos = list(check_box_pos)[:2]
            input_box_pos[1] -= 1
            # Return copy of input field widget from its coordinates
            input_box_item = self.gridLayout.itemAtPosition(input_box_pos[0], input_box_pos[1]).widget()
            if self.optional_check_boxes[i].isChecked():
                input_box_item.setEnabled(True)
                self.check_boxes_ticked[i] = True
                input_box_type = input_box_item.staticMetaObject.className()
                if input_box_type == "QLineEdit":
                    if input_box_item.text() == "":
                        valid = False
                elif input_box_type == "FastEditQDoubleSpinBox" or input_box_type == "FastEditQSpinBox":
                    if input_box_item.value() == 0:
                        valid = False
            else:
                input_box_item.setEnabled(False)
                self.check_boxes_ticked[i] = False

        if self.first_tier_fee_box.value() == 0:
            tiers_valid = False

        if self.fund_fee_rows > 1:
            if self.widgets_list_list[0][1].value() <= self.first_tier_box.value():
                tiers_valid = False
            if self.widgets_list_list[0][3].value() == 0:
                tiers_valid = False

        for i in range(len(self.widgets_list_list) - 1, 0, -1):
            if self.widgets_list_list[i][1].value() <= self.widgets_list_list[i-1][1].value():
                tiers_valid = False
            if self.widgets_list_list[i][3].value() == 0:
                tiers_valid = False

        if tiers_valid and self.fund_fee_rows < 6:
            self.add_row_but.setEnabled(True)
        else:
            self.add_row_but.setEnabled(False)

        if valid and tiers_valid:
            self.save_but.setEnabled(True)
        else:
            self.save_but.setEnabled(False)

    def update_tier_labels(self):
        if self.fund_fee_rows > 1:
            prev_value = self.first_tier_box.value()
            self.widgets_list_list[0][0].setText(f"between £{int(prev_value)} and")

        for i in range(len(self.widgets_list_list) - 1, 0, -1):
            prev_value = self.widgets_list_list[i-1][1].value()
            self.widgets_list_list[i][0].setText(f"between £{int(prev_value)} and")

        if self.fund_fee_rows > 1:
            max_band = self.widgets_list_list[self.fund_fee_rows - 2][1].value()
        else:
            max_band = self.first_tier_box.value()
        self.val_above_lab.setText(f"on the value above £{int(max_band)} there is no charge")

    def add_row(self):
        widgets = []
        font = QFont()
        font.setPointSize(11)

        widgets.append(QLabel(self.gridLayoutWidget_2))
        widgets[0].setFont(font)

        widgets.append(FastEditQDoubleSpinBox(self.gridLayoutWidget_2))
        widgets[1].setPrefix("£")
        widgets[1].setMaximum(9999999)
        widgets[1].setButtonSymbols(FastEditQDoubleSpinBox.ButtonSymbols.NoButtons)
        widgets[1].setFont(font)
        widgets[1].valueChanged.connect(self.check_valid)
        widgets[1].valueChanged.connect(self.update_tier_labels)

        widgets.append(QLabel(self.gridLayoutWidget_2))
        widgets[2].setText(f"the fee is")
        widgets[2].setFont(font)

        widgets.append(FastEditQDoubleSpinBox(self.gridLayoutWidget_2))
        widgets[3].setSuffix("%")
        widgets[3].setMaximum(100)
        widgets[3].setButtonSymbols(FastEditQDoubleSpinBox.ButtonSymbols.NoButtons)
        widgets[3].setFont(font)
        widgets[3].valueChanged.connect(self.check_valid)

        # TODO: why 28.5?
        self.gridLayoutWidget_2.setGeometry(11, 309, 611, int(round(28.5 * (self.fund_fee_rows + 1), 0)))
        for i in range(len(widgets)):
            self.gridLayout_2.addWidget(widgets[i], self.fund_fee_rows, i, 1, 1)

        self.fund_fee_rows += 1

        self.widgets_list_list.append(widgets)
        cur_label_idx = self.gridLayout_2.indexOf(widgets[0])
        cur_box_idx = self.gridLayout_2.indexOf(widgets[1])
        cur_label_pos = list(self.gridLayout_2.getItemPosition(cur_label_idx))[:2]
        cur_box_pos = list(self.gridLayout_2.getItemPosition(cur_box_idx))[:2]

        prev_box_row = cur_box_pos[0] - 1
        prev_box_item = self.gridLayout_2.itemAtPosition(prev_box_row, cur_box_pos[1]).widget()
        cur_label_item = self.gridLayout_2.itemAtPosition(cur_label_pos[0], cur_label_pos[1]).widget()
        cur_label_item.setText(f"between £{int(prev_box_item.value())} and")

        if self.fund_fee_rows > 1:
            self.del_row_but.setEnabled(True)

        if self.fund_fee_rows > 5:
            self.add_row_but.setEnabled(False)

        self.check_valid()

        # TODO: Tab order

    def remove_row(self):
        for widget in self.widgets_list_list[self.fund_fee_rows - 2]:
            self.gridLayout_2.removeWidget(widget)
            widget.hide()
        self.widgets_list_list.pop()
        self.fund_fee_rows -= 1
        self.gridLayoutWidget_2.setGeometry(11, 309, 611, int(round(28.5 * self.fund_fee_rows, 0)))

        if self.fund_fee_rows < 2:
            self.del_row_but.setEnabled(False)

        if self.fund_fee_rows < 6:
            self.add_row_but.setEnabled(True)

        self.check_valid()
        self.update_tier_labels()

    # Getter functions (is this necessary? maybe directly reading class vars would be best...)
    def get_optional_boxes(self):
        return self.check_boxes_ticked

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
