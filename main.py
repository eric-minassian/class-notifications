import os
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from helpers.notification import Notification

URL = "https://www.reg.uci.edu/perl/WebSoc"
TIMEOUT = 30
MAX_ERROR_COUNT = 5


def get_status(year_term: str, course_code: str):
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
            return tr.find_all("td")[-1].text

    raise Exception("Failed to get status")


if __name__ == "__main__":
    load_dotenv()

    app_token = os.environ["PUSHOVER_APP_TOKEN"]
    user_key = os.environ["PUSHOVER_USER_KEY"]
    year_term = os.environ["YEAR_TERM"]
    course_code = os.environ["COURSE_CODE"]

    notification = Notification(app_token, user_key)

    prev = ""
    error_count = 0

    while True:
        try:
            status = get_status(year_term, course_code)
            if status != prev:
                print(status)

                if not notification.send_message(f"Status: {status}"):
                    raise Exception("Failed to send message")

                prev = status

            error_count = 0
        except Exception as e:
            print(e)
            error_count += 1
            if error_count > MAX_ERROR_COUNT:
                break

        time.sleep(TIMEOUT)
