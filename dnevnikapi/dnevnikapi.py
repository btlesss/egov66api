from datetime import datetime, timedelta
from typing import List, Optional, Union

from . import utils
from .storage.abstract import AbstractStorage
from .storage.file_storage import FileStorage
from .types import (
    ANY_SUBJECT,
    Announcements,
    AuthData,
    AvailableStudents,
    Period,
    Student,
)


class Dnevnik(utils.APIHelper):
    def __init__(
        self,
        login: Optional[str] = None,
        password: Optional[str] = None,
        auto_logout=False,
        auth_storage: Optional[AbstractStorage] = None
    ):
        """Login into account

        Args:
            login (`str`, optional): Defaults to `None`.
            password (`str`, optional): Defaults to `None`.
            auto_logout (`bool`, optional): Revoke access hash but save refresh hash. Work if instance used in context manager. Defaults to `False`.
            auth_storage (`AbstractStorage`, optional): Specify storage type. Defaults to `FileStorage` with login as filename.
        """

        if auth_storage is None:
            auth_storage = FileStorage(f"{login}.data")
        self.auto_logout = auto_logout
        self.auth_storage = auth_storage
        self.student: Optional[Student] = None

        super().__init__()

        if self.auth_storage.refresh_token is None:
            if login is None or password is None:
                raise ValueError("Login and password must be specified if auth_storage is empty")

            r = self._call_post(
                "/auth/Auth/Login", {"login": login, "password": password}
            )
            self.auth_storage.update_auth_data(utils.from_instance(AuthData, r))
        elif not self.auth_storage.access_token or self.auth_storage.is_expired():
            self.refresh()
        
        self.update_access_token(self.auth_storage.access_token)

        r = utils.from_instance(AvailableStudents, self._call_get("/students"))
        self.available_students = r.students
        self.is_parent = r.isParent
        self.student = self.available_students[0]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.auto_logout:
            self.revoke()
        
        self.auth_storage.close()

    def revoke(self):
        if not self.auth_storage.refresh_token:
            return
        self.auth_storage.remove_access_token()
        self._call_post(
            "/auth/Token/Revoke", {"refreshToken": self.auth_storage.refresh_token}
        )

    def refresh(self, refresh_token: str = ""):
        """Get new accessToken using old refreshToken

        Args:
            refresh_token (str, optional): Must be specified if no auth data. Defaults to auth_storage.refresh_token.
        """
        if not (refresh_token or self.auth_storage.refresh_token):
            raise ValueError("No refresh token")

        r = self._call_post(
            "/auth/Token/Refresh",
            {"refreshToken": self.auth_storage.refresh_token or refresh_token}
        )
        self.auth_storage.update_auth_data(utils.from_instance(AuthData, r))
        self.update_access_token(self.auth_storage.access_token)

    def get_estimate_periods(self) -> List[Period]:
        r = self._call_get(
            "/estimate/periods",
            {"studentId": self.student.id, "schoolYear": datetime.today().year},
        )
        result = []
        for period in r["periods"]:
            result.append(utils.from_instance(Period, period))

        return result

    def get_estimate(self, period: str, year: Optional[int] = None,
                     mounth: str = ANY_SUBJECT, subject: str = ANY_SUBJECT):
        if year is None:
            year = datetime.today().year

        r = self._call_get(
            "/estimate",
            {
                "studentId": self.student.id,
                "schoolYear": year,
                "periodId": period,
                "monthId": mounth,
                "subjectId": subject,
            },
        )
        return r

    def get_homework(self, date: Union[datetime, timedelta] = None) -> dict:
        """Get Homework
        [Not fully implemented]

        Args:
            date (Union[datetime,timedelta], optional): Date of homework or timedelta from today. Defaults to datetime.today().

        Returns:
            dict: raw output
        """
        if date is None:
            date = datetime.today()

        if isinstance(date, timedelta):
            date = datetime.today() + date
        print({"date": utils.stringify_datetime(date), "studentId": self.student.id})
        r = self._call_get(
            "/homework",
            {"date": utils.stringify_datetime(date), "studentId": self.student.id},
        )

        return r

    def get_announcements(self) -> Announcements:
        r = self._call_get("/announcements", {"studentId": self.student.id})
        print(r)
        return Announcements(r["announcements"])
