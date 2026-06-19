import uuid


# used for generating the auth tokens
# https://stackoverflow.com/questions/41354205/how-to-generate-a-unique-auth-token-in-python
class Auth:
    def __init__(self):
        self.__tokens = {}

    def login(self, user_id: int) -> str:
        token = str(uuid.uuid4())
        self.__tokens[token] = user_id
        return token

    def owner(self, token: str) -> int | None:
        return self.__tokens.get(token)

    def logout(self, token: str):
        self.__tokens.pop(token, None)
