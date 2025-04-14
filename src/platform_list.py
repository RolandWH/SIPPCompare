from PyQt6.QtWidgets import QWidget, QListWidgetItem
from PyQt6.QtGui import QIcon, QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
from PyQt6 import uic

import resource_finder


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
        self.db = db
        self.plat_name_list = self.db.retrieve_plat_list()
        print(self.plat_name_list)

        for platform in self.plat_name_list:
            item = QListWidgetItem()
            item.setText(platform)
            self.platListWidget.addItem(item)

        # Handle events
        self.add_plat_but.clicked.connect(self.add_platform)

    def add_platform(self):
        self.plat_list_dialog.show()
