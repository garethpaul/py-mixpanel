"""
Event tracking - basic for mixpanel
"""
TRACK_BASE_URL = "https://api.mixpanel.com/track/"
ARCHIVE_BASE_URL = "https://api.mixpanel.com/import/?data=%s&api_key=%s"
REQUEST_TIMEOUT_SECONDS = 10
MAX_RESPONSE_BODY_BYTES = 1024
try:
  import urllib2
except ImportError:
  from urllib import error as urllib_error
  from urllib import request as urllib2
  urllib2.URLError = urllib_error.URLError

try:
  from urllib import quote
except ImportError:
  from urllib.parse import quote

import json
import base64
import time
import threading

try:
  basestring
except NameError:
  basestring = str

try:
  unicode
except NameError:
  unicode = str

TEXT_TYPES = (basestring,)
RESPONSE_TYPES = (basestring, bytes)

try:
  long
except NameError:
  long = int


class MixpanelError(Exception):
  pass


def open_mixpanel_url(url):
  return urllib2.urlopen(url, timeout=REQUEST_TIMEOUT_SECONDS)


def validate_callback(callback):
  if callback is not None and not callable(callback):
    raise ValueError("Callback must be callable")


def validate_event(event):
  if not isinstance(event, TEXT_TYPES) or not event.strip():
    raise ValueError("Must specify an event")
  return event.strip()


def snapshot_json_value(value, active=None):
  if active is None:
    active = set()

  if value is None or isinstance(value, (bool, int, long, float) + TEXT_TYPES):
    return value

  identity = id(value)
  if identity in active:
    raise ValueError("Circular reference detected")

  if isinstance(value, dict):
    active.add(identity)
    try:
      snapshot = {}
      for key, item in dict.items(value):
        snapshot[key] = snapshot_json_value(item, active)
      return snapshot
    finally:
      active.remove(identity)

  if isinstance(value, list):
    active.add(identity)
    try:
      return [
        snapshot_json_value(list.__getitem__(value, index), active)
        for index in range(list.__len__(value))
      ]
    finally:
      active.remove(identity)

  if isinstance(value, tuple):
    active.add(identity)
    try:
      return tuple(
        snapshot_json_value(tuple.__getitem__(value, index), active)
        for index in range(tuple.__len__(value))
      )
    finally:
      active.remove(identity)

  raise TypeError("Mixpanel properties must contain JSON values")


def prepare_properties(properties):
  if properties is None:
    properties = {}
  elif not isinstance(properties, dict):
    raise ValueError("Properties must be a dict")
  else:
    properties = snapshot_json_value(properties)

  if ("distinct_id" not in properties or
      not isinstance(properties["distinct_id"], TEXT_TYPES) or
      not properties["distinct_id"].strip()):
    raise ValueError("Must specify a distinct ID")
  properties["distinct_id"] = properties["distinct_id"].strip()
  return properties


def validate_json_properties(event, properties):
  json.dumps({"event": event, "properties": properties}, allow_nan=False)


def validate_mixpanel_response(response_body):
  if isinstance(response_body, bytes) and not isinstance(response_body, unicode):
    try:
      response_body = response_body.decode("ascii")
    except UnicodeDecodeError:
      raise MixpanelError("Mixpanel rejected the event")
  if not isinstance(response_body, TEXT_TYPES) or response_body.strip() != "1":
    raise MixpanelError("Mixpanel rejected the event")


def read_mixpanel_response(resp):
  response_body = resp.read(MAX_RESPONSE_BODY_BYTES + 1)
  if (isinstance(response_body, RESPONSE_TYPES) and
      len(response_body) > MAX_RESPONSE_BODY_BYTES):
    raise MixpanelError("Mixpanel response exceeds 1024 bytes")
  return response_body


def encode_payload(params):
  serialized = json.dumps(params, allow_nan=False)
  if not isinstance(serialized, bytes):
    serialized = serialized.encode("utf-8")
  return quote(base64.b64encode(serialized), safe='')


def build_track_request(params):
  body = ("data=" + encode_payload(params)).encode("ascii")
  request = urllib2.Request(TRACK_BASE_URL, data=body)
  request.add_header("Content-Type", "application/x-www-form-urlencoded")
  request.add_header("Content-Length", str(len(body)))
  return request


def request_mixpanel(url):
  try:
    resp = open_mixpanel_url(url)
  except Exception:
    resp = None
  if resp is None:
    raise MixpanelError("Mixpanel request failed")

  failure = None
  response_body = None
  try:
    status = resp.getcode()
    if status is not None and (status < 200 or status >= 300):
      raise MixpanelError("Mixpanel request failed")
    response_body = read_mixpanel_response(resp)
    validate_mixpanel_response(response_body)
  except MixpanelError as error:
    failure = error
  except Exception:
    failure = MixpanelError("Mixpanel request failed")

  try:
    resp.close()
  except Exception:
    if failure is None:
      failure = MixpanelError("Mixpanel request failed")

  if failure is not None:
    raise failure

  return response_body


class EventTracker(object):
  """Simple Event Tracker
  Designed to be generic, but currently uses Mixpanel
  to actually handle the tracking of the events
  """
  def __init__(self, token, api_key=None):
    """Create a new event tracker
    :param token: The auth token to use to validate each request
    :type token: str
    """
    if not isinstance(token, TEXT_TYPES) or not token.strip():
      raise ValueError("Must specify a token")

    token = token.strip()
    if api_key is not None:
      if not isinstance(api_key, TEXT_TYPES) or not api_key.strip():
        raise ValueError("Must specify an API key")
      api_key = api_key.strip()

    self.token = token
    self.api_key = api_key

  def track(self, event, properties=None, callback=None):
    """Track a single event
    :param event: The name of the event to track
    :type event: str
    :param properties: An optional dict of properties to describe the event
    :type properties: dict
    :param callback: An optional callback to execute when
      the event has been tracked.
      The callback function should accept two arguments, the event
      and properties, just as they are provided to this function 
      This is mostly used for handling Async operations
    :type callback: function
    """
    event = validate_event(event)
    validate_callback(callback)
    properties = prepare_properties(properties)
    validate_json_properties(event, properties)
    self._track_prepared(event, properties, callback, self.token, self.api_key)

  def _track_prepared(self, event, properties, callback, token, api_key):
    callback_properties = snapshot_json_value(properties)
    request_properties = snapshot_json_value(properties)

    request_properties['token'] = token
    if "time" not in request_properties:
      request_properties['time'] = int(time.time())

    params = {"event": event, "properties": request_properties}
    if api_key:
      data = encode_payload(params)
      url = ARCHIVE_BASE_URL % (data, quote(api_key, safe=''))
    else:
      url = build_track_request(params)
    request_mixpanel(url)

    if callback is not None:
      callback(event, callback_properties)

  def track_async(self, event, properties=None, callback=None):
    """Track an event asyncrhonously, essentially this runs the track
    event in a new thread
    :param event: The name of the event to track
    :type event: str
    :param properties: An optional dict of properties to describe the event
    :type properties: dict
    :param callback: An optional callback to execute when the event has been
      tracked. The callback function should accept two arguments, the event
      and properties, just as they are provided to this function
    :type callback: function

    :return: Thread object that will process this request
    :rtype: :class:`threading.Thread`
    """
    event = validate_event(event)
    validate_callback(callback)
    properties = prepare_properties(properties)
    validate_json_properties(event, properties)
    token = self.token
    api_key = self.api_key

    t = threading.Thread(target=self._track_prepared, kwargs={
      'event': event, 
      'properties': properties, 
      'callback': callback,
      'token': token,
      'api_key': api_key,
    })
    t.daemon = True
    t.start()
    return t
