from PyQt6 import uic
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QIcon, QRegularExpressionValidator, QFont
from PyQt6.QtWidgets import QWidget, QListWidgetItem, QDialog, QDialogButtonBox, QMessageBox

import resource_finder
from db_handler import DBHandler
from data_struct import Platform
from platform_edit import PlatformEdit


class PlatformRename(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Import Qt Designer UI XML file
        uic.loadUi(resource_finder.get_res_path("gui/dialogs/platform_rename.ui"), self)
        self.setWindowIcon(QIcon(resource_finder.get_res_path("icon2.ico")))

        self.rename_plat_box.setFocus()
        self.new_name = ""

        # Set validators
        # Regex accepts any characters that match [a-Z], [0-9] or _
        self.rename_plat_box.setValidator(
            QRegularExpressionValidator(QRegularExpression("\\w*"))
        )

        self.rename_plat_ok_but.clicked.connect(self.store_new_name)

    def store_new_name(self):
        self.new_name = self.rename_plat_box.text()

    def closeEvent(self, event):
        event.ignore()
        self.reject()


class RemoveConfirm(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowIcon(QIcon(resource_finder.get_res_path("icon2.ico")))
        self.setWindowTitle("Remove platform?")
        self.setIcon(QMessageBox.Icon.Warning)
        font = QFont()
        font.setPointSize(11)
        self.setFont(font)
        self.setText("Are you sure you want to remove this platform?")
        self.setInformativeText("This action is immediate and permanent")

        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel)
        self.setDefaultButton(QMessageBox.StandardButton.Cancel)
        font.setPointSize(10)
        self.findChild(QDialogButtonBox).setFont(font)


class PlatformList(QWidget):
    def __init__(self, db: DBHandler):
        super().__init__()
        # Import Qt Designer UI XML file
        uic.loadUi(resource_finder.get_res_path("gui/platform_list.ui"), self)
        self.setWindowIcon(QIcon(resource_finder.get_res_path("icon2.ico")))

        self.db = db
        self.plat_edit_win = None
        self.plat_list_dialog = PlatformRename()
        self.del_plat_dialog = RemoveConfirm()
        self.plat_list = []
        self.plat_name_list = []
        self.new_plat_name = ""
        self.update_plat_list()
        self.db_indices = [x for x in range(len(self.plat_name_list))]

        # Handle events
        self.add_plat_but.clicked.connect(self.add_platform)
        self.del_plat_but.clicked.connect(self.remove_platform)
        self.edit_plat_but.clicked.connect(self.edit_platform)
        self.plist_save_but.clicked.connect(self.save_platforms)
        self.plat_enabled_check.checkStateChanged.connect(self.toggle_platform_state)
        self.platListWidget.currentRowChanged.connect(self.get_enabled_state)

    def update_plat_list(self):
        self.plat_name_list = self.db.retrieve_plat_list()
        self.plat_list = self.db.retrieve_platforms()
        self.platListWidget.clear()

        for i in range(len(self.plat_name_list)):
            plat_name = self.plat_name_list[i]
            item = QListWidgetItem()
            if plat_name is not None:
                item.setText(plat_name)
            else:
                item.setText(f"Unnamed [ID: {i}]")

            self.platListWidget.addItem(item)

    def add_platform(self):
        name_dialog_res = self.plat_list_dialog.exec()
        if name_dialog_res == QDialog.DialogCode.Accepted:
            name = self.plat_list_dialog.new_name
            index = self.platListWidget.count()
            if name != "":
                self.platListWidget.addItem(name)
                name_param = name
            else:
                self.platListWidget.addItem(f"Unnamed [ID: {index}]")
                name_param = None

            self.plat_list.append(Platform(
                index, [[0], [0]], name_param, True, 0, 0, None, 0, None, None)
            )
            self.plat_edit_win = PlatformEdit(self.plat_list[index])
            self.plat_edit_win.show()

    def get_enabled_state(self):
        index = self.platListWidget.currentRow()
        is_enabled = self.plat_list[index].enabled
        if is_enabled:
            self.plat_enabled_check.setChecked(True)
        else:
            self.plat_enabled_check.setChecked(False)

        if index in self.db_indices:
            self.del_plat_but.setEnabled(True)
        else:
            self.del_plat_but.setEnabled(False)

    def edit_platform(self):
        index = self.platListWidget.currentRow()
        self.plat_edit_win = PlatformEdit(self.plat_list[index])
        self.plat_edit_win.show()

    def save_platforms(self):
        self.db.write_platforms(self.plat_list)
        self.update_plat_list()
        self.db_indices = [x for x in range(len(self.plat_name_list))]

    def toggle_platform_state(self):
        index = self.platListWidget.currentRow()
        state = self.plat_enabled_check.isChecked()
        self.plat_list[index].enabled = state

    def remove_platform(self):
        index = self.platListWidget.currentRow()
        del_dialog_res = self.del_plat_dialog.exec()
        if del_dialog_res == QMessageBox.StandardButton.Yes:
            self.db.remove_platform(index)
            self.update_plat_list()
