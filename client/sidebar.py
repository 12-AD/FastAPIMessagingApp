from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile


class SidebarUser(QWidget):
    def __init__(self, name, status="Available"):
        super().__init__()
        self.__user_card = QUiLoader().load(QFile("user_item.ui"), None)  # load the .ui file
        # update labels
        self.__user_card.nameLabel.setText(name) # type: ignore
        self.__user_card.statusLabel.setText(status) # type: ignore
        self.__user_card.avatarLabel.setText(name[0].upper())  # type: ignore
        # add to layout box
        self.__layout = QHBoxLayout(self)
        # remove padding
        self.__layout.setContentsMargins(0, 0, 0, 0)
        # add the widget
        self.__layout.addWidget(self.__user_card) # type: ignore
