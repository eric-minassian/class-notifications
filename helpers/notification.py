import http.client
from urllib.parse import urlencode

RETRY_COUNT = 3


class Notification:
    def __init__(self, app_token: str, user_key: str):
        self.app_token = app_token
        self.user_key = user_key

    def send_message(self, message: str) -> bool:
        for _ in range(RETRY_COUNT):
            response = self._send_message(message)

            if response.status == 200:
                return True

        return False

    def _send_message(self, message: str) -> http.client.HTTPResponse:
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request(
            "POST",
            "/1/messages.json",
            urlencode(
                {
                    "token": self.app_token,
                    "user": self.user_key,
                    "message": message,
                }
            ),
            {"Content-type": "application/x-www-form-urlencoded"},
        )

        return conn.getresponse()
