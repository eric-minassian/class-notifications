import os
import time
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from helpers.notification import Notification

URL = "https://www.reg.uci.edu/perl/WebSoc"
TIMEOUT = 30
MAX_ERROR_COUNT = 5


@dataclass
class CourseStatus:
    instructor: str
    modality: str
    time: str
    limit: int
    enr: int
    waitlist: str
    rstr: str
    status: str

    def __str__(self):
        return f"""
        Instructor: {self.instructor}
        Modality: {self.modality}
        Time: {self.time}
        Limit: {self.limit}
        Enr: {self.enr}
        Waitlist: {self.waitlist}
        Rstr: {self.rstr}
        Status: {self.status}
        """


def get_status(year_term: str, course_code: str) -> CourseStatus:
    response = requests.post(
        URL,
        data={
            "YearTerm": year_term,
            "CourseCodes": course_code,
        },
    )

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        for tr in soup.find_all("tr", valign="top", bgcolor="#FFFFCC"):
            data = tr.find_all("td")

            return CourseStatus(
                instructor=data[4].text.strip(),
                modality=data[5].text.strip(),
                time=data[6].text.strip(),
                limit=int(data[8].text),
                enr=int(data[9].text),
                waitlist=data[10].text.strip(),
                rstr=data[13].text.strip(),
                status=data[-1].text.strip(),
            )

    raise Exception("Failed to get status")


if __name__ == "__main__":
    load_dotenv()

    app_token = os.environ["PUSHOVER_APP_TOKEN"]
    user_key = os.environ["PUSHOVER_USER_KEY"]
    year_term = os.environ["YEAR_TERM"]
    course_code = os.environ["COURSE_CODE"]

    notification = Notification(app_token, user_key)

    prev = None
    error_count = 0

    while True:
        try:
            status = get_status(year_term, course_code)
            if status != prev:
                print(status)

                if not notification.send_message(str(status)):
                    raise Exception("Failed to send message")

                prev = status

            error_count = 0
        except Exception as e:
            print(e)
            error_count += 1
            if error_count > MAX_ERROR_COUNT:
                notification.send_message("Quitting due to too many errors")
                break

        time.sleep(TIMEOUT)
