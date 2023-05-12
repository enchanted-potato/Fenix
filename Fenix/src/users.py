from src.database import Database
from src.hasher import Hasher


class Users:
    """
    Gets the list of users from the users table of the database and can also add new users to it.
    """

    @staticmethod
    def add_new_user(username: str, email: str, password: str):
        hashed_password = Hasher([password]).generate()[0]
        user_dict = {"username": username, "email": email, "password": hashed_password}
        with Database(db="fenixdatabase") as db:
            db.insert_dict_to_table("users", user_dict)

    @staticmethod
    def get_user_list(database: str = "fenixdatabase"):
        with Database(db=database) as db:
            query = "SELECT * FROM users"
            result = db.execute_query(query)
            return {
                "usernames": {
                    r[0]: {"email": r[1], "name": r[0], "password": r[2]}
                    for r in result
                }
            }
