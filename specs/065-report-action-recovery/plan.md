# Implementation Plan: Report Action Recovery After Closing History

**Status**: Completed

## Summary

Fix the follow-on state bug introduced by loaded-run recovery: after hiding old
report actions, later pipeline updates must be able to reconfigure and show the
main Next Action button as `Load Report` or `Review Report`.

## Architecture

- Add small browser-side helpers for reconfiguring the main action button as a
  controller action or a tab-jump action.
- Ensure those helpers remove the `hidden` class whenever a dynamic action
  becomes available.
- Use delegated click handling for controller and tab-jump buttons so role
  changes after page load remain wired.
- Preserve static HTML command-copy behavior and active `cockpit-server`
  endpoint behavior.

## Verification

- Red/green regression test for report loading after closing loaded history.
- Focused cockpit renderer and CLI cockpit tests.
- Release check.
- Full pytest suite.
