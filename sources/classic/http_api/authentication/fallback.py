from falcon import Request

from .base import Authenticator, AuthenticationFailed


class FallbackAuthenticator(Authenticator):

    def __init__(self, authenticators: list[Authenticator], **kwargs):
        super().__init__(**kwargs)
        self.authenticators = authenticators

    def __call__(self, request: Request) -> object:
        identity = None
        for authenticator in self.authenticators:
            try:
                identity = authenticator(request)
            except AuthenticationFailed:
                continue

        if identity is None:
            raise AuthenticationFailed()

        if self.factory:
            return self.factory(identity)
