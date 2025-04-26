from typing import Optional

from pydantic import BaseModel


class Server(BaseModel):
    url: str
    description: Optional[str] = None
    variables: Optional[dict[str, "ServerVariable"]] = None


class ServerVariable(BaseModel):
    default: str
    enum: Optional[list[str]] = None
    description: Optional[str] = None
