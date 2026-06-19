from PySide6.QtWidgets import QApplication
from login_window import LoginWindow
from main_window import MainWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_win = LoginWindow()
    login_win.show()
    app.exec()

    if not login_win.token():
        sys.exit()
    window = MainWindow(login_win.username(), login_win.token())
    window.show()
    code = app.exec()
    if window.poller:
        window.poller.stop()
        window.poller.wait()
    sys.exit(code)
        