# -------------------------------------------------------------------
# Project:    InterRIoT-2024S2-fastapi-security-1
# Filename:   basicauth.py
# Location:   ./
# Author:     Adrian Gould <adrian.gould@nmtafe.wa.edu.au>
# Created:    2024-09-24
# Purpose:
#    To provide a basic authentication mechanism for PBAC demo
#    
# ---------------------------------------------------------------------
import base64
import binascii

from starlette.authentication import (
    AuthenticationBackend,
    AuthenticationError,
    AuthCredentials,
    SimpleUser
)

class BasicAuth(AuthenticationBackend):
    async def authenticate(self, request):
        if "Authorization" not in request.headers:
            return None

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            decoded = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise AuthenticationError("Invalid basic auth credentials")

        username, _, password = decoded.partition(":")
        return AuthCredentials(["authenticated"]), SimpleUser(username)
