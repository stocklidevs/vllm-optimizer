# Feature Specification: Completed Run Pipeline Sync

## User Story

As a cockpit user, I want the pipeline display and next action to update when a
run completes so that I know what happened and what to do next.

## Requirements

- When an active run job completes, the browser must read completed pipeline
  stages from the job result and update the visible pipeline progress.
- The next-action card must change from `Start Optimization` to the next
  meaningful action after run completion.
- The operation summary must explain that report generation is the next step.
- The active server must support the local report action so the next-action
  control can generate/load report artifacts after a run.
- Existing live-run confirmation and promotion gates must remain unchanged.

## Acceptance Criteria

- Completed run jobs with `completed_stages=["plan", "preview", "run"]` mark
  Plan, Preview, and Run complete in the pipeline UI.
- Completed run jobs move the pipeline progress beyond the initial 8%.
- Completed run jobs present `Load Report` as the next action.
- The server supports a local `report` controller action.
- Focused tests, full tests, and browser validation pass.
