from enum import Enum
from typing import Self


class EnumHttpStatusCode(Enum):
    Continue = 100
    SwitchingProtocols = 101
    Processing = 102
    EarlyHints = 103
    UploadResumptionSupported = 104
    OK = 200
    Created = 201
    Accepted = 202
    NonAuthoritativeInformation = 203
    NoContent = 204
    ResetContent = 205
    PartialContent = 206
    MultiStatus = 207
    AlreadyReported = 208
    IMUsed = 226
    MultipleChoices = 300
    MovedPermanently = 301
    Found = 302
    SeeOther = 303
    NotModified = 304
    UseProxy = 305
    TemporaryRedirect = 307
    PermanentRedirect = 308
    BadRequest = 400
    Unauthorized = 401
    PaymentRequired = 402
    Forbidden = 403
    NotFound = 404
    MethodNotAllowed = 405
    NotAcceptable = 406
    ProxyAuthenticationRequired = 407
    RequestTimeout = 408
    Conflict = 409
    Gone = 410
    LengthRequired = 411
    PreconditionFailed = 412
    ContentTooLarge = 413
    URITooLong = 414
    UnsupportedMediaType = 415
    RangeNotSatisfiable = 416
    ExpectationFailed = 417
    Unused = 418
    MisdirectedRequest = 421
    UnprocessableContent = 422
    Locked = 423
    FailedDependency = 424
    TooEarly = 425
    UpgradeRequired = 426
    Unassigned = 427
    PreconditionRequired = 428
    TooManyRequests = 429
    RequestHeaderFieldsTooLarge = 431
    UnavailableForLegalReasons = 451
    InternalServerError = 500
    NotImplemented = 501
    BadGateway = 502
    ServiceUnavailable = 503
    GatewayTimeout = 504
    HTTPVersionNotSupported = 505
    VariantAlsoNegotiates = 506
    InsufficientStorage = 507
    LoopDetected = 508
    NetworkAuthenticationRequired = 511

    @classmethod
    def safe_init(cls, value: int | str) -> Self:
        if isinstance(value, str) and value.isdigit():
            value = int(value)
        return cls(value)

    def is_success_status_code(self) -> bool:
        return bool(self.value >= 200 and self.value < 300)

    def is_redirect_status_code(self) -> bool:
        return bool(self.value >= 300 and self.value < 400)

    def is_error_status_code(self) -> bool:
        return bool(self.value >= 400 and self.value < 600)
