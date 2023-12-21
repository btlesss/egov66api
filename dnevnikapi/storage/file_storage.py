from datetime import datetime
from os.path import isfile
from typing import Callable, Generator, Iterable, Optional

from ..types import AuthData
from .abstract import AbstractStorage


def cast_iterator(iterator: Iterable[str],
                  types: Iterable[Callable[[str], ...]]
                  ) -> Generator:
    # Append None to iterator for types lenght
    iterator = [
        *iterator,
        *(None for _ in range(len(types)-len(iterator)))
    ]
    return (t(v) if v else None
            for v, t in zip(iterator, types))


class FileStorage(AbstractStorage):
    def __init__(self, name: str) -> None:
        self._name = name
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._expiration_date: Optional[datetime] = None

        self._read()

    def is_expired(self) -> bool:
        tz = self._expiration_date.tzinfo
        return self._expiration_date < datetime.now(tz = tz)

    def update_auth_data(self, auth_data: AuthData) -> 'AbstractStorage':
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
            open(self._name, 'w').close()

        with open(self._name, 'r') as f:
            (
                self._access_token, self._refresh_token,
                self._expiration_date
            ) = cast_iterator(
                list(map(str.strip, f.readlines())),
                (str, str, datetime.fromisoformat)
            )

    def _write(self):
        with open(self._name, 'w') as f:
            f.writelines(map(
                lambda v: ("" if v is None else v)+'\n',
                (
                    self._access_token, self._refresh_token,
                    self._expiration_date.isoformat()
                )
            ))
