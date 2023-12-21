from datetime import datetime
from os.path import isfile
from typing import Optional
import pickle

from ..types import AuthData
from .abstract import AbstractStorage


class FileStorage(AbstractStorage):
    def __init__(self, name: str) -> None:
        self._name = name
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._expiration_date: Optional[datetime] = None

        self._read()

    def is_expired(self) -> bool:
        tz = self._expiration_date.tzinfo
        return self._expiration_date < datetime.now(tz=tz)

    def update_auth_data(self, auth_data: AuthData) -> AbstractStorage:
        self._access_token = auth_data.accessToken
        self._refresh_token = auth_data.refreshToken
        self._expiration_date = auth_data.accessTokenExpirationDate
        self._write()

    @property
    def access_token(self) -> Optional[str]:
        return self._access_token

    def remove_access_token(self):
        self._access_token = None
        self._write()

    @property
    def refresh_token(self) -> Optional[str]:
        return self._refresh_token

    def _read(self):
        if not isfile(self._name):
            open(self._name, "w").close()
            return

        with open(self._name, "rb") as f:
            self.update_auth_data(pickle.loads(f.read()))

    def _write(self):
        with open(self._name, "wb") as f:
            f.write(
                pickle.dumps(
                    AuthData(
                        self._access_token, self._refresh_token, self._expiration_date
                    )
                )
            )
