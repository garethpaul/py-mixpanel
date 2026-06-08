import base64
import json
import threading
import unittest
import urlparse

import mixpanel


class FakeResponse(object):
    def read(self):
        return "1"


class FakeThread(object):
    created = []

    def __init__(self, target=None, kwargs=None):
        self.target = target
        self.kwargs = kwargs or {}
        self.started = False
        FakeThread.created.append(self)

    def start(self):
        self.started = True
        self.target(**self.kwargs)


class EventTrackerTest(unittest.TestCase):
    def setUp(self):
        self.urls = []
        self.original_urlopen = mixpanel.urllib2.urlopen
        self.original_time = mixpanel.time.time
        mixpanel.urllib2.urlopen = self.urlopen
        mixpanel.time.time = lambda: 1234567890

    def tearDown(self):
        mixpanel.urllib2.urlopen = self.original_urlopen
        mixpanel.time.time = self.original_time

    def urlopen(self, url):
        self.urls.append(url)
        return FakeResponse()

    def payload_from_url(self, url):
        parsed = urlparse.urlparse(url)
        query = urlparse.parse_qs(parsed.query)
        payload = json.loads(base64.b64decode(query["data"][0]))
        return parsed, query, payload

    def test_track_posts_https_payload(self):
        callbacks = []
        tracker = mixpanel.EventTracker("project-token")

        def callback(event, properties):
            callbacks.append((event, properties.copy()))

        tracker.track("Signed Up", {"distinct_id": "user-1"}, callback)

        self.assertEqual(1, len(self.urls))
        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual("https", parsed.scheme)
        self.assertEqual("api.mixpanel.com", parsed.netloc)
        self.assertEqual("/track/", parsed.path)
        self.assertIn("data", query)
        self.assertEqual("Signed Up", payload["event"])
        self.assertEqual("project-token", payload["properties"]["token"])
        self.assertEqual("user-1", payload["properties"]["distinct_id"])
        self.assertEqual(1234567890, payload["properties"]["time"])
        self.assertEqual([("Signed Up", payload["properties"])], callbacks)

    def test_import_posts_https_payload_with_api_key(self):
        tracker = mixpanel.EventTracker("project-token", api_key="api-secret")

        tracker.track("Imported", {"distinct_id": "user-2"})

        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual("https", parsed.scheme)
        self.assertEqual("/import/", parsed.path)
        self.assertEqual(["api-secret"], query["api_key"])
        self.assertEqual("Imported", payload["event"])
        self.assertEqual("project-token", payload["properties"]["token"])

    def test_track_async_posts_payload_and_runs_callback(self):
        callbacks = []
        tracker = mixpanel.EventTracker("project-token")
        original_thread = threading.Thread
        FakeThread.created = []
        threading.Thread = FakeThread

        def callback(event, properties):
            callbacks.append((event, properties.copy()))

        try:
            thread = tracker.track_async("Async Event", {"distinct_id": "user-3"}, callback)
        finally:
            threading.Thread = original_thread

        self.assertEqual(1, len(FakeThread.created))
        self.assertEqual(FakeThread.created[0], thread)
        self.assertTrue(thread.started)
        self.assertEqual(1, len(self.urls))

        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual("https", parsed.scheme)
        self.assertEqual("/track/", parsed.path)
        self.assertIn("data", query)
        self.assertEqual("Async Event", payload["event"])
        self.assertEqual("project-token", payload["properties"]["token"])
        self.assertEqual("user-3", payload["properties"]["distinct_id"])
        self.assertEqual([("Async Event", payload["properties"])], callbacks)


if __name__ == "__main__":
    unittest.main()
