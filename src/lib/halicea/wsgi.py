import cgi
import logging
import re
import StringIO
import sys
import traceback
import urlparse
import webob
import wsgiref.handlers
import wsgiref.headers
import wsgiref.util
from lib.halicea.helpers import ClassImport
from lib.halicea.HalRequestHandler import HalRequestHandler as halHandler

RE_FIND_GROUPS = re.compile('\(.*?\)')
_CHARSET_RE = re.compile(r';\s*charset=([^;\s]*)', re.I)

class Request(webob.Request):
  """Abstraction for an HTTP request.

  Properties:
    uri: the complete URI requested by the user
    scheme: 'http' or 'https'
    host: the host, including the port
    path: the path up to the ';' or '?' in the URL
    parameters: the part of the URL between the ';' and the '?', if any
    query: the part of the URL after the '?'

  You can access parsed query and POST values with the get() method; do not
  parse the query string yourself.
  """

  request_body_tempfile_limit = 0

  uri = property(lambda self: self.url)
  query = property(lambda self: self.query_string)

  def __init__(self, environ):
    """Constructs a Request object from a WSGI environment.

    If the charset isn't specified in the Content-Type header, defaults
    to UTF-8.

    Args:
      environ: A WSGI-compliant environment dictionary.
    """
    match = _CHARSET_RE.search(environ.get('CONTENT_TYPE', ''))
    if match:
      charset = match.group(1).lower()
    else:
      charset = 'utf-8'

    webob.Request.__init__(self, environ, charset=charset,
                           unicode_errors= 'ignore', decode_param_names=True)

  def get(self, argument_name, default_value='', allow_multiple=False):
    """Returns the query or POST argument with the given name.

    We parse the query string and POST payload lazily, so this will be a
    slower operation on the first call.

    Args:
      argument_name: the name of the query or POST argument
      default_value: the value to return if the given argument is not present
      allow_multiple: return a list of values with the given name (deprecated)

    Returns:
      If allow_multiple is False (which it is by default), we return the first
      value with the given name given in the request. If it is True, we always
      return a list.
    """
    param_value = self.get_all(argument_name)
    if allow_multiple:
      logging.warning('allow_multiple is a deprecated param, please use the '
                      'Request.get_all() method instead.')
    if len(param_value) > 0:
      if allow_multiple:
        return param_value
      return param_value[0]
    else:
      if allow_multiple and not default_value:
        return []
      return default_value

  def get_all(self, argument_name, default_value=None):
    """Returns a list of query or POST arguments with the given name.

    We parse the query string and POST payload lazily, so this will be a
    slower operation on the first call.

    Args:
      argument_name: the name of the query or POST argument
      default_value: the value to return if the given argument is not present,
        None may not be used as a default, if it is then an empty list will be
        returned instead.

    Returns:
      A (possibly empty) list of values.
    """
    if self.charset:
      argument_name = argument_name.encode(self.charset)

    if default_value is None:
      default_value = []

    param_value = self.params.getall(argument_name)

    if param_value is None or len(param_value) == 0:
      return default_value

    for i in xrange(len(param_value)):
      if isinstance(param_value[i], cgi.FieldStorage):
        param_value[i] = param_value[i].value

    return param_value

  def arguments(self):
    """Returns a list of the arguments provided in the query and/or POST.

    The return value is a list of strings.
    """
    return list(set(self.params.keys()))

  def get_range(self, name, min_value=None, max_value=None, default=0):
    """Parses the given int argument, limiting it to the given range.

    Args:
      name: the name of the argument
      min_value: the minimum int value of the argument (if any)
      max_value: the maximum int value of the argument (if any)
      default: the default value of the argument if it is not given

    Returns:
      An int within the given range for the argument
    """
    value = self.get(name, default)
    if value is None:
      return value
    try:
      value = int(value)
    except ValueError:
      value = default
    if value is not None:
      if max_value is not None:
        value = min(value, max_value)
      if min_value is not None:
        value = max(value, min_value)
    return value


class Response(object):
  """Abstraction for an HTTP response.

  Properties:
    out: file pointer for the output stream
    headers: wsgiref.headers.Headers instance representing the output headers
  """
  def __init__(self):
    """Constructs a response with the default settings."""


    self.out = StringIO.StringIO()
    self.__wsgi_headers = []
    self.headers = wsgiref.headers.Headers(self.__wsgi_headers)
    self.headers['Content-Type'] = 'text/html; charset=utf-8'
    self.headers['Cache-Control'] = 'no-cache'

    self.set_status(200)

  @property
  def status(self):
    """Returns current request status code."""
    return self.__status[0]

  @property
  def status_message(self):
    """Returns current request status message."""
    return self.__status[1]

  def set_status(self, code, message=None):
    """Sets the HTTP status code of this response.

    Args:
      message: the HTTP status string to use

    If no status string is given, we use the default from the HTTP/1.1
    specification.
    """
    if not message:
      message = Response.http_status_message(code)
    self.__status = (code, message)

  def has_error(self):
    """Indicates whether the response was an error response."""
    return self.__status[0] >= 400

  def clear(self):
    """Clears all data written to the output stream so that it is empty."""
    self.out.seek(0)
    self.out.truncate(0)

  def wsgi_write(self, start_response):
    """Writes this response using WSGI semantics with the given WSGI function.

    Args:
      start_response: the WSGI-compatible start_response function
    """
    body = self.out.getvalue()
    if isinstance(body, unicode):


      body = body.encode('utf-8')
    elif self.headers.get('Content-Type', '').endswith('; charset=utf-8'):


      try:


        body.decode('utf-8')
      except UnicodeError, e:
        logging.warning('Response written is not UTF-8: %s', e)

    if (self.headers.get('Cache-Control') == 'no-cache' and
        not self.headers.get('Expires')):
      self.headers['Expires'] = 'Fri, 01 Jan 1990 00:00:00 GMT'
    self.headers['Content-Length'] = str(len(body))


    new_headers = []
    for header, value in self.__wsgi_headers:
      if not isinstance(value, basestring):
        value = unicode(value)
      if ('\n' in header or '\r' in header or
          '\n' in value or '\r' in value):
        logging.warning('Replacing newline in header: %s', repr((header,value)))
        value = value.replace('\n','').replace('\r','')
        header = header.replace('\n','').replace('\r','')
      new_headers.append((header, value))
    self.__wsgi_headers = new_headers

    write = start_response('%d %s' % self.__status, self.__wsgi_headers)
    write(body)
    self.out.close()

  def http_status_message(code):
    """Returns the default HTTP status message for the given code.

    Args:
      code: the HTTP code for which we want a message
    """
    if not Response.__HTTP_STATUS_MESSAGES.has_key(code):
      raise Error('Invalid HTTP status code: %d' % code)
    return Response.__HTTP_STATUS_MESSAGES[code]
  http_status_message = staticmethod(http_status_message)

  __HTTP_STATUS_MESSAGES = {
    100: 'Continue',
    101: 'Switching Protocols',
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non-Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Moved Temporarily',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    306: 'Unused',
    307: 'Temporary Redirect',
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Time-out',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request-URI Too Large',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Time-out',
    505: 'HTTP Version not supported'
  }


class WSGIApplication(object):
  """Wraps a set of webapp RequestHandlers in a WSGI-compatible application.

  To use this class, pass a list of (URI regular expression, RequestHandler)
  pairs to the constructor, and pass the class instance to a WSGI handler.
  See the example in the module comments for details.

  The URL mapping is first-match based on the list ordering.
  """
  REQUEST_CLASS = Request
  RESPONSE_CLASS = Response

  def __init__(self, mapDict, debug=False):
    self.mapDict = mapDict
    """Initializes this application with the given URL mapping.

    Args:
      url_mapping: list of (URI regular expression, RequestHandler) pairs
                   (e.g., [('/', ReqHan)])
      debug: if true, we send Python stack traces to the browser on errors
    """
    self.__debug = debug

    WSGIApplication.active_instance = self
    self.current_request_args = ()

  def __call__(self, environ, start_response):
    """Called by WSGI when a request comes in."""
    request = self.REQUEST_CLASS(environ)
    response = self.RESPONSE_CLASS()
    WSGIApplication.active_instance = self
    
    url, match = environ['wsgiorg.routing_args'] 
    route = environ['routes.route']
    url = environ['routes.url']
    if match:
      try:
        groups = dict([(x,match[x]) for x in match if x not in ['controller', 'action']])
        handler_cls = ClassImport(self.mapDict[match['controller']])
        handler_cls = handler_cls.new_factory(op=match['action'])
        handler = handler_cls()
        handler.initialize(request, response)
      except Exception, ex:
        handler = halHandler()
        handler.initialize(request, response)
        handler.handle_exception(ex, self.__debug)
      finally:
        try:
          method = environ['REQUEST_METHOD']
          if method == 'GET':
            handler.get(*groups)
          elif method == 'POST':
            handler.post(*groups)
          elif method == 'HEAD':
            handler.head(*groups)
          elif method == 'OPTIONS':
            handler.options(*groups)
          elif method == 'PUT':
            handler.put(*groups)
          elif method == 'DELETE':
            handler.delete(*groups)
          elif method == 'TRACE':
            handler.trace(*groups)
          else:
            handler.error(501)
        except Exception, e:
          handler.handle_exception(e, self.__debug)
    else:
      response.set_status(404)
    
    response.wsgi_write(start_response)
    return ['']