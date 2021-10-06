import falcon.media

from classic.components import component
from classic.app.errors import AppError, ErrorsList

from pydantic import ValidationError

from . import error_handlers, utils


@component(init=False)
class App(falcon.App):
    
    def __init__(self, *args, prefix='/api', **kwargs):
        super().__init__(*args, **kwargs)

        self.prefix = prefix
    
        self.req_options.auto_parse_qs_csv = True

        self.add_error_handler(AppError, error_handlers.app_error)
        self.add_error_handler(ErrorsList, error_handlers.app_errors_list)
        self.add_error_handler(ValidationError, error_handlers.validation_error)

    @property
    def url_prefix(self) -> str:
        return self.prefix or ''

    def register(self, controller, url=None):
        if url is None:
            url = '/' + utils.camel_case_to_dash(
                controller.__class__.__name__
            )

        for suffix in utils.get_suffixes(controller):
            self.add_method(
                f'{url}/{suffix}',
                controller, suffix=suffix
            )

    def add_method(self, url, controller, suffix=None):
        self.add_route(
            f'{self.url_prefix}{url}',
            controller, suffix=suffix
        )
