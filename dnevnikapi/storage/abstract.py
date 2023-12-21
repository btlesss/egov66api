from typing import Optional

from ..types import AuthData


class AbstractStorage:
    def is_expired(self) -> bool:
        raise NotImplementedError
    
    def update_auth_data(self, auth_data: AuthData) -> 'AbstractStorage':
        raise NotImplementedError
    
    @property
    def access_token(self) -> Optional[str]:
        raise NotImplementedError

    def remove_access_token(self):
        raise NotImplementedError

    @property
    def refresh_token(self) -> Optional[str]:
        raise NotImplementedError

    def close(self):
        pass
