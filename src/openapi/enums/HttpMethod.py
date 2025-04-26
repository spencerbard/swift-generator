from enum import StrEnum


class EnumHttpMethod(StrEnum):
    get = "get"
    put = "put"
    post = "post"
    delete = "delete"
    options = "options"
    head = "head"
    patch = "patch"
    trace = "trace"
