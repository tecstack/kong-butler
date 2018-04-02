# -*- coding:utf-8 -*-
# !/usr/bin/env python
#
# Author: daisheng
# Email: shawntai.ds@gmail.com

from utils import logger


class KongError(Exception):

    def __init__(self, message=None, context=None):
        super(KongError, self).__init__(message)
        self.message = message
        self.context = context
        logger.error('KongError:%s' % message)


class KongAdmConnectionTimeoutError(KongError):
    pass


class KongAdmAuthFaildError(KongError):
    pass


class KongAdmPermissionError(KongError):
    pass


class KongAdmDBUnreachable(KongError):
    pass


class KongAdmUnkownConnError(KongError):
    pass


class ResourceNotFoundError(KongError):
    pass


class MethodNotAllowedError(KongError):
    pass


class AuthenticationError(KongError):
    pass


class ServerError(KongError):
    pass


class BadGatewayError(KongError):
    pass


class ServiceUnavailableError(KongError):
    pass


class BadRequestError(KongError):
    pass


class ForbiddenError(KongError):
    pass


class RateLimitExceededError(KongError):
    pass


class MultipleMatchingUsersError(KongError):
    pass


class UnexpectedError(KongError):
    pass


class TokenUnauthorizedError(KongError):
    pass


class ConflictError(KongError):
    pass


class UnsupportedMediaTypeError(KongError):
    pass


error_codes = {
    400: BadRequestError,
    401: AuthenticationError,
    403: ForbiddenError,
    404: ResourceNotFoundError,
    405: MethodNotAllowedError,
    409: ConflictError,
    415: UnsupportedMediaTypeError,
    500: ServerError,
    502: BadGatewayError,
    503: ServiceUnavailableError
}


class UsernameDuplicateError(KongError):
    pass
