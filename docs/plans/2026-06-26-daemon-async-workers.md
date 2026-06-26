# Daemon Async Workers

Status: Completed

## Problem

`track_async()` returned a normal non-daemon thread. A slow Mixpanel request
could therefore keep a command or short-lived process alive until the network
timeout even though analytics submission is best-effort background work.

## Decision

Mark the worker daemon before `start()`. Continue returning the thread so a
caller with an explicit delivery requirement can call `join()` before shutdown.

## Verification

- The focused test failed first because the created worker had no daemon flag.
- Unit coverage requires daemon ownership on the returned started worker.
- A hostile mutation removes the daemon assignment and must fail the suite.
- Full Python 2/3 `make check`, hosted, and exact-head review evidence is
  recorded before merge.
- Pull request #20 implementation head
  `56b1c7a1556ca4f4ed92a1d796103e7bb945d3c5` passed hosted Python 2.7,
  Python 3.11, Python 3.14, CodeQL actions/Python analyses, and the aggregate
  gate.
- Required Codex review stopped before analysis because OpenAI WebSocket and
  HTTPS transports returned HTTP 401. Local, remote, and pull-request heads
  matched, and immutable manual fallback review found no actionable defects.
