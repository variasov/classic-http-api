from functools import wraps
from typing import Any, Callable

from classic.components import add_extra_annotation, doublewrap
from classic.error_handling import Error

from falcon import Request, Response


Factory = Callable[[Any], Any]


class Authenticator:

    def __init__(self, factory: Factory = None):
        self.factory = factory

    def __call__(self, request: Request):
        raise NotImplementedError


class AuthenticationFailed(Error):

    def __init__(self, reason: str = 'Authentication failed'):
        self.message = reason


@doublewrap
def authenticate(method, prop: str = 'authenticator'):
    """

    """

    @wraps(method)
    def wrapper(self, request: Request, *args, **kwargs):
        authenticator = getattr(self, prop)
        try:
            authenticator(request)
        except KeyError:
            raise AuthenticationFailed

        return method(self, request, *args, **kwargs)

    return add_extra_annotation(wrapper, prop, Authenticator)


class AuthenticationMiddleware:
    authenticate: Authenticator

    def __init__(self, authenticator: Authenticator):
        self.authenticate = authenticator

    def process_request(self, request: Request, response: Response):
        self.authenticate(request)
