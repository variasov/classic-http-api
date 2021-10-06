from falcon import status_codes


def validation_error(request, response, error, params):
    response.status = status_codes.HTTP_400
    response.media = error.errors()


def app_error(request, response, error, params):
    response.status = status_codes.HTTP_400
    response.media = [{'type': error.code,
                       'msg': error.message,
                       'ctx': error.context}]


def app_errors_list(request, response, error, params):
    response.status = status_codes.HTTP_400
    response.media = [
        {'type': e.code,
         'msg': e.message,
         'ctx': e.context}
        for e in error.errors
    ]
