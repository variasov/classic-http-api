from functools import wraps
from typing import Type, Optional

from classic.components import doublewrap
from falcon import Request, Response
import msgspec


@doublewrap
def specification(
    method,
    summary: Optional[str] = None,
    media: Optional[Type] = None,
    response: Optional[Type] = None,
    query: Optional[Type] = None,
    header: Optional[Type] = None,
    cookie: Optional[Type] = None,
    deprecated: bool = False,
):
    @wraps(method)
    def wrapper(resource, req: Request, resp: Response, **kwargs):
        if query:
            req.context.query = msgspec.convert(
                req.params, type=query, strict=False,
            )
        if header:
            req.context.headers = msgspec.convert(
                req.headers, type=header, strict=False,
            )
        if cookie:
            req.context.cookies = msgspec.convert(
                req.cookies, type=cookie, strict=False,
            )
        if media:
            req.context.media = msgspec.json.decode(
                req.bounded_stream.read(),
                type=media,
            )
        method(resource, req, resp, **kwargs)

    wrapper.__specification__ = dict(
        summary=summary,
        request_type=media,
        response_type=response,
        query_type=query,
        header_type=header,
        cookie_type=cookie,
        deprecated=deprecated,
    )

    return wrapper
