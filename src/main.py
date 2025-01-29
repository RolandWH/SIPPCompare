from PyQt6.QtWidgets import QApplication

import sys

import main_window


app = QApplication(sys.argv)
window = main_window.SIPPCompare()
window.show()
window.show_platform_edit()
app.exec()
