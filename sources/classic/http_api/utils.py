import inspect
import re

from falcon import HTTP_METHODS


__camel_case_re = re.compile(r'(?<!^)(?=[A-Z])')

__methods = '|'.join((f'({method.lower()})' for method in HTTP_METHODS))
__method_name_re = re.compile(r'^\bon_(' + __methods + ')_')


def camel_case_to_dash(text):
    return __camel_case_re.sub('_', text).lower()


def get_suffix(method_name):
    result, count = __method_name_re.subn('', method_name)
    if count > 0:
        return result


def get_suffixes(controller):
    members = inspect.getmembers(controller)
    for name, member in members:
        if not inspect.ismethod(member):
            continue

        suffix = get_suffix(name)
        if suffix:
            yield suffix
