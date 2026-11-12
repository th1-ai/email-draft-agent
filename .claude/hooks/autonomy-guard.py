#!/usr/bin/env python3
"""PreToolUse guard for the Bash tool. Example: read it before you rely on it.

Reads the hook JSON from stdin and AUTONOMY.md from the project root, then:

1. Blocks any command that looks like a mail SEND. Always, at every level.
2. In an unattended run (permission mode "dontAsk"):
   - blocks every command when AUTONOMY.md says Level PAUSED or Level 0
     (a missing file, no Level line, two Level lines or an unknown value
     count as PAUSED);
   - blocks draft-creating commands below Level 2.

Exit 2 = block (the stderr text is shown to Claude). Exit 0 = no decision: the
normal permission rules still apply. Text inside quotes is ignored when the
command is checked, so an email body that contains the word "send" passes.

This matches command text. It is a seat belt, not a security boundary: a
command that hides its verb (inside `sh -c '...'` or a wrapper script with a
neutral name) is not seen. Edit the patterns below to fit your own CLI.
"""
import json
import os
import re
import sys

# A send verb as its own word or as part of a subcommand: `send`, `drafts-send`,
# `send_email.py`, `sendmail`. Not matched: `sender`, `resend-policy.md`.
SEND = re.compile(r"(?<![a-z])(send|sendmail|send[-_]\w+|\w+[-_]send)(?![a-z])", re.I)
# A draft-creating command: `drafts-create`, `create_draft_reply.py`, `drafts create`.
DRAFT = re.compile(r"draft", re.I)
# Draft commands that only read: `drafts-list`, `drafts get`, `drafts.show`.
DRAFT_READ = re.compile(r"drafts?[-_ .](list|get|show|read)(?![a-z])", re.I)
QUOTED = re.compile(r"'[^']*'|\"(?:\\.|[^\"\\])*\"")


def block(reason):
    sys.stderr.write("autonomy-guard: " + reason + "\n")
    sys.exit(2)


def read_autonomy(root):
    """Return (level, paused).

    AUTONOMY.md has exactly one line "Level: <value>", value 0-3 or PAUSED.
    A missing file, a missing line, more than one line or an unknown value
    all count as PAUSED.
    """
    try:
        with open(os.path.join(root, "AUTONOMY.md"), encoding="utf-8") as fh:
            values = re.findall(r"^Level:[ \t]*(\S*)[ \t]*$", fh.read(), re.MULTILINE)
    except OSError:
        return 0, True
    if len(values) == 1 and values[0] in ("0", "1", "2", "3"):
        return int(values[0]), False
    return 0, True


def main():
    try:
        data = json.load(sys.stdin)
    except ValueError:
        block("could not read the hook input, so the command is blocked.")
    if data.get("tool_name") != "Bash":
        sys.exit(0)
    command = (data.get("tool_input") or {}).get("command") or ""
    bare = QUOTED.sub(" ", command)

    if SEND.search(bare):
        block("this looks like a send command. This agent creates drafts only; "
              "sending is the operator's click at every autonomy level.")

    if data.get("permission_mode") != "dontAsk":
        sys.exit(0)  # the operator is present and approves each step

    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or "."
    level, paused = read_autonomy(root)
    if paused:
        block("AUTONOMY.md is PAUSED (or has no valid Level line). Scheduled runs "
              "do nothing until the line holds a level digit.")
    if level == 0:
        block("AUTONOMY.md says Level 0. Scheduled runs are off.")
    if level < 2 and DRAFT.search(bare) and not DRAFT_READ.search(bare):
        block("creating a mailbox draft needs Level 2; AUTONOMY.md says Level %d. "
              "Write the proposed text to runs/proposals/ instead." % level)
    sys.exit(0)


if __name__ == "__main__":
    main()
