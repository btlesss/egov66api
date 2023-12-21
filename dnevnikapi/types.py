from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional

ANY_SUBJECT = "00000000-0000-0000-0000-000000000000"

@dataclass
class AuthData:
    accessToken: str
    refreshToken: str
    accessTokenExpirationDate: datetime

    def __post_init__(self):
        if not isinstance(self.accessTokenExpirationDate, datetime):
            self.accessTokenExpirationDate = datetime.fromisoformat(self.accessTokenExpirationDate)


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

@dataclass
class PaginationData:
    pageNumber: int
    totalPages: int
    hasPreviousPage: bool
    hasNextPage: bool

class GradesType(Enum):
    PERIOD = "periodGradesTable"
    WEEK = "weekGradesTable"
    YEAR = "weekGradesTable"

def _parse_valued_timestamp(date: str, hour: int, minute: int) -> datetime:
    date = datetime.fromisoformat(date)
    return date.replace(hour=hour, minute=minute)

class WeekGrades:
    @dataclass
    class Lesson:
        beginDate: datetime
        endDate: datetime
        grades: List[str]
        name: str
    
    @dataclass
    class Grades:
        beginDate: datetime
        endDate: datetime
        paginationData: PaginationData
        lessons: List
    
    Grades.lessons: List[Lesson]


class Announcements(list):
    def __init__(self, announcements):
        super().__init__([Announce(**i) for i in announcements])
