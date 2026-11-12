# runs/

The skill's memory between runs. Everything here except this file is ignored by git, because it holds guest names and email text.

| Path | Written by | Purpose |
|---|---|---|
| `LOG.md` | this skill | One entry per run, newest last. The latest run summary is the last entry; other agents read that entry, not a separate file. The skill reads the recent entries before it acts, so a request is never drafted twice. |
| `proposals/{request-id}.md` | this skill | Proposed email text that is not in a mailbox (Level 1, and the shadow drafts at Level 2). |
| `handoff/email-requests/{request-id}.md` | you, or a sibling agent | A request for one draft. The skill reads these and never changes them. |

## Log entry format

```
## 2026-01-15 07:00 | Level 1 | scheduled
Checked: 3 requests (2 new, 1 already done), 2 threads read, 0 own drafts open
Actions taken: none
Proposed: req-0142 -> runs/proposals/req-0142.md (reply, stays)
Skipped: req-0139 (done 2026-01-14, draft r-881)
Errors: none
Needs you: req-0143 complaint about noise, not drafted unattended
```

At Level 2 "Actions taken" lists each draft as `request id -> draft id (action, account, thread id)`. A run that the kill switch stopped is one line: `## {timestamp} | PAUSED | scheduled | nothing done: {reason}`, for example `Level is PAUSED` or `AUTONOMY.md has no valid Level line`.

A request counts as done when a log entry lists it under "Actions taken". To have one drafted again, give it a new id.

## Request file format

One file per email, named `{request-id}.md`. Ids only need to be unique.

```
id: req-0142
from: booking-inquiry-agent        # the sibling agent or person asking
action: reply                      # reply | new   (forwards are never drafted unattended)
account: stays                     # optional hint; the routing rule in the skill decides
message_id: 18c2f0a1b2             # needed for a reply
thread_id: 18c2f0a1b2              # needed for a reply
to: guest@example.com              # needed for a new email
language: en
topic: availability                # plain words; sensitive topics are escalated
brief: |
  Thank them, confirm the dates they asked for are free, offer the garden room.
facts: |
  Garden room free 12-15 March (source: PMS availability check, 2026-01-15 06:55)
```

The skill writes only what `brief`, `facts` and the thread support. Anything else it needs becomes a `[CONFIRM: ...]` marker.
