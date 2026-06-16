import base64
import json
import sys
import threading
import unittest
import urlparse

sys.dont_write_bytecode = True

import mixpanel


class FakeResponse(object):
    def __init__(self, response_body="1", read_error=None):
        self.response_body = response_body
        self.read_error = read_error
        self.closed = False
        self.read_sizes = []

    def read(self, size=None):
        self.read_sizes.append(size)
        if self.read_error is not None:
            raise self.read_error
        if size is not None and isinstance(self.response_body, basestring):
            return self.response_body[:size]
        return self.response_body

    def close(self):
        self.closed = True


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


class DeferredThread(object):
    created = []

    def __init__(self, target=None, kwargs=None):
        self.target = target
        self.kwargs = kwargs or {}
        self.started = False
        self.__class__.created.append(self)

    def start(self):
        self.started = True

    def run(self):
        self.target(**self.kwargs)


class UncopyableValue(object):
    def __deepcopy__(self, memo):
        raise RuntimeError("nested copy failed")


class EventTrackerTest(unittest.TestCase):
    def setUp(self):
        self.urls = []
        self.timeouts = []
        self.responses = []
        self.response_body = "1"
        self.response_read_error = None
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
        response = FakeResponse(self.response_body, self.response_read_error)
        self.responses.append(response)
        return response

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
        self.assertEqual([
            ("Signed Up", {"distinct_id": "user-1"}),
        ], callbacks)
        self.assertTrue(self.responses[0].closed)
        self.assertEqual(
            [mixpanel.MAX_RESPONSE_BODY_BYTES + 1],
            self.responses[0].read_sizes,
        )

    def test_track_closes_response_when_read_fails(self):
        callbacks = []
        self.response_read_error = IOError("response read failed")
        tracker = mixpanel.EventTracker("project-token")

        with self.assertRaises(IOError):
            tracker.track(
                "Signed Up",
                {"distinct_id": "user-1"},
                lambda event, properties: callbacks.append((event, properties)),
            )

        self.assertEqual([], callbacks)
        self.assertEqual(1, len(self.responses))
        self.assertTrue(self.responses[0].closed)

    def test_track_accepts_stripped_success_acknowledgement(self):
        callbacks = []
        self.response_body = "  1\n"
        tracker = mixpanel.EventTracker("project-token")

        tracker.track(
            "Signed Up",
            {"distinct_id": "user-1"},
            lambda event, properties: callbacks.append((event, properties)),
        )

        self.assertEqual(1, len(callbacks))
        self.assertTrue(self.responses[0].closed)

    def test_track_rejects_failed_or_unexpected_acknowledgements(self):
        callbacks = []
        tracker = mixpanel.EventTracker("project-token")

        for response_body in ("0", "", " \t\n", "unexpected", None):
            self.response_body = response_body
            with self.assertRaisesRegexp(mixpanel.MixpanelError, "Mixpanel rejected the event"):
                tracker.track(
                    "Signed Up",
                    {"distinct_id": "user-1"},
                    lambda event, properties: callbacks.append((event, properties)),
                )

        self.assertEqual([], callbacks)
        self.assertEqual(5, len(self.responses))
        self.assertTrue(all(response.closed for response in self.responses))

    def test_track_rejects_oversized_response_before_callback(self):
        callbacks = []
        private_marker = "private-upstream-response"
        self.response_body = (
            "1" + ("x" * mixpanel.MAX_RESPONSE_BODY_BYTES) + private_marker
        )
        tracker = mixpanel.EventTracker("project-token")

        with self.assertRaisesRegexp(
                mixpanel.MixpanelError,
                "Mixpanel response exceeds 1024 bytes") as raised:
            tracker.track(
                "Signed Up",
                {"distinct_id": "user-1"},
                lambda event, properties: callbacks.append((event, properties)),
            )

        self.assertNotIn(private_marker, str(raised.exception))
        self.assertEqual([], callbacks)
        self.assertEqual(1, len(self.responses))
        self.assertTrue(self.responses[0].closed)
        self.assertEqual(
            [mixpanel.MAX_RESPONSE_BODY_BYTES + 1],
            self.responses[0].read_sizes,
        )

    def test_track_requires_distinct_id_without_optimized_asserts(self):
        tracker = mixpanel.EventTracker("project-token")
        properties = {}

        with self.assertRaises(ValueError):
            tracker.track("Missing ID", properties)

        self.assertEqual([], self.urls)
        self.assertEqual({}, properties)

    def test_track_requires_nonblank_string_distinct_id(self):
        tracker = mixpanel.EventTracker("project-token")

        for distinct_id in (None, "", " \t\n", 123):
            with self.assertRaises(ValueError):
                tracker.track("Missing ID", {"distinct_id": distinct_id})

        self.assertEqual([], self.urls)

    def test_track_rejects_non_finite_properties_before_request(self):
        tracker = mixpanel.EventTracker("project-token")
        callbacks = []

        for value in (float("nan"), float("inf"), float("-inf")):
            properties = {"distinct_id": "user-1", "measurement": value}
            with self.assertRaises(ValueError):
                tracker.track(
                    "Invalid Measurement",
                    properties,
                    lambda event, values: callbacks.append((event, values)),
                )
            self.assertIs(properties["measurement"], value)

        self.assertEqual([], self.urls)
        self.assertEqual([], callbacks)

    def test_track_requires_properties_dict(self):
        tracker = mixpanel.EventTracker("project-token")

        for properties in ("distinct_id=user-1", [("distinct_id", "user-1")], 123):
            with self.assertRaises(ValueError):
                tracker.track("Bad Properties", properties)

        self.assertEqual([], self.urls)

    def test_track_requires_nonblank_event_name(self):
        tracker = mixpanel.EventTracker("project-token")
        properties = {"distinct_id": "user-1"}

        for event in (None, "", " \t\n"):
            with self.assertRaises(ValueError):
                tracker.track(event, properties)

        self.assertEqual([], self.urls)
        self.assertEqual({"distinct_id": "user-1"}, properties)

    def test_track_requires_callable_callback_before_request(self):
        tracker = mixpanel.EventTracker("project-token")
        properties = {"distinct_id": "user-1"}

        with self.assertRaises(ValueError):
            tracker.track("Bad Callback", properties, callback="not-callable")

        self.assertEqual([], self.urls)
        self.assertEqual({"distinct_id": "user-1"}, properties)

    def test_track_trims_event_name(self):
        callbacks = []
        tracker = mixpanel.EventTracker("project-token")

        tracker.track(
            " Signed Up ",
            {"distinct_id": "user-1"},
            lambda event, properties: callbacks.append((event, properties.copy())),
        )

        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual("https", parsed.scheme)
        self.assertIn("data", query)
        self.assertEqual("Signed Up", payload["event"])
        self.assertEqual([
            ("Signed Up", {"distinct_id": "user-1"}),
        ], callbacks)

    def test_tracker_requires_nonblank_token(self):
        for token in (None, "", " \t\n"):
            with self.assertRaises(ValueError):
                mixpanel.EventTracker(token)

        tracker = mixpanel.EventTracker(" project-token ")
        self.assertEqual("project-token", tracker.token)

    def test_tracker_requires_nonblank_api_key_when_provided(self):
        for api_key in ("", " \t\n", 123):
            with self.assertRaises(ValueError):
                mixpanel.EventTracker("project-token", api_key=api_key)

        tracker = mixpanel.EventTracker("project-token", api_key=" api-secret ")
        self.assertEqual("api-secret", tracker.api_key)

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

    def test_track_uses_configured_token_over_caller_property(self):
        callbacks = []
        tracker = mixpanel.EventTracker("project-token")
        properties = {
            "distinct_id": "user-6",
            "token": "caller-token",
            "time": 987654321,
        }

        tracker.track(
            "Token Authority",
            properties,
            lambda event, values: callbacks.append((event, values.copy())),
        )

        self.assertEqual({
            "distinct_id": "user-6",
            "token": "caller-token",
            "time": 987654321,
        }, properties)
        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual("project-token", payload["properties"]["token"])
        self.assertEqual(987654321, payload["properties"]["time"])
        self.assertEqual([("Token Authority", properties)], callbacks)

    def test_track_callback_excludes_configured_token_and_generated_time(self):
        callbacks = []
        tracker = mixpanel.EventTracker("project-token")

        tracker.track(
            "Credential Isolation",
            {"distinct_id": "user-8", "plan": "paid"},
            lambda event, values: callbacks.append((event, values.copy())),
        )

        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual("project-token", payload["properties"]["token"])
        self.assertEqual(1234567890, payload["properties"]["time"])
        self.assertEqual([
            ("Credential Isolation", {
                "distinct_id": "user-8",
                "plan": "paid",
            }),
        ], callbacks)
        self.assertNotIn("token", callbacks[0][1])
        self.assertNotIn("time", callbacks[0][1])

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
        self.assertEqual([
            ("Async Event", {"distinct_id": "user-3"}),
        ], callbacks)

    def test_track_async_callback_excludes_configured_token_and_generated_time(self):
        callbacks = []
        tracker = mixpanel.EventTracker("project-token")
        original_thread = threading.Thread
        FakeThread.created = []
        threading.Thread = FakeThread

        try:
            tracker.track_async(
                "Async Credential Isolation",
                {"distinct_id": "user-9", "plan": "paid"},
                lambda event, values: callbacks.append((event, values.copy())),
            )
        finally:
            threading.Thread = original_thread

        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual("project-token", payload["properties"]["token"])
        self.assertEqual(1234567890, payload["properties"]["time"])
        self.assertEqual([
            ("Async Credential Isolation", {
                "distinct_id": "user-9",
                "plan": "paid",
            }),
        ], callbacks)
        self.assertNotIn("token", callbacks[0][1])
        self.assertNotIn("time", callbacks[0][1])

    def test_track_async_uses_configured_token_over_caller_property(self):
        tracker = mixpanel.EventTracker("project-token")
        properties = {"distinct_id": "user-7", "token": "caller-token"}
        original_thread = threading.Thread
        FakeThread.created = []
        threading.Thread = FakeThread

        try:
            tracker.track_async("Async Token Authority", properties)
        finally:
            threading.Thread = original_thread

        self.assertEqual({
            "distinct_id": "user-7",
            "token": "caller-token",
        }, properties)
        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual("project-token", payload["properties"]["token"])

    def test_track_async_snapshots_nested_properties_before_worker(self):
        callbacks = []
        tracker = mixpanel.EventTracker("project-token")
        properties = {
            "distinct_id": "user-10",
            "profile": {"plan": "free", "tags": ["initial"]},
        }
        original_thread = threading.Thread
        DeferredThread.created = []
        threading.Thread = DeferredThread

        try:
            worker = tracker.track_async(
                "Async Snapshot",
                properties,
                lambda event, values: callbacks.append((event, values)),
            )
            properties["profile"]["plan"] = "enterprise"
            properties["profile"]["tags"].append("caller-mutation")
            worker.run()
        finally:
            threading.Thread = original_thread

        self.assertEqual(1, len(DeferredThread.created))
        self.assertTrue(worker.started)
        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual({
            "plan": "free",
            "tags": ["initial"],
        }, payload["properties"]["profile"])
        self.assertEqual([
            ("Async Snapshot", {
                "distinct_id": "user-10",
                "profile": {"plan": "free", "tags": ["initial"]},
            }),
        ], callbacks)
        self.assertEqual({
            "plan": "enterprise",
            "tags": ["initial", "caller-mutation"],
        }, properties["profile"])

    def test_track_async_requires_callable_callback_before_thread(self):
        tracker = mixpanel.EventTracker("project-token")
        original_thread = threading.Thread
        FakeThread.created = []
        threading.Thread = FakeThread

        try:
            with self.assertRaises(ValueError):
                tracker.track_async(
                    "Async Event",
                    {"distinct_id": "user-3"},
                    callback="not-callable",
                )
        finally:
            threading.Thread = original_thread

        self.assertEqual([], FakeThread.created)
        self.assertEqual([], self.urls)

    def test_track_async_rejects_invalid_inputs_before_thread(self):
        tracker = mixpanel.EventTracker("project-token")
        original_thread = threading.Thread
        FakeThread.created = []
        threading.Thread = FakeThread

        invalid_calls = [
            (None, {"distinct_id": "user-3"}),
            ("", {"distinct_id": "user-3"}),
            ("Async Event", None),
            ("Async Event", "distinct_id=user-3"),
            ("Async Event", {}),
            ("Async Event", {"distinct_id": None}),
            ("Async Event", {"distinct_id": " \t\n"}),
        ]
        try:
            for event, properties in invalid_calls:
                with self.assertRaises(ValueError):
                    tracker.track_async(event, properties)
        finally:
            threading.Thread = original_thread

        self.assertEqual([], FakeThread.created)
        self.assertEqual([], self.urls)

    def test_track_async_rejects_unserializable_properties_before_thread(self):
        tracker = mixpanel.EventTracker("project-token")
        original_thread = threading.Thread
        FakeThread.created = []
        threading.Thread = FakeThread

        try:
            with self.assertRaises(TypeError):
                tracker.track_async(
                    "Async Event",
                    {"distinct_id": "user-3", "nested": object()},
                )
        finally:
            threading.Thread = original_thread

        self.assertEqual(
            [],
            FakeThread.created,
            "unserializable properties must not create a worker",
        )
        self.assertEqual(
            [],
            self.urls,
            "unserializable properties must not open a request",
        )

    def test_track_async_rejects_non_finite_properties_before_thread(self):
        tracker = mixpanel.EventTracker("project-token")
        original_thread = threading.Thread
        FakeThread.created = []
        callbacks = []
        threading.Thread = FakeThread

        try:
            for value in (float("nan"), float("inf"), float("-inf")):
                with self.assertRaises(ValueError):
                    tracker.track_async(
                        "Invalid Async Measurement",
                        {"distinct_id": "user-3", "measurement": value},
                        lambda event, values: callbacks.append((event, values)),
                    )
        finally:
            threading.Thread = original_thread

        self.assertEqual(
            [],
            FakeThread.created,
            "non-finite properties must not create a worker",
        )
        self.assertEqual(
            [],
            self.urls,
            "non-finite properties must not open a request",
        )
        self.assertEqual([], callbacks)

    def test_track_async_rejects_copy_failures_before_thread(self):
        tracker = mixpanel.EventTracker("project-token")
        original_thread = threading.Thread
        FakeThread.created = []
        threading.Thread = FakeThread

        try:
            with self.assertRaisesRegexp(RuntimeError, "nested copy failed"):
                tracker.track_async(
                    "Async Event",
                    {"distinct_id": "user-3", "nested": UncopyableValue()},
                )
        finally:
            threading.Thread = original_thread

        self.assertEqual(
            [],
            FakeThread.created,
            "copy failures must not create a worker",
        )
        self.assertEqual(
            [],
            self.urls,
            "copy failures must not open a request",
        )


if __name__ == "__main__":
    unittest.main()
