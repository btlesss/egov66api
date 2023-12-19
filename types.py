from dataclasses import dataclass, asdict, fields, is_dataclass
from typing import Optional, List
from enum import Enum
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


ANY_SUBJECT = "00000000-0000-0000-0000-000000000000"

@dataclass
class AuthData:
    accessToken: str = ""
    refreshToken: str = ""
    accessTokenExpirationDate: str = ""


@dataclass
class Student:
    firstName: str
    lastName: str
    surName: str
    className: str
    orgName: str
    id: str
    avatarId: Optional[str]


@dataclass
class AvailableStudents:
    isParent: bool
    students: List[Student]

    def __post_init__(self):
        self.students = [
            Student(**i) if type(i) != Student else i for i in self.students
        ]


@dataclass
class AnnounceFile:
    pass


@dataclass
class Announce:
    id: str
    date: str
    expired: str
    title: str
    description: str
    isImportant: bool
    hasFiles: bool
    isChecked: bool
    files: List[AnnounceFile]
    author: dict

@dataclass
class Period:
    id: str
    name: str


class Announcements(list):
    def __init__(self, announcements):
        super().__init__([Announce(**i) for i in announcements])
