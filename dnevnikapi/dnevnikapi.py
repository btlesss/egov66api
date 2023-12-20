from os import PathLike
from typing import Union, Optional, List, overload
from datetime import datetime, timedelta
from .types import *
from . import utils


class Dnevnik(utils.APIHelper):
    def __init__(
        self,
        login: Optional[str] = None,
        password: Optional[str] = None,
        auto_logout=True,
        auth_data: Optional[AuthData] = None
    ):
        """Login into account
        One of (login, password) and auth_data (or only refreshToken) must be specified.

        Args:
            login (str, optional): Defaults to None.
            password (str, optional): Defaults to None.
            auto_logout (bool, optional): If using in context manager. Defaults to True.
            auth_data (AuthData, optional): Defaults to None.
        """

        self.auto_logout = auto_logout
        self.student = None
        self.student: Optional[Student]
        self.auth_data: AuthData

        super().__init__()

        if auth_data:
            self.auth_data = auth_data
            tz = self.auth_data.accessTokenExpirationDate.tzinfo
            if self.auth_data.accessTokenExpirationDate < datetime.now(tz = tz):
                self.refresh()
        else:
            if login is None or password is None:
                raise ValueError("Login and password must be specified if no auth_data")

            r = self._call_post(
                "/auth/Auth/Login", {"login": login, "password": password}
            )
            self.auth_data = utils.from_instance(AuthData, r)
        
        self._update_access_token()

        r = utils.from_instance(AvailableStudents, self._call_get("/students"))
        self.available_students = r.students
        self.is_parent = r.isParent
        self.student = self.available_students[0]

    def _update_access_token(self):
        super().update_access_token(self.auth_data.accessToken)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.auto_logout:
            self.revoke()

    def revoke(self):
        if not self.auth_data:
            return

        self._call_post(
            "/auth/Token/Revoke", {"refreshToken": self.auth_data.refreshToken}
        )

    def refresh(self, refresh_token: str = ""):
        """Get new accessToken using old refreshToken

        Args:
            refresh_token (str, optional): Must be specified if no auth data. Defaults to auth_data.refreshToken.
        """
        if not (refresh_token or self.auth_data):
            raise ValueError("No refresh token")
        r = self._call_post(
                "/auth/Token/Refresh", {"refreshToken": self.auth_data.refreshToken or refresh_token}
            )
        self.auth_data = utils.from_instance(AuthData, r)
        self._update_access_token()

    def get_estimate_periods(self) -> List[Period]:
        r = self._call_get(
            "/estimate/periods",
            {"studentId": self.student.id, "schoolYear": datetime.today().year},
        )
        result = []
        for period in r["periods"]:
            result.append(utils.from_instance(Period, period))

        return result

    def get_estimate(self, period: str, year: Optional[int] = None):
        if year is None:
            year = datetime.today().year

        r = self._call_get(
            "/estimate",
            {
                "studentId": self.student.id,
                "schoolYear": year,
                "periodId": period,
                "monthId": "00000000-0000-0000-0000-000000000000",
                "subjectId": "00000000-0000-0000-0000-000000000000",
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