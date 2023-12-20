from dataclasses import dataclass, asdict, fields, is_dataclass
from os import access
import requests
from typing import Optional
from datetime import datetime

def from_instance(klass, d):
    try:
        fieldtypes = {f.name: f.type for f in fields(klass)}
        return klass(
            **{
                f: from_instance(fieldtypes[f], d[f])
                if is_dataclass(fieldtypes[f])
                else d[f]
                for f in d
            }
        )
    except:
        raise ValueError(f"incorrect values for {klass.__name__}")

def stringify_datetime(date: datetime):
    return date.strftime("%Y-%m-%d")

class APIHelper:
    BASE_URL = "https://dnevnik.egov66.ru/api"

    def __init__(self):
        self.session = requests.Session()
    
    def update_access_token(self, access_token: str):
        self.session.headers["Authorization"] = f"Bearer {access_token}"
    
    def _call_url(self, url, method, query=None, data=None) -> Optional[dict]:
        try:
            r = self.session.request(
                method, APIHelper.BASE_URL + url, params=query, json=data, timeout=30
            )
        except requests.exceptions.ReadTimeout:
            raise requests.exceptions.ReadTimeout(f"at {method} {url}")
        if r.status_code != 200:
            raise ValueError(f"Return code {r.status_code} at {method} {url}")

        if r.text == "":
            return {}

        try:
            return r.json()
        except:
            raise ValueError(f"Cant parse json at {method} {url}")

    def _call_post(self, url, data={}) -> dict:
        return self._call_url(url, "POST", data=data)

    def _call_get(self, url, query={}) -> dict:
        return self._call_url(url, "GET", query=query)