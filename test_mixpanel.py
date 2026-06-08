import base64
import json
import unittest
import urlparse

import mixpanel


class FakeResponse(object):
    def read(self):
        return "1"


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


if __name__ == "__main__":
    unittest.main()
