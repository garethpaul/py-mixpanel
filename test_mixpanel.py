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
        self.timeouts = []
        self.original_urlopen = mixpanel.urllib2.urlopen
        self.original_time = mixpanel.time.time
        mixpanel.urllib2.urlopen = self.urlopen
        mixpanel.time.time = lambda: 1234567890

    def tearDown(self):
        mixpanel.urllib2.urlopen = self.original_urlopen
        mixpanel.time.time = self.original_time

    def urlopen(self, url, timeout=None):
        self.urls.append(url)
        self.timeouts.append(timeout)
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
        self.assertEqual([mixpanel.REQUEST_TIMEOUT_SECONDS], self.timeouts)
        self.assertEqual([("Signed Up", payload["properties"])], callbacks)

    def test_track_requires_distinct_id_without_optimized_asserts(self):
        tracker = mixpanel.EventTracker("project-token")
        properties = {}

        with self.assertRaises(ValueError):
            tracker.track("Missing ID", properties)

        self.assertEqual([], self.urls)
        self.assertEqual({}, properties)

    def test_track_requires_nonblank_event_name(self):
        tracker = mixpanel.EventTracker("project-token")
        properties = {"distinct_id": "user-1"}

        for event in (None, "", " \t\n"):
            with self.assertRaises(ValueError):
                tracker.track(event, properties)

        self.assertEqual([], self.urls)
        self.assertEqual({"distinct_id": "user-1"}, properties)

    def test_tracker_requires_nonblank_token(self):
        for token in (None, "", " \t\n"):
            with self.assertRaises(ValueError):
                mixpanel.EventTracker(token)

        tracker = mixpanel.EventTracker(" project-token ")
        self.assertEqual("project-token", tracker.token)

    def test_track_does_not_mutate_caller_properties(self):
        tracker = mixpanel.EventTracker("project-token")
        properties = {"distinct_id": "user-5", "plan": "free"}

        tracker.track("No Mutation", properties)

        self.assertEqual({"distinct_id": "user-5", "plan": "free"}, properties)
        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual("https", parsed.scheme)
        self.assertIn("data", query)
        self.assertEqual("No Mutation", payload["event"])
        self.assertEqual("project-token", payload["properties"]["token"])
        self.assertEqual(1234567890, payload["properties"]["time"])
        self.assertEqual("free", payload["properties"]["plan"])

    def test_track_propagates_request_errors_without_callback(self):
        callbacks = []
        tracker = mixpanel.EventTracker("project-token")

        def failing_urlopen(url, timeout=None):
            self.urls.append(url)
            self.timeouts.append(timeout)
            raise mixpanel.urllib2.URLError("network unavailable")

        mixpanel.urllib2.urlopen = failing_urlopen

        with self.assertRaises(mixpanel.urllib2.URLError):
            tracker.track(
                "Request Failed",
                {"distinct_id": "user-4"},
                lambda event, properties: callbacks.append((event, properties)),
            )

        self.assertEqual(1, len(self.urls))
        self.assertEqual([mixpanel.REQUEST_TIMEOUT_SECONDS], self.timeouts)
        self.assertEqual([], callbacks)

    def test_import_posts_https_payload_with_api_key(self):
        tracker = mixpanel.EventTracker("project-token", api_key="api-secret")

        tracker.track("Imported", {"distinct_id": "user-2"})

        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual("https", parsed.scheme)
        self.assertEqual("/import/", parsed.path)
        self.assertEqual(["api-secret"], query["api_key"])
        self.assertEqual("Imported", payload["event"])
        self.assertEqual("project-token", payload["properties"]["token"])
        self.assertEqual([mixpanel.REQUEST_TIMEOUT_SECONDS], self.timeouts)

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
        self.assertEqual([mixpanel.REQUEST_TIMEOUT_SECONDS], self.timeouts)
        self.assertEqual([("Async Event", payload["properties"])], callbacks)


if __name__ == "__main__":
    unittest.main()
