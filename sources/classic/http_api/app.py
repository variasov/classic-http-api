import inspect

import falcon.media
from falcon import Request, Response

from classic.components import component
from classic.error_handling import Error, ErrorsList

from defspec import OpenAPI, RenderTemplate
import msgspec

from . import error_handlers


def is_method_with_spec(fn):
    return callable(fn) and hasattr(fn, '__specification__')


class OpenAPIResource:
    def __init__(self, openapi) -> None:
        self.openapi = openapi
        self.spec = None

    def on_get(self, req: Request, resp: Response):
        if not self.spec:
            self.spec = self.openapi.to_json()
        resp.content_type = falcon.MEDIA_JSON
        resp.data = self.spec


class OpenAPIRender:
    def __init__(self, spec_url: str, template: RenderTemplate) -> None:
        self.template = template.value.format(spec_url=spec_url)

    def on_get(self, req: Request, resp: Response):
        resp.content_type = falcon.MEDIA_HTML
        resp.text = self.template


@component(init=False)
class App(falcon.App):
    
    def __init__(
        self,
        openapi: bool = False,
        open_api_spec_url: str = '/openapi/spec.json',
        swagger_url: str = '/openapi/swagger',
        media_type=falcon.DEFAULT_MEDIA_TYPE,
        request_type=Request,
        response_type=Response,
        middleware=None,
        router=None,
        independent_middleware=True,
        cors_enable=False,
        sink_before_static_route=True,
    ):
        super().__init__(
            media_type,
            request_type,
            response_type,
            middleware,
            router,
            independent_middleware,
            cors_enable,
            sink_before_static_route,
        )

        if openapi:
            self.openapi = OpenAPI()
            self.add_route(open_api_spec_url, OpenAPIResource(self.openapi))
            self.add_route(swagger_url, OpenAPIRender(
                open_api_spec_url,
                RenderTemplate.SWAGGER,
            ))
        else:
            self.openapi = None

        self.req_options.auto_parse_qs_csv = True
        self.req_options.keep_blank_qs_values = False

        self.resp_options.media_handlers[
            falcon.MEDIA_JSON
        ] = falcon.media.JSONHandler(
            dumps=msgspec.json.encode,
        )

        self.add_error_handler(Error, error_handlers.app_error)
        self.add_error_handler(ErrorsList, error_handlers.app_errors_list)
        self.add_error_handler(
            msgspec.ValidationError,
            error_handlers.validation_error,
        )

    def add_route(self, uri_template, resource, **kwargs):
        if self.openapi:
            for name, handler in inspect.getmembers(
                resource, is_method_with_spec,
            ):
                self.openapi.register_route(
                    uri_template, name[3:], **handler.__specification__
                )
        return super().add_route(uri_template, resource, **kwargs)
