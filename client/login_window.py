from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


class LoginWindow:
    def __init__(self):
        self.__window = QUiLoader().load(QFile("login.ui"), None)
        self.__username = None
        self.__token = None

        self.__window.loginButton.clicked.connect(self.__login)  # type: ignore
        self.__window.registerButton.clicked.connect(self.__register)  # type: ignore
        self.__window.usernameLineEdit.returnPressed.connect(self.__login)  # type: ignore
        self.__window.passwordLineEdit.returnPressed.connect(self.__login)  # type: ignore

    def show(self):
        self.__window.show()

    def token(self):
        return self.__token

    def username(self):
        return self.__username

    def __fields(self):
        return (
            self.__window.usernameLineEdit.text().strip(),  # type: ignore
            self.__window.passwordLineEdit.text().strip(),  # type: ignore
        )

    def __post_req(
        self, path, **kwargs
    ):  # have to redefine the post request because we cant use the api service class since a token wasnt created yet
        return requests.post(f"{API_URL}{path}", params=kwargs, timeout=5).json()

    def __login(self):
        username, password = self.__fields()
        if not username or not password:
            return  # add a check for imcomplete data
        data = self.__post_req("/login", username=username, password=password)
        if "token" in data:
            self.__username = username
            self.__token = data["token"]
            self.__window.close()
        else:
            self.__window.passwordLineEdit.clear()  # type: ignore
            self.__window.passwordLineEdit.setPlaceholderText(  # type: ignore
                data.get("message", "login failed")
            )

    def __register(self):
        username, password = self.__fields()
        if not username or not password:
            return  # add a check for imcomplete data
        data = self.__post_req("/register", username=username, password=password)
        msg = data.get("message", "")
        if msg == "account successfully created":
            self.__login()
        else:
            self.__window.passwordLineEdit.clear()  # type: ignore
            self.__window.passwordLineEdit.setPlaceholderText(msg)  # type: ignore
