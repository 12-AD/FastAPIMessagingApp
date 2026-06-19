from api_queries import (
    db_send_message,
    db_delete_message,
    db_edit_message,
    db_get_changed_or_new_messages,
    db_check_owner_of_message_id,
    db_register_user,
    db_initial_load,
    db_load_more,
    db_check_username_and_password,
    db_username_exists,
    db_get_users,
)


class Database:
    def __init__(self):
        self.__MAX_MESSAGE_LENGTH = 300

    def send_message(self, message, user_destination, user_origin):
        if len(message) > self.__MAX_MESSAGE_LENGTH:
            return {"message": "Message too long"}
        message_id = db_send_message(
            message, user_origin, user_destination
        )  # insert in DB
        return {"message": "sent", "message_id": message_id}

    def delete_message(self, message_id, user_origin):
        message_owner = db_check_owner_of_message_id(message_id)
        if message_owner is None:
            return {"message": f"Message: {message_id}, does not exist"}
        if message_owner != user_origin:
            return {"message": "this message does not belong to you"}
        if db_delete_message(message_id) == 1:
            return {"message": "deleted"}
        else:
            return {"message": "message failed to delete"}

    def edit_message(self, message_id, user_origin, message):
        if len(message) > self.__MAX_MESSAGE_LENGTH:
            return {"message": "Message too long"}
        message_owner = db_check_owner_of_message_id(message_id)
        if message_owner is None:
            return {"message": f"Message: {message_id}, does not exist"}
        if message_owner != user_origin:
            return {"message": "this message does not belong to you"}
        if db_edit_message(message_id, message) == 1:
            return {"message": "changed"}
        else:
            return {"message": "failed to edit message"}

    def load_messages(self, user_origin, user_destination, limit, before_id):
        if before_id is None:  # load 50 messages on launch
            return db_initial_load(user_origin, user_destination, limit)
        else:  # load more messages when user scrolls up
            return db_load_more(user_origin, user_destination, limit, before_id)

    def changed_or_new_messages(self, user_origin, user_destination, last_seen_time):
        return db_get_changed_or_new_messages(
            user_origin, user_destination, last_seen_time
        )

    def login(self, username, password):
        return db_check_username_and_password(username, password)

    def check_user(self, username):
        return db_username_exists(username)

    def register(self, username, password):
        return db_register_user(username, password)

    def get_users(self, user_origin):
        return db_get_users(user_origin)
