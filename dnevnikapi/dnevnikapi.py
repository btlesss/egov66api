import requests
from typing import Union, Optional, List, overload
from datetime import datetime, timedelta
from .types import *


BASE_URL = "https://dnevnik.egov66.ru/api"

def require_student(f):
    def _wrapper(self, *args, **kwargs):
        if self.student is None:
            raise ValueError("No student selected.")
        f(self, *args, **kwargs)
    return _wrapper

class Dnevnik:
    def __init__(
        self,
        login: Optional[str] = None,
        password: Optional[str] = None,
        auto_logout=True,
        auth_data: Optional[AuthData] = None,
    ):
        """Login into account

        Args:
            login (str): Login
            password (str): Non-hashed password
        """


        self.auto_logout = auto_logout
        self._session = requests.Session()

        if auth_data:
            self.auth_data = auth_data
        else:
            if login is None or password is None:
                raise ValueError("Login and password must be specified if no auth_data")

            r = self._call_post(
                "/auth/Auth/Login", {"login": login, "password": password}
            )
            self.auth_data = from_instance(AuthData, r)
        
        self.auth_data: AuthData

        self.student = None
        self.student: Optional[Student]

        self._session.headers["Authorization"] = f"Bearer {self.auth_data.accessToken}"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.auto_logout:
            self.revoke()

    def _call_url(self, url, method, query=None, data=None) -> Optional[dict]:
        try:
            r = self._session.request(
                method, BASE_URL + url, params=query, json=data, timeout=30
            )
        except requests.exceptions.ReadTimeout:
            raise requests.exceptions.ReadTimeout(f"at {method} {url}")
        if r.status_code != 200:
            raise ValueError(f"Return code {r.status_code} at {method} {url}")

        if r.text == "":
            raise ValueError(f"Error server response empty at {method} {url}")

        try:
            return r.json()
        except:
            raise ValueError(f"Cant parse json at {method} {url}")

    def _call_post(self, url, data={}) -> dict:
        return self._call_url(url, "POST", data=data)

    def _call_get(self, url, query={}) -> dict:
        return self._call_url(url, "GET", query=query)

    def _stringify_datetime(self, date: datetime):
        return date.strftime("%Y-%m-%d")

    @require_student
    def get_periods(self) -> List[Period]:
        r = self._call_get(
            "/estimate/periods", {"studentId": self.student.id, "schoolYear": datetime.today().year}
        )
        result = []
        for period in r["periods"]:
            result.append(from_instance(Period, period))

        return result

    @require_student
    def get_marks(self, period: str, year: Optional[int] = None):
        if year is None:
            year = datetime.today().year
        
        r = self._call_get(
            "/estimate",
            {
                "studentId": self.student.id,
                "schoolYear": year,
                "periodId": self._get_period(),
                "monthId": "00000000-0000-0000-0000-000000000000",
                "subjectId": "00000000-0000-0000-0000-000000000000",
            },
        )
        return r

    def revoke(self):
        if not self.auth_data:
            return

        self._call_post(
            "/auth/Token/Revoke", {"refreshToken": self.auth_data.refreshToken}
        )

    def get_students(self) -> Union[AvailableStudents, Student]:
        r = self._call_get("/students")
        r = from_instance(AvailableStudents, r)

        if len(r.students) == 1:
            self.student = r.students[0]
            return r.students[0]

        return r

    @require_student
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
        r = self._call_get(
            "/homework",
            {"date": self._stringify_datetime(date), "studentId": self.student.id},
        )
        return r
    
    
    @require_student
    def get_announcements(self) -> Announcements:
        r = self._call_get("/announcements", {"studentId": self.student.id})
        return Announcements(r["announcements"])
