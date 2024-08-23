from typing import Any, Sequence, Optional

from falcon import Request

try:
    import jwt
except ImportError:
    pass


from .base import Authenticator, AuthenticationFailed


class JWTAuthenticator(Authenticator):

    def __init__(
        self,
        secret_key: str,
        field: str = 'sub',
        algorithms: Sequence[str] = None,
        decoding_options: Optional[dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)

        self.secret_key = secret_key
        self.algorithms = algorithms or ['HS256']
        self.decoding_options = decoding_options
        self.field = field

        try:
            jwt
        except NameError as error:
            raise ImportError(f'Package {error.name} should be installed')

    def __call__(self, request: Request) -> None:
        token = self._extract_token(request)
        request.context.jwt = self._decode_token(token)
        self._set_identity(request)

    def _set_identity(self, request: Request):
        request.context.identity = self.factory(
            request.context.jwt[self.field]
        )

    def _extract_token(self, request: Request) -> str:
        try:
            return request.auth.split(' ')[-1]
        except KeyError:
            raise AuthenticationFailed(
                'Authorization header must contain 2 value, '
                'splitted by whitespace'
            )
        except AttributeError:
            raise AuthenticationFailed('No Authorization header')

    def _decode_token(self, token: str):
        try:
            return jwt.decode(
                token,
                self.secret_key,
                algorithms=self.algorithms,
                options=self.decoding_options,
            )
        except jwt.DecodeError:
            raise AuthenticationFailed('Token decoding error')
        except jwt.PyJWTError as e:
            raise AuthenticationFailed(f'Unexpected token error [{str(e)}]')
