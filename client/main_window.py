from api_service import ApiService
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Qt
from PySide6.QtWidgets import QListWidgetItem
from message_bubble import MessageBubble
from sidebar import SidebarUser
from polling import Polling, UserPoller
from datetime import datetime
import time


# helper
def format_time(time):
    return datetime.fromtimestamp(time).strftime("%I:%M %p")


from dotenv import load_dotenv
import os

load_dotenv()
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


class MainWindow:
    def __init__(self, username, token):
        # initiate all variables needed
        self.__username = username
        self.__api = ApiService(token, API_URL)
        self.__destination_id = None
        self.__destination_username = None
        self.__known_users = set()
        self.__oldest_id = None  # oldest message
        self.poller = None  # no poller yet, only when running
        # keep poller public because it must be accessed later from main and this makes it much simpler

        # create the window object
        self.__window = QUiLoader().load(QFile("gui.ui"), None)  # load the .ui file
        self.__window.setWindowTitle(f"Chat Open as {username}")
        # update labels
        self.__window.loadButton.setText("Load Older Messages")  # type: ignore
        self.__window.textInput.setPlaceholderText(  # type: ignore
            "Select a conversation..."
        )  # placeholder text makes it grayed out
        # lock inputs until the user selects someone to chat with
        self.__window.textInput.setEnabled(False)  # type: ignore
        self.__window.sendButton.setEnabled(False)  # type: ignore
        self.__window.loadButton.setEnabled(False)  # type: ignore

        # assign functions to the buttons and textInputs
        # NOTE TO SELF: DO NOT ADD BRACKETS FOR THE FUNCTIONS
        self.__window.textInput.returnPressed.connect(self.__send)  # type: ignore
        self.__window.sendButton.clicked.connect(self.__send)  # type: ignore
        self.__window.loadButton.clicked.connect(self.__load_older)  # type: ignore
        self.__window.sidebarList.itemClicked.connect(self.__user_selected)  # type: ignore

        self.__populate_sidebar()  # initially fill sidebar, poller only works after user selected
        self.__user_poller = UserPoller(self.__api)
        self.__user_poller.set_known_users(self.__known_users)
        self.__user_poller.new_users.connect(self.__on_new_user)
        self.__user_poller.start()
        


    def show(self):
        self.__window.show()

    # ---------- sidebar methods ----------
    def __populate_sidebar(self):
        users = self.__api.get_users()
        if not users:
            print("could not load users")
            return
        for user in users:
            self.__known_users.add(user["id"])
            self.__add_sidebar_user(user["username"], user["id"])

    # https://doc.qt.io/qtforpython-6/PySide6/QtGui/QStandardItem.html
    def __add_sidebar_user(self, name, user_id):
        # UserRole allows you to add non-visible data attached to the visible element
        item = QListWidgetItem(self.__window.sidebarList)  # type: ignore
        item.setData(Qt.UserRole, user_id)  # type: ignore
        item.setData(Qt.UserRole + 1, name)  # type: ignore
        card = SidebarUser(name)
        item.setSizeHint(
            card.sizeHint()
        )  # pass the size hint of the card as the size hint of the item in the list
        self.__window.sidebarList.setItemWidget(item, card)  # type: ignore

    # ---------- user selected method ----------

    # UserRole (0) -> user id
    # UserRole (+1) -> user name
    def __user_selected(self, item):
        if self.poller:
            self.poller.stop()  # stop the poller (because we need to make a new poller)
            self.poller.wait()  # wait() to ensure the thread is fully done before making a new one

        # get the variables from the card container
        self.__destination_id = item.data(Qt.UserRole)  # type: ignore
        self.__destination_username = item.data(Qt.UserRole + 1)  # type: ignore

        # reset the oldest id since we just opened a chat
        self.__oldest_id = None

        # update window name
        self.__window.setWindowTitle(f"Chatting with {self.__destination_username}")

        # enable stuff
        self.__window.messageHistoryList.clear()  # type: ignore
        self.__window.textInput.setEnabled(True)  # type: ignore
        self.__window.textInput.setPlaceholderText(  # type: ignore
            f"Send a message to {self.__destination_username}"
        )
        self.__window.sendButton.setEnabled(True)  # type: ignore
        self.__window.loadButton.setEnabled(True)  # type: ignore
        self.__window.loadButton.setText("Load Older Messages")  # type: ignore
        self.__load_initial()
        self.__start_polling()

    # ---------- message loading ----------
    # both of these methods load 1 extra as a 'peek'

    def __load_initial(self):
        messages = self.__api.load_messages(
            self.__destination_id, limit=51
        )  # we only really want 50, but we load 51 to peek at the next message to see if we disable the button or not
        if not messages:  # if the client just doesnt have any messages with the user
            self.__disable_load_button()
            return
        if (
            len(messages) < 51
        ):  # see if len is less than 51, once again, one extra message is needed as a peek
            self.__disable_load_button()
        else:
            messages.pop()
        self.__oldest_id = messages[-1]["id"]
        for msg in messages[
            ::-1
        ]:  # server returns them newest first, but for rendering we need oldest first
            self.__add_bubble(msg, prepend=False)

    def __load_older(self):
        if (
            not self.__destination_id or self.__oldest_id is None
        ):  # check isn't needed *asuming* the GUI is working well
            return
        messages = self.__api.load_messages(
            self.__destination_id, limit=21, before_id=self.__oldest_id
        )
        if not messages:
            self.__disable_load_button()
            return

        before_count = self.__window.messageHistoryList.count()  # type: ignore
        for msg in messages:
            self.__add_bubble(msg, prepend=True)
        self.__window.messageHistoryList.setCurrentRow(  # type: ignore
            self.__window.messageHistoryList.count() - before_count  # type: ignore
        )
        if len(messages) < 21:
            self.__disable_load_button()
        else:
            messages.pop()
        self.__oldest_id = messages[-1]["id"]

    def __disable_load_button(self):
        self.__window.loadButton.setText("No More History")  # type: ignore
        self.__window.loadButton.setEnabled(False)  # type: ignore

    # ---------- polling ----------

    def __start_polling(self):
        if self.__user_poller.isRunning(): # end the user poller since the main poller handles user changes
            self.__user_poller.stop()
            self.__user_poller.wait()
        self.poller = Polling(self.__api, self.__destination_id)
        self.poller.set_known_users(self.__known_users)
        self.poller.new_messages.connect(self.__on_new_message)
        self.poller.new_users.connect(self.__on_new_user)
        self.poller.start()

    def __on_new_user(self, users):
        for user in users:
            self.__known_users.add(user["id"])
            self.__add_sidebar_user(user["username"], user["id"])

    def __on_new_message(self, messages):
        for msg in messages:
            if msg["user_destination"] == self.__destination_id:
                continue  # skip so messages don't echo back
            self.__add_bubble(msg, prepend=False)

    # ---------- sending ----------
    def __send(self):
        text = self.__window.textInput.text().strip()  # type: ignore
        if not text or not self.__destination_id:
            return  # not proper data, no blank messages
        result = self.__api.send_message(text, self.__destination_id)
        if result.get("message") == "sent":  # api response
            self.__add_bubble_raw(
                text,
                format_time(time.time()),
                self.__username,
                is_me=True,
                prepend=False,
            )
        self.__window.textInput.clear()  # type: ignore

    # ---------- bubble rendering ----------
    def __add_bubble(self, msg, prepend):
        is_me = (
            msg["user_destination"] == self.__destination_id
        )  # if the person recieving the message is the person who I'm talking to
        sender = self.__username if is_me else self.__destination_username
        self.__add_bubble_raw(
            msg["message"], format_time(msg["created_at"]), sender, is_me, prepend
        )

    def __add_bubble_raw(self, text, time, sender, is_me, prepend):
        bubble = MessageBubble(
            text, time, sender, is_me, self.__window.messageHistoryList.width()  # type: ignore
        )
        item = QListWidgetItem()
        item.setSizeHint(bubble.sizeHint())
        if prepend:
            self.__window.messageHistoryList.insertItem(0, item)  # type: ignore
        else:
            self.__window.messageHistoryList.addItem(item)  # type: ignore
            self.__window.messageHistoryList.scrollToBottom()  # type: ignore
        self.__window.messageHistoryList.setItemWidget(item, bubble)  # type: ignore
