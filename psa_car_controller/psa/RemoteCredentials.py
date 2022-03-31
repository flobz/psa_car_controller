from datetime import datetime


class RemoteCredentials:
    def __init__(self, remote_refresh_token):
        self._refresh_token = remote_refresh_token
        self.access_token = None
        self.update_callbacks = []
        self.last_update = datetime.fromtimestamp(0)

    def __update_callbacks(self):
        self.last_update = datetime.now()
        for update_callback in self.update_callbacks:
            update_callback()

    @property
    def refresh_token(self):
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, remote_refresh_token):
        self._refresh_token = remote_refresh_token
        self.__update_callbacks()
