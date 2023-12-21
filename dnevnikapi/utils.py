from dataclasses import fields, is_dataclass
from datetime import datetime
from typing import Optional

import requests


def from_instance(cls, d):
    try:
        fieldtypes = {f.name: f.type for f in fields(cls)}
        return cls(
            **{
                f: from_instance(fieldtypes[f], d[f])
                if is_dataclass(fieldtypes[f])
                else d[f]
                for f in d
            }
        )
    except Exception:
        raise ValueError(f"incorrect values for {cls.__name__}")

def stringify_datetime(date: datetime):
    return date.strftime("%Y-%m-%d")

class APIHelper:
    BASE_URL = "https://dnevnik.egov66.ru/api"

    def __init__(self):
        self._session = requests.Session()
    
    def update_access_token(self, access_token: str):
        self._session.headers["Authorization"] = f"Bearer {access_token}"
    
    def _call_url(self, url, method, query=None, data=None) -> Optional[dict]:
        try:
            r = self._session.request(
                method, APIHelper.BASE_URL + url, params=query, json=data, timeout=30
            )
        except requests.exceptions.ReadTimeout:
            raise requests.exceptions.ReadTimeout(f"at {method} {url}")
        if r.status_code // 100 != 2:
            raise requests.exceptions.HTTPError(
                f"Return code {r.status_code} at {method} {url}"
            )

        if r.text == "":
            return {}

        try:
            return r.json()
        except requests.exceptions.JSONDecodeError:
            raise ValueError(f"Cant parse json at {method} {url}")

    def _call_post(self, url, data={}) -> dict:
        return self._call_url(url, "POST", data=data)

    def _call_get(self, url, query={}) -> dict:
        return self._call_url(url, "GET", query=query)