import sys

from PyQt6.QtWidgets import QApplication
import main_window

app = QApplication(sys.argv)
window = main_window.SIPPCompare()
window.show()
app.exec()
