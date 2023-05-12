import bcrypt
import streamlit as st


class Authenticate:
    def __init__(self, credentials: dict):
        """
        Create a new instance of "Authenticate".
        Parameters
        ----------
        credentials: dict
            The dictionary of usernames, names, passwords, and emails.
        """
        self.credentials = credentials
        self.credentials["usernames"] = {
            key.lower(): value for key, value in credentials["usernames"].items()
        }

        if "authentication_status" not in st.session_state:
            st.session_state["authentication_status"] = None
        if "username" not in st.session_state:
            st.session_state["username"] = None

    def _check_pw(self) -> bool:
        """
        Checks the validity of the entered password.
        Returns
        -------
        bool
            The validity of the entered password by comparing it to the hashed password on disk.
        """
        return bcrypt.checkpw(
            self.password.encode(),
            self.credentials["usernames"][self.username]["password"].encode(),
        )

    def _check_credentials(self) -> bool:
        """
        Checks the validity of the entered credentials.
        Parameters
        ----------
        inplace: bool
            Inplace setting, True: authentication status will be stored in session state,
            False: authentication status will be returned as bool.
        Returns
        -------
        bool
            Validity of entered credentials.
        """
        if self.username in self.credentials["usernames"]:
            if self._check_pw():
                st.session_state["username"] = self.credentials["usernames"][
                    self.username
                ]["name"]
                st.session_state["authentication_status"] = True
                return True
        st.session_state["authentication_status"] = False

    def login(self, form_name: str) -> tuple:
        """
        Creates a login widget.
        Parameters
        ----------
        form_name: str
            The rendered name of the login form.
        Returns
        -------
        str
            Name of the authenticated user.
        bool
            The status of authentication, None: no credentials entered,
            False: incorrect credentials, True: correct credentials.
        str
            Username of the authenticated user.
        """
        login_form = st.form("Login")
        login_form.subheader(form_name)
        self.username = login_form.text_input("Username").lower()
        st.session_state["username"] = self.username
        self.password = login_form.text_input("Password", type="password")

        if login_form.form_submit_button("Login"):
            self._check_credentials()
            st.experimental_rerun()

    def logout(self, button_name: str):
        """
        Creates a logout button.
        Parameters
        ----------
        button_name: str
            The rendered name of the logout button.
        location: str
            The location of the logout button i.e. main or sidebar.
        """
        if st.button(button_name):
            st.session_state["username"] = None
            st.session_state["authentication_status"] = None
            st.experimental_rerun()

    def _get_username(self, key: str, value: str) -> str:
        """
        Retrieves username based on a provided entry.
        Parameters
        ----------
        key: str
            Name of the credential to query i.e. "email".
        value: str
            Value of the queried credential i.e. "jsmith@gmail.com".
        Returns
        -------
        str
            Username associated with given key, value pair i.e. "jsmith".
        """
        for username, entries in self.credentials["usernames"].items():
            if entries[key] == value:
                return username
        return False
