from PyQt6.QtWidgets import QApplication

import sys

import platform_edit


app = QApplication(sys.argv)
# Show platform edit window first, before main win
window = platform_edit.PlatformEdit()
window.show()
app.exec()
