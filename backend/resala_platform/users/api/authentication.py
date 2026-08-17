from rest_framework import exceptions
from rest_framework.request import Request

from knox.auth import TokenAuthentication


class CookieTokenAuthentication(TokenAuthentication):
    """
    Authenticate requests using the knox token stored in an HttpOnly cookie
    """

    cookie_name = "knox_token"

    def authenticate(self, request: Request):
        token = request.COOKIES.get(self.cookie_name)
        if not token:
            return None

        return self.authenticate_credentials(token.encode("utf-8"))
