from falcon import testing
import pytest

from classic.http_api import App
from classic.error_handling import Error, ErrorsList
from pydantic import BaseModel


class SomeError(Error):
    message_template = 'Some error'
    code = 'app.some_error'


class SomeModel(BaseModel):
    prop: int


class Errors:

    def on_get_validation(self, request, response):
        SomeModel(prop=None)  # Raises ValidationError

    def on_get_app_error(self, request, response):
        raise SomeError()

    def on_get_errors_list(self, request, response):
        raise ErrorsList(
            SomeError(),
            SomeError(),
        )


@pytest.fixture(scope='module')
def app():
    app = App()
    app.register(Errors())
    return app


@pytest.fixture(scope='module')
def client(app):
    return testing.TestClient(app)


def test_validation_errors(client):
    result = client.simulate_get('/api/errors/validation')

    assert result.json == [{
        'type': 'type_error.none.not_allowed',
        'msg': 'none is not an allowed value',
        'loc': ['prop'],
    }]


def test_app_errors(client):
    result = client.simulate_get('/api/errors/app_error')

    assert result.json == [{
        'type': 'app.some_error',
        'msg': 'Some error',
        'ctx': {},
    }]


def test_list_errors(client):
    result = client.simulate_get('/api/errors/errors_list')

    assert result.json == [
        {
            'type': 'app.some_error',
            'msg': 'Some error',
            'ctx': {},
        }, {
            'type': 'app.some_error',
            'msg': 'Some error',
            'ctx': {},
        }
    ]
