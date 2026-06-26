import base64
import json
import sys
import threading
import unittest

try:
    import urlparse
except ImportError:
    from urllib import parse as urlparse

try:
    basestring
except NameError:
    basestring = (str, bytes)

sys.dont_write_bytecode = True

import mixpanel

if hasattr(unittest.TestCase, "assertRaisesRegex"):
    unittest.TestCase.assertRaisesPattern = unittest.TestCase.assertRaisesRegex
else:
    unittest.TestCase.assertRaisesPattern = unittest.TestCase.assertRaisesRegexp


class FakeResponse(object):
    def __init__(self, response_body="1", read_error=None, close_error=None, status=200):
        self.response_body = response_body
        self.read_error = read_error
        self.close_error = close_error
        self.status = status
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
        if self.close_error is not None:
            raise self.close_error

    def getcode(self):
        return self.status


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


class SelfCopyingDict(dict):
    def copy(self):
        return self


class SelfAliasingDict(dict):
    def __deepcopy__(self, memo):
        return self


class SelfAliasingList(list):
    def __deepcopy__(self, memo):
        return self


class HostileItemsDict(dict):
    def items(self):
        return [("distinct_id", "attacker-controlled")]


class FailingStartThread(object):
    def __init__(self, target=None, kwargs=None):
        self.target = target
        self.kwargs = kwargs or {}

    def start(self):
        raise RuntimeError("thread start failed")


class EventTrackerTest(unittest.TestCase):
    def setUp(self):
        self.urls = []
        self.requests = []
        self.timeouts = []
        self.responses = []
        self.response_body = "1"
        self.response_read_error = None
        self.response_close_error = None
        self.response_status = 200
        self.original_urlopen = mixpanel.urllib2.urlopen
        self.original_time = mixpanel.time.time
        mixpanel.urllib2.urlopen = self.urlopen
        mixpanel.time.time = lambda: 1234567890

    def tearDown(self):
        mixpanel.urllib2.urlopen = self.original_urlopen
        mixpanel.time.time = self.original_time

    def urlopen(self, request, timeout=None):
        self.requests.append(request)
        if hasattr(request, "get_full_url"):
            url = request.get_full_url()
        else:
            url = request
        self.urls.append(url)
        self.timeouts.append(timeout)
        response = FakeResponse(
            self.response_body,
            self.response_read_error,
            self.response_close_error,
            self.response_status,
        )
        self.responses.append(response)
        return response

    def payload_from_request(self, request):
        if hasattr(request, "get_full_url"):
            url = request.get_full_url()
            body = request.data
            if not isinstance(body, str):
                body = body.decode("ascii")
            encoded = urlparse.parse_qs(body)
        else:
            url = request
            encoded = urlparse.parse_qs(urlparse.urlparse(url).query)

        parsed = urlparse.urlparse(url)
        payload = json.loads(base64.b64decode(encoded["data"][0]))
        return parsed, encoded, payload

    def payload_from_url(self, url):
        parsed = urlparse.urlparse(url)
        if "data" in urlparse.parse_qs(parsed.query):
            return self.payload_from_request(url)
        return self.payload_from_request(self.requests[self.urls.index(url)])

    def request_header(self, request, name):
        return request.get_header(name) or request.get_header(name.title())

    def test_track_posts_https_payload(self):
        callbacks = []
        tracker = mixpanel.EventTracker("project-token")

        def callback(event, properties):
            callbacks.append((event, properties.copy()))

        tracker.track("Signed Up", {"distinct_id": "user-1"}, callback)

        self.assertEqual(1, len(self.urls))
        request = self.requests[0]
        parsed, form, payload = self.payload_from_request(request)
        self.assertEqual("https", parsed.scheme)
        self.assertEqual("api.mixpanel.com", parsed.netloc)
        self.assertEqual("/track/", parsed.path)
        self.assertEqual("", parsed.query)
        self.assertEqual("POST", request.get_method())
        self.assertEqual(["data"], sorted(form))
        self.assertIsInstance(request.data, bytes)
        self.assertEqual(
            "application/x-www-form-urlencoded",
            self.request_header(request, "Content-type"),
        )
        self.assertEqual(
            str(len(request.data)),
            self.request_header(request, "Content-length"),
        )
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

    def test_track_keeps_event_data_out_of_url(self):
        token = "private-token-marker/?#&=%0d%0aHost:attacker.invalid"
        distinct_id = "private-distinct-marker/?#&=%0d%0a"
        event = "Private Event Marker /?&=#%0d%0a"
        property_value = "private-property-marker/?#&=%0d%0a"
        tracker = mixpanel.EventTracker(token)

        tracker.track(event, {
            "distinct_id": distinct_id,
            "private_property": property_value,
        })

        request = self.requests[0]
        url = request.get_full_url()
        self.assertEqual(mixpanel.TRACK_BASE_URL, url)
        for private_value in (
                "data", token, distinct_id, event, property_value,
                "private_property"):
            self.assertNotIn(private_value, url)

    def test_track_form_body_round_trips_unicode_and_binary_bytes(self):
        self.response_body = b"1"
        tracker = mixpanel.EventTracker(u"project-token")
        event = json.loads('"Signed \\u2603 Up"')
        properties = {
            "distinct_id": json.loads('"user-\\u2603"'),
            "message": json.loads('"snowman \\u2603 and rocket \\ud83d\\ude80"'),
        }

        tracker.track(event, properties)

        request = self.requests[0]
        parsed, form, payload = self.payload_from_request(request)
        self.assertEqual("", parsed.query)
        self.assertEqual(["data"], sorted(form))
        self.assertIsInstance(request.data, bytes)
        self.assertEqual(event, payload["event"])
        self.assertEqual(properties["distinct_id"], payload["properties"]["distinct_id"])
        self.assertEqual(properties["message"], payload["properties"]["message"])

    def test_track_posts_large_event_body_without_putting_it_in_url(self):
        large_value = "x" * (1024 * 1024)
        tracker = mixpanel.EventTracker("large-token")

        tracker.track("Large Event", {
            "distinct_id": "large-user",
            "blob": large_value,
        })

        request = self.requests[0]
        parsed, form, payload = self.payload_from_request(request)
        self.assertEqual("", parsed.query)
        self.assertGreater(len(request.data), 1024 * 1024)
        self.assertEqual(str(len(request.data)), self.request_header(
            request, "Content-length"))
        self.assertEqual(large_value, payload["properties"]["blob"])
        self.assertEqual(["data"], sorted(form))

    def test_track_closes_response_when_read_fails_without_leaking_details(self):
        callbacks = []
        private_marker = "project-token-private-read"
        self.response_read_error = IOError(private_marker)
        tracker = mixpanel.EventTracker("project-token")

        with self.assertRaisesPattern(mixpanel.MixpanelError, "Mixpanel request failed") as raised:
            tracker.track(
                "Signed Up",
                {"distinct_id": "user-1"},
                lambda event, properties: callbacks.append((event, properties)),
            )

        self.assertNotIn(private_marker, str(raised.exception))
        self.assertEqual([], callbacks)
        self.assertEqual(1, len(self.responses))
        self.assertTrue(self.responses[0].closed)

    def test_track_preserves_primary_failure_when_response_close_also_fails(self):
        private_read_marker = "project-token-private-read"
        private_close_marker = "api-secret-private-close"
        self.response_read_error = IOError(private_read_marker)
        self.response_close_error = IOError(private_close_marker)
        tracker = mixpanel.EventTracker("project-token", api_key="api-secret")

        with self.assertRaisesPattern(mixpanel.MixpanelError, "Mixpanel request failed") as raised:
            tracker.track("Signed Up", {"distinct_id": "user-1"})

        self.assertNotIn(private_read_marker, str(raised.exception))
        self.assertNotIn(private_close_marker, str(raised.exception))
        self.assertTrue(self.responses[0].closed)

    def test_track_rejects_non_success_http_status_before_callback(self):
        callbacks = []
        self.response_status = 503
        tracker = mixpanel.EventTracker("project-token")

        with self.assertRaisesPattern(mixpanel.MixpanelError, "Mixpanel request failed"):
            tracker.track(
                "Signed Up",
                {"distinct_id": "user-1"},
                lambda event, properties: callbacks.append((event, properties)),
            )

        self.assertEqual([], callbacks)
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
            with self.assertRaisesPattern(mixpanel.MixpanelError, "Mixpanel rejected the event"):
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

        with self.assertRaisesPattern(
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

        if sys.version_info[0] >= 3:
            with self.assertRaises(ValueError):
                mixpanel.EventTracker(b"project-token")

    def test_tracker_requires_nonblank_api_key_when_provided(self):
        for api_key in ("", " \t\n", 123):
            with self.assertRaises(ValueError):
                mixpanel.EventTracker("project-token", api_key=api_key)

        tracker = mixpanel.EventTracker("project-token", api_key=" api-secret ")
        self.assertEqual("api-secret", tracker.api_key)

        if sys.version_info[0] >= 3:
            with self.assertRaises(ValueError):
                mixpanel.EventTracker("project-token", api_key=b"api-secret")

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

    def test_track_isolates_self_copying_dict_subclass(self):
        callbacks = []
        tracker = mixpanel.EventTracker("project-token")
        properties = SelfCopyingDict(distinct_id="user-subclass", plan="free")

        tracker.track(
            "Subclass Isolation",
            properties,
            lambda event, values: callbacks.append((event, dict(values))),
        )

        self.assertEqual({
            "distinct_id": "user-subclass",
            "plan": "free",
        }, properties)
        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual("project-token", payload["properties"]["token"])
        self.assertEqual(1234567890, payload["properties"]["time"])
        self.assertEqual([
            ("Subclass Isolation", {
                "distinct_id": "user-subclass",
                "plan": "free",
            }),
        ], callbacks)
        self.assertNotIn("token", callbacks[0][1])
        self.assertNotIn("time", callbacks[0][1])

    def test_track_uses_builtin_dict_items_for_hostile_subclasses(self):
        tracker = mixpanel.EventTracker("project-token")
        properties = HostileItemsDict(distinct_id="real-user", plan="free")

        tracker.track("Hostile Items", properties)

        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual("real-user", payload["properties"]["distinct_id"])
        self.assertEqual("free", payload["properties"]["plan"])

    def test_track_callback_mutation_cannot_change_caller_or_payload(self):
        tracker = mixpanel.EventTracker("project-token")
        properties = {
            "distinct_id": "user-callback",
            "profile": {"tags": ["initial"]},
        }

        def callback(event, values):
            values["profile"]["tags"].append("callback-mutation")

        tracker.track("Callback Isolation", properties, callback)

        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual(["initial"], properties["profile"]["tags"])
        self.assertEqual(["initial"], payload["properties"]["profile"]["tags"])

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

    def test_track_redacts_request_errors_without_callback(self):
        callbacks = []
        tracker = mixpanel.EventTracker("project-token", api_key="api-secret")

        def failing_urlopen(url, timeout=None):
            self.urls.append(url)
            self.timeouts.append(timeout)
            raise mixpanel.urllib2.URLError(url)

        mixpanel.urllib2.urlopen = failing_urlopen

        with self.assertRaisesPattern(mixpanel.MixpanelError, "Mixpanel request failed") as raised:
            tracker.track(
                "Request Failed",
                {"distinct_id": "user-4"},
                lambda event, properties: callbacks.append((event, properties)),
            )

        error_text = str(raised.exception)
        self.assertNotIn("project-token", error_text)
        self.assertNotIn("api-secret", error_text)
        self.assertNotIn("user-4", error_text)
        if hasattr(raised.exception, "__context__"):
            self.assertIsNone(raised.exception.__context__)
        self.assertEqual(1, len(self.urls))
        self.assertEqual([mixpanel.REQUEST_TIMEOUT_SECONDS], self.timeouts)
        self.assertEqual([], callbacks)

    def test_import_legacy_get_path_remains_unchanged_with_api_key(self):
        tracker = mixpanel.EventTracker("project-token", api_key="api-secret")

        tracker.track("Imported", {"distinct_id": "user-2"})

        self.assertIsInstance(self.requests[0], str)
        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual("https", parsed.scheme)
        self.assertEqual("/import/", parsed.path)
        self.assertEqual(["api_key", "data"], sorted(query))
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
        self.assertTrue(thread.daemon)
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

    def test_track_async_isolates_self_copying_dict_subclass(self):
        callbacks = []
        tracker = mixpanel.EventTracker("project-token")
        properties = SelfCopyingDict(distinct_id="async-subclass", plan="paid")
        original_thread = threading.Thread
        FakeThread.created = []
        threading.Thread = FakeThread

        try:
            tracker.track_async(
                "Async Subclass Isolation",
                properties,
                lambda event, values: callbacks.append((event, dict(values))),
            )
        finally:
            threading.Thread = original_thread

        self.assertEqual({
            "distinct_id": "async-subclass",
            "plan": "paid",
        }, properties)
        self.assertEqual(1, len(FakeThread.created))
        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual("project-token", payload["properties"]["token"])
        self.assertEqual(1234567890, payload["properties"]["time"])
        self.assertEqual([
            ("Async Subclass Isolation", {
                "distinct_id": "async-subclass",
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

    def test_track_async_canonicalizes_self_aliasing_nested_containers(self):
        callbacks = []
        tracker = mixpanel.EventTracker("project-token")
        profile = SelfAliasingDict(
            plan="free",
            tags=SelfAliasingList(["initial"]),
        )
        properties = {"distinct_id": "user-11", "profile": profile}
        original_thread = threading.Thread
        DeferredThread.created = []
        threading.Thread = DeferredThread

        try:
            worker = tracker.track_async(
                "Async Hostile Snapshot",
                properties,
                lambda event, values: callbacks.append((event, values)),
            )
            profile["plan"] = "enterprise"
            profile["tags"].append("caller-mutation")
            worker.run()
        finally:
            threading.Thread = original_thread

        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual({
            "plan": "free",
            "tags": ["initial"],
        }, payload["properties"]["profile"])
        self.assertEqual({
            "plan": "free",
            "tags": ["initial"],
        }, callbacks[0][1]["profile"])

    def test_track_async_snapshots_tracker_credentials_before_worker(self):
        tracker = mixpanel.EventTracker("original-token", api_key="original-api-key")
        original_thread = threading.Thread
        DeferredThread.created = []
        threading.Thread = DeferredThread

        try:
            worker = tracker.track_async(
                "Async Credential Snapshot",
                {"distinct_id": "user-12"},
            )
            tracker.token = "replacement-token"
            tracker.api_key = "replacement-api-key"
            worker.run()
        finally:
            threading.Thread = original_thread

        parsed, query, payload = self.payload_from_url(self.urls[0])
        self.assertEqual("original-token", payload["properties"]["token"])
        self.assertEqual(["original-api-key"], query["api_key"])
        self.assertNotIn("replacement-token", self.urls[0])
        self.assertNotIn("replacement-api-key", self.urls[0])

    def test_track_async_does_not_retain_worker_when_start_fails(self):
        tracker = mixpanel.EventTracker("project-token")
        original_thread = threading.Thread
        threading.Thread = FailingStartThread

        try:
            with self.assertRaisesPattern(RuntimeError, "thread start failed"):
                tracker.track_async(
                    "Async Start Failure",
                    {"distinct_id": "user-13"},
                )
        finally:
            threading.Thread = original_thread

        self.assertEqual([], self.urls)

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

    def test_track_rejects_circular_properties_before_request(self):
        tracker = mixpanel.EventTracker("project-token")
        properties = {"distinct_id": "user-cycle"}
        properties["cycle"] = properties

        with self.assertRaisesPattern(ValueError, "Circular reference detected"):
            tracker.track("Circular", properties)

        self.assertEqual([], self.urls)

    def test_track_async_rejects_circular_properties_before_thread(self):
        tracker = mixpanel.EventTracker("project-token")
        properties = {"distinct_id": "user-cycle"}
        properties["cycle"] = properties
        original_thread = threading.Thread
        FakeThread.created = []
        threading.Thread = FakeThread

        try:
            with self.assertRaisesPattern(ValueError, "Circular reference detected"):
                tracker.track_async("Circular Async", properties)
        finally:
            threading.Thread = original_thread

        self.assertEqual([], FakeThread.created)
        self.assertEqual([], self.urls)

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

    def test_track_async_rejects_non_json_objects_before_thread(self):
        tracker = mixpanel.EventTracker("project-token")
        original_thread = threading.Thread
        FakeThread.created = []
        threading.Thread = FakeThread

        try:
            with self.assertRaisesPattern(
                    TypeError,
                    "Mixpanel properties must contain JSON values"):
                tracker.track_async(
                    "Async Event",
                    {"distinct_id": "user-3", "nested": UncopyableValue()},
                )
        finally:
            threading.Thread = original_thread

        self.assertEqual(
            [],
            FakeThread.created,
            "non-JSON values must not create a worker",
        )
        self.assertEqual(
            [],
            self.urls,
            "non-JSON values must not open a request",
        )


if __name__ == "__main__":
    unittest.main()
