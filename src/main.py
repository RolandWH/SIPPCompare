import sys

from PyQt6.QtWidgets import QApplication

from main_window import SIPPCompare


app = QApplication(sys.argv)
window = SIPPCompare()
window.show()
app.exec()
