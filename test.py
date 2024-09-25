# -------------------------------------------------------------------
# Project:    InterRIoT-2024S2-fastapi-security-1
# Filename:   test.py
# Location:   ./
# Author:     Adrian Gould <adrian.gould@nmtafe.wa.edu.au>
# Created:    2024-09-24
# Purpose:
#    This file provides the following features, methods and associated 
#    supporting code:
#    
# ---------------------------------------------------------------------

import base64
import binascii

import casbin
import uvicorn
from fastapi import FastAPI
from starlette.authentication import AuthenticationBackend, AuthenticationError, SimpleUser, AuthCredentials
from starlette.middleware.authentication import AuthenticationMiddleware

from fastapi_authz import CasbinMiddleware

app = FastAPI()


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


enforcer = casbin.Enforcer('./policies/rbac_model.conf', './policies/rbac_policy.csv')

backend = BasicAuth()

app.add_middleware(CasbinMiddleware, enforcer=enforcer)
app.add_middleware(AuthenticationMiddleware, backend=BasicAuth())


@app.get('/')
async def index():
    return "If you see this, you have been authenticated."


@app.get('/dataset1/protected')
async def auth_test():
    return "You must be alice to see this."
