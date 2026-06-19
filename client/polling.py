from PySide6.QtCore import QThread, Signal
import time

# https://doc.qt.io/qtforpython-6/PySide6/QtCore/QThread.html#PySide6.QtCore.QThread

# QThread is a built class into PySide6 (the gui module im using)
# that can create threads that run in the background without
# interruping the functions of the main GUI code

# it could also be done with the threading module in python (what i originally did)
# but i found out this is better since it allows the thread to communcate
# directly with the GUI using Signal(s)
# https://doc.qt.io/qtforpython-6/PySide6/QtCore/Signal.html#PySide6.QtCore.Signal


class Polling(QThread):
    # QThread needs the signals to be created before object creation so these go here rather than the __init__
    new_messages = Signal(list)
    new_users = Signal(list)

    def __init__(self, api, user_destination):
        super().__init__()
        self.__api = api
        self.__user_destination = user_destination
        self.__last_seen_time = int(time.time())
        self.__known_users = set()
        self.__is_running = True

    def set_known_users(self, known_users):
        self.__known_users = known_users

    def run(self):
        while self.__is_running:
            try:
                returned_messages = self.__api.get_changes(
                    self.__user_destination, self.__last_seen_time
                )
                if returned_messages:  # if there's new data
                    self.__last_seen_time = max(
                        m["updated_at"] for m in returned_messages
                    )  # gets the latest thing (maximum time) and sets that as the last seen event
                    self.new_messages.emit(
                        returned_messages
                    )  # send that data to the signal which was created
                returned_users = self.__api.get_users()
                if returned_users:
                    new = [
                        user
                        for user in returned_users
                        if user["id"] not in self.__known_users
                    ]
                    if new:
                        for u in new:
                            self.__known_users.add(u["id"])
                        self.new_users.emit(new)
            except Exception as e:
                print(f"Error when polling: {e}")
            self.msleep(1500)  # wait 1.5s

    def stop(self):
        self.__is_running = False


class UserPoller(QThread):
    new_users = Signal(list)

    def __init__(self, api):
        super().__init__()
        self.__api = api
        self.__known_users = set()
        self.__is_running = True

    def set_known_users(self, known_users):
        self.__known_users = set(known_users)

    def run(self):
        while self.__is_running:
            try:
                returned_users = self.__api.get_users()
                if returned_users:
                    new = [
                        u for u in returned_users if u["id"] not in self.__known_users
                    ]
                    if new:
                        for u in new:
                            self.__known_users.add(u["id"])
                        self.new_users.emit(new)
            except Exception as e:
                print(f"Error when polling users: {e}")
            self.msleep(1500)

    def stop(self):
        self.__is_running = False
