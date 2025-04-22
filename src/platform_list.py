from PyQt6.QtWidgets import QWidget, QListWidgetItem
from PyQt6.QtGui import QIcon, QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
from PyQt6 import uic

import resource_finder
import data_struct
import platform_edit


class PlatformRename(QWidget):
    def __init__(self):
        super().__init__()
        # Import Qt Designer UI XML file
        uic.loadUi(resource_finder.get_res_path("gui/dialogs/platform_rename.ui"), self)
        self.setWindowIcon(QIcon(resource_finder.get_res_path("icon2.ico")))

        # Set validators
        # Regex accepts any characters that match [a-Z], [0-9] or _
        self.rename_plat_box.setValidator(
            QRegularExpressionValidator(QRegularExpression("\\w*"))
        )


class PlatformList(QWidget):
    def __init__(self, db):
        super().__init__()
        # Import Qt Designer UI XML file
        uic.loadUi(resource_finder.get_res_path("gui/platform_list.ui"), self)
        self.setWindowIcon(QIcon(resource_finder.get_res_path("icon2.ico")))

        self.plat_list_dialog = PlatformRename()
        self.p_edit = None
        self.db = db
        self.plat_name_list = self.db.retrieve_plat_list()
        self.plat_list = self.db.retrieve_platforms()
        print(self.plat_list[1].fund_plat_fee)
        print(self.plat_name_list)

        for platform in self.plat_name_list:
            item = QListWidgetItem()
            item.setText(platform)
            self.platListWidget.addItem(item)

        # Handle events
        self.add_plat_but.clicked.connect(self.add_platform)
        self.del_plat_but.clicked.connect(self.remove_platform)
        self.edit_plat_but.clicked.connect(self.edit_platform)
        self.plat_enabled_check.checkStateChanged.connect(self.toggle_platform_state)
        self.platListWidget.currentRowChanged.connect(self.get_enabled_state)

    def add_platform(self):
        self.plat_list_dialog.show()

    def get_enabled_state(self):
        index = self.platListWidget.currentRow()
        is_enabled = self.plat_list[index].enabled
        if is_enabled:
            self.plat_enabled_check.setChecked(True)
        else:
            self.plat_enabled_check.setChecked(False)

    def edit_platform(self):
        index = self.platListWidget.currentRow()
        self.p_edit = platform_edit.PlatformEdit(self.plat_list[index])
        self.p_edit.show()

    def toggle_platform_state(self):
        return None

    def remove_platform(self):
        return None
