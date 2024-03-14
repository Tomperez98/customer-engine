from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

BearerToken = Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())]
