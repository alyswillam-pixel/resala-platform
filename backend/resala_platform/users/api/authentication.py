from __future__ import annotations

from typing import TYPE_CHECKING

from knox.auth import TokenAuthentication
from rest_framework import exceptions
from rest_framework.authentication import CSRFCheck

if TYPE_CHECKING:
    from rest_framework.request import Request


class CookieTokenAuthentication(TokenAuthentication):
    """
    Authenticate requests using the knox token stored in an HttpOnly cookie
    """

    cookie_name = "knox_token"

    def authenticate(self, request: Request):
        token = request.COOKIES.get(self.cookie_name)
        if not token:
            return None

        user_auth_tuple = self.authenticate_credentials(token.encode("utf-8"))
        self.enforce_csrf(request)
        return user_auth_tuple

    def enforce_csrf(self, request):
        """
        Enforce CSRF validation for cookie-based authentication.
        """

        def dummy_get_response(request):
            return None

        check = CSRFCheck(dummy_get_response)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise exceptions.PermissionDenied(f"CSRF Failed: {reason}")
