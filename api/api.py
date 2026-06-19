from fastapi import FastAPI

# video i used for making most of the API
# https://www.youtube.com/watch?v=iWS9ogMPOI0


from database import Database
from authorization import Auth

app = FastAPI()  # create the app object
server_database = Database()
authorization_manager = Auth()


@app.get("/")  # define the path with a decorator (http://127.0.0.1:8000/)
def root():
    return {"message": "HELLO WORLD"}


@app.post("/message")
def send_message(message: str, user_destination: int, token: str):
    user_origin = authorization_manager.owner(token)
    if user_origin is None:
        return {"message": "invalid credentials"}
    return server_database.send_message(message, user_destination, user_origin)


@app.post("/delete")
def delete_message(message_id: int, token: str):
    user_origin = authorization_manager.owner(token)
    if user_origin is None:
        return {"message": "invalid credentials"}
    return server_database.delete_message(message_id, user_origin)


@app.post("/edit")
def edit_message(message_id: int, token: str, message: str):
    user_origin = authorization_manager.owner(token)
    if user_origin is None:
        return {"message": "invalid credentials"}
    return server_database.edit_message(message_id, user_origin, message)


# gets the messages for when the user first loads the program
@app.get("/messages_load")
def get_messages_load(
    token: str,
    user_destination: int,
    limit: int = 50,  # limit is 50 by default, unless overriden
    before_id: (
        int | None
    ) = None,  # set the before ID to be None, it is only used when loading older messages, because the client upon booting up only loads LIMIT messages, to load more the user has to manually chose so, (why this is here)
):
    user_origin = authorization_manager.owner(token)
    if user_origin is None:
        return {"message": "invalid credentials"}
    return server_database.load_messages(
        user_origin, user_destination, limit, before_id
    )


@app.get("/changes")  # for polling
def get_changed_or_new_messages(last_seen_time: int, user_destination: int, token: str):
    user_origin = authorization_manager.owner(token)
    if user_origin is None:
        return {"message": "invalid credentials"}
    return server_database.changed_or_new_messages(
        user_origin, user_destination, last_seen_time
    )


@app.post("/login")
def login(username: str, password: str):
    username = username.lower()
    user_id = server_database.login(username, password)
    if user_id is None:
        return {"message": "invalid login credentials"}
    token = authorization_manager.login(user_id)
    return {"token": token}


@app.post("/register")
def register(username: str, password: str):
    username = username.lower()
    # later add a check to ensure a secure password
    if 12 < len(username) or len(username) < 3:
        return {"message": "username must be between 3 and 12 characters long"}
    if 12 < len(password) or len(password) < 8:
        return {"message": "password must be between 8 and 12 characters long"}

    if server_database.check_user(username):
        return {"message": "name taken"}

    if server_database.register(username, password):
        return {"message": "account successfully created"}
    else:
        return {"message": "failed to create account"}


@app.get("/users")
def users(token: str):
    user_origin = authorization_manager.owner(token)
    if user_origin is None:
        return {"message": "invalid credentials"}
    return server_database.get_users(user_origin)


# TODO signout
