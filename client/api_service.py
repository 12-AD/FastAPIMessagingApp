import requests


class ApiService:
    def __init__(self, token, API_URL):
        self.__token = token
        self.__API_URL = API_URL

    # https://www.codecademy.com/resources/docs/python/requests-module/request
    # https://requests.readthedocs.io/en/latest/_modules/requests/api/
    # https://docs.python-requests.org/en/latest/user/quickstart/#json-response-content

    # Copilot Generated this Function, i removed the error code check and added a timeout
    def __get_req(self, path, **params):
        return requests.get(
            f"{self.__API_URL}{path}",
            params={"token": self.__token, **params},
            timeout=5,
        )

    # Copilot Generated this Function, i removed the error code check and added a timeout
    def __post_req(self, path, **params):
        return requests.post(
            f"{self.__API_URL}{path}",
            params={"token": self.__token, **params},
            timeout=5,
        )

    def get_users(self):
        return self.__get_req("/users").json()

    def send_message(self, message, user_destination):
        return self.__post_req(
            "/message", message=message, user_destination=user_destination
        ).json()

    def load_messages(self, user_destination, limit=50, before_id=None):
        params = {"user_destination": user_destination, "limit": limit}
        if before_id is not None:
            params["before_id"] = before_id
        return self.__get_req("/messages_load", **params).json()

    def get_changes(self, user_destination, last_seen_time):
        return self.__get_req(
            "/changes", user_destination=user_destination, last_seen_time=last_seen_time
        ).json()
