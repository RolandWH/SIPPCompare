from PyQt6.QtWidgets import QApplication

import sys

import platform_edit


app = QApplication(sys.argv)
# Show platform edit window first, before main win
# When debugging, can be useful to autofill values to save time
if len(sys.argv) > 1:
    if sys.argv[1] == "--DEBUG_AUTOFILL":
        window = platform_edit.PlatformEdit(True)
    else:
        window = platform_edit.PlatformEdit(False)
else:
    window = platform_edit.PlatformEdit(False)

window.show()
app.exec()
