py-mixpanel
===========

Track events with mixpanel. 


USAGE
=====


`````python
tracker = EventTracker(TOKEN)
tracker.track_async("My Event", {
   "distinct_id": "some_unique_id", 
   "mp_tag_name": "My User Name",
   "my_property": "some value"
   "some_int_value": 0,
})
`````


METHOD
======

Sends requests to track "My Event" or "Any Events" asynchronously.
