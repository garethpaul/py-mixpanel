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
