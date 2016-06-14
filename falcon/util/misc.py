# Copyright 2013 by Rackspace Hosting, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import functools
import inspect
import warnings

import six
if False:
    from typing import Any, Callable

__all__ = (
    'deprecated',
    'http_now',
    'dt_to_http',
    'http_date_to_dt',
    'to_query_str',
    'get_bound_method',
)


# PERF(kgriffs): Avoid superfluous namespace lookups
strptime = datetime.datetime.strptime
utcnow = datetime.datetime.utcnow


# NOTE(kgriffs): We don't want our deprecations to be ignored by default,
# so create our own type.
#
# TODO(kgriffs): Revisit this decision if users complain.
class DeprecatedWarning(UserWarning):
    pass


def deprecated(instructions):
    # type: (str) -> Callable
    """Flags a method as deprecated.

    This function returns a decorator which can be used to mark deprecated
    functions. Applying this decorator will result in a warning being
    emitted when the function is used.

    Args:
        instructions (str): Specific guidance for the developer, e.g.:
            'Please migrate to add_proxy(...)''
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            message = 'Call to deprecated function {0}(...). {1}'.format(
                func.__name__,
                instructions)

            frame = inspect.currentframe().f_back

            warnings.warn_explicit(message,
                                   category=DeprecatedWarning,
                                   filename=inspect.getfile(frame.f_code),
                                   lineno=frame.f_lineno)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def http_now():
    # type: () -> str
    """Returns the current UTC time as an IMF-fixdate.

    Returns:
        str: The current UTC time as an IMF-fixdate,
            e.g., 'Tue, 15 Nov 1994 12:45:26 GMT'.
    """

    return dt_to_http(utcnow())


def dt_to_http(dt):
    # type: (datetime.datetime) -> str
    """Converts a ``datetime`` instance to an HTTP date string.

    Args:
        dt (datetime): A ``datetime`` instance to convert, assumed to be UTC.

    Returns:
        str: An RFC 1123 date string, e.g.: "Tue, 15 Nov 1994 12:45:26 GMT".

    """

    # Tue, 15 Nov 1994 12:45:26 GMT
    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')


def http_date_to_dt(http_date, obs_date=False):
    # type: (str, bool) -> datetime.datetime
    """Converts an HTTP date string to a datetime instance.

    Args:
        http_date (str): An RFC 1123 date string, e.g.:
            "Tue, 15 Nov 1994 12:45:26 GMT".
        obs_date (bool, optional): Support obs-date formats according to
            RFC 7231, e.g.:
            "Sunday, 06-Nov-94 08:49:37 GMT" (default ``False``).

    Returns:
        datetime: A UTC datetime instance corresponding to the given
            HTTP date.

    Raises:
        ValueError: http_date doesn't match any of the available time formats
    """

    if not obs_date:
        # PERF(kgriffs): This violates DRY, but we do it anyway
        #   to avoid the overhead of setting up a tuple, looping
        #   over it, and setting up exception handling blocks each
        #   time around the loop, in the case that we don't actually
        #   need to check for multiple formats.
        return strptime(http_date, '%a, %d %b %Y %H:%M:%S %Z')

    time_formats = (
        '%a, %d %b %Y %H:%M:%S %Z',
        '%a, %d-%b-%Y %H:%M:%S %Z',
        '%A, %d-%b-%y %H:%M:%S %Z',
        '%a %b %d %H:%M:%S %Y',
    )

    # Loop through the formats and return the first that matches
    for time_format in time_formats:
        try:
            return strptime(http_date, time_format)
        except ValueError:
            continue

    # Did not match any formats
    raise ValueError('time data %r does not match known formats' % http_date)


def to_query_str(params):
    # type: (dict) -> str
    """Converts a dictionary of params to a query string.

    Args:
        params (dict): A dictionary of parameters, where each key is a
            parameter name, and each value is either a ``str`` or
            something that can be converted into a ``str``. If `params`
            is a ``list``, it will be converted to a comma-delimited string
            of values (e.g., 'thing=1,2,3')

    Returns:
        str: A URI query string including the '?' prefix, or an empty string
            if no params are given (the ``dict`` is empty).
    """

    if not params:
        return ''

    # PERF: This is faster than a list comprehension and join, mainly
    # because it allows us to inline the value transform.
    query_str = '?'
    for k, v in params.items():
        if v is True:
            v = 'true'
        elif v is False:
            v = 'false'
        elif isinstance(v, list):
            v = ','.join(map(str, v))
        else:
            v = str(v)

        query_str += k + '=' + v + '&'

    return query_str[:-1]


def get_bound_method(obj, method_name):
    # type: (Any, str) -> Callable
    """Get a bound method of the given object by name.

    Args:
        obj: Object on which to look up the method.
        method_name: Name of the method to retrieve.

    Returns:
        Bound method, or ``None`` if the method does not exist on
        the object.

    Raises:
        AttributeError: The method exists, but it isn't
            bound (most likely a class was passed, rather than
            an instance of that class).

    """

    method = getattr(obj, method_name, None)
    if method is not None:
        # NOTE(kgriffs): Ensure it is a bound method
        if six.get_method_self(method) is None:
            # NOTE(kgriffs): In Python 3 this code is unreachable
            # because the above will raise AttributeError on its
            # own.
            msg = '{0} must be a bound method'.format(method)
            raise AttributeError(msg)

    return method
