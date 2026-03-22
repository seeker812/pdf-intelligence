from enum import Enum


class ErrorCode(str, Enum):
    BAD_REQUEST = "BAD_REQUEST"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DOCUMENT_PROCESSING_ERROR = "DOCUMENT_PROCESSING_ERROR"
    CONFLICT = "CONFLICT"


class ErrorStatus(int, Enum):
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503
    CONFLICT = 409


class AppBaseException(Exception):
    status_code: int = ErrorStatus.INTERNAL_SERVER_ERROR
    code: str = ErrorCode.INTERNAL_SERVER_ERROR

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ConflictException(AppBaseException):
    status_code = ErrorStatus.CONFLICT
    code: str = ErrorCode.CONFLICT


class BadRequestException(AppBaseException):
    status_code = ErrorStatus.BAD_REQUEST
    code = ErrorCode.BAD_REQUEST


class UnAuthorizedException(AppBaseException):
    status_code = ErrorStatus.UNAUTHORIZED
    code = ErrorCode.UNAUTHORIZED


class ForbiddenException(AppBaseException):
    status_code = ErrorStatus.FORBIDDEN
    code = ErrorCode.FORBIDDEN


class RecordNotFoundException(AppBaseException):
    status_code = ErrorStatus.NOT_FOUND
    code = ErrorCode.NOT_FOUND


class InternalServerError(AppBaseException):
    status_code = ErrorStatus.INTERNAL_SERVER_ERROR
    code = ErrorCode.INTERNAL_SERVER_ERROR


class ServiceUnavailableError(AppBaseException):
    status_code = ErrorStatus.SERVICE_UNAVAILABLE
    code = ErrorCode.SERVICE_UNAVAILABLE


class DocumentProcessingError(AppBaseException):
    status_code = ErrorStatus.INTERNAL_SERVER_ERROR
    code = ErrorCode.DOCUMENT_PROCESSING_ERROR
