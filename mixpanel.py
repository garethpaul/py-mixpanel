"""
Event tracking - basic for mixpanel
"""
TRACK_BASE_URL = "https://api.mixpanel.com/track/?data=%s"
ARCHIVE_BASE_URL = "https://api.mixpanel.com/import/?data=%s&api_key=%s"
REQUEST_TIMEOUT_SECONDS = 10
import urllib2
import urllib
import json
import base64
import time


def open_mixpanel_url(url):
  return urllib2.urlopen(url, timeout=REQUEST_TIMEOUT_SECONDS)


def validate_callback(callback):
  if callback is not None and not callable(callback):
    raise ValueError("Callback must be callable")


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
    if not isinstance(token, basestring) or not token.strip():
      raise ValueError("Must specify a token")

    token = token.strip()
    if api_key is not None:
      if not isinstance(api_key, basestring) or not api_key.strip():
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
    if not isinstance(event, basestring) or not event.strip():
      raise ValueError("Must specify an event")
    event = event.strip()
    validate_callback(callback)

    if properties is None:
      properties = {}
    elif not isinstance(properties, dict):
      raise ValueError("Properties must be a dict")
    else:
      properties = properties.copy()

    if (not properties.has_key("distinct_id") or
        not isinstance(properties["distinct_id"], basestring) or
        not properties["distinct_id"].strip()):
      raise ValueError("Must specify a distinct ID")
    properties["distinct_id"] = properties["distinct_id"].strip()

    if not properties.has_key("token"):
      properties['token'] = self.token
    if not properties.has_key("time"):
      properties['time'] = int(time.time())

    params = {"event": event, "properties": properties}
    data = urllib.quote(base64.b64encode(json.dumps(params)), safe='')
    if self.api_key:
      resp = open_mixpanel_url(ARCHIVE_BASE_URL % (data, urllib.quote(self.api_key, safe='')))
    else:
      resp = open_mixpanel_url(TRACK_BASE_URL % data)
    resp.read()

    if callback is not None:
      callback(event, properties)

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
    validate_callback(callback)

    from threading import Thread
    t = Thread(target=self.track, kwargs={
      'event': event, 
      'properties': properties, 
      'callback': callback
    })
    t.start()
    return t
