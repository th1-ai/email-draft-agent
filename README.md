# Email Draft Agent

A Claude Code skill for hotel operators. It drafts replies, forwards, and new emails from the right hotel account, in HTML, threaded properly — and always as a draft, never sent.

Built on the **WAT framework** (Workflows, Agents, Tools): probabilistic AI handles reasoning, deterministic scripts handle execution.

This repo is a template. It contains the skill (the instructions Claude follows) and nothing else: you supply the email CLI and helper scripts that talk to your mail provider.

---

## What it does

- **Picks the right account** — guests go to the bookings inbox, whole-property renters to the rentals inbox, suppliers and partners to the primary B2B inbox. When a recipient could fit more than one, it asks you
- **Enforces routing rule over thread continuity** — if an old thread is on the wrong account, the agent starts a fresh email from the correct one rather than perpetuating the mistake
- **HTML by default** — paragraphs, bullets, blockquotes, forward headers; never plain text (which loses formatting in most mail clients)
- **Threads cleanly** — sets `threadId`, `In-Reply-To`, and `References` on replies
- **Does not make things up** — a missing price, date or policy becomes a visible `[CONFIRM: ...]` marker in the draft, listed in the report, instead of a guess
- **Signs off in the operator's voice** — default sign-off is configurable
- **Draft-only** — the agent never sends; it shows you the text, creates the draft, and you send
- **Can run on a schedule** — it works through a queue of draft requests on its own, within the level you set in [`AUTONOMY.md`](AUTONOMY.md) (report only by default), remembers what it did in `runs/LOG.md`, and interrupts you only for exceptions. See [Run it on its own](#run-it-on-its-own)

---

## What you need

- [Claude Code](https://code.claude.com/docs/en/overview) installed
- One or more email accounts you can read/draft programmatically (Gmail via a Google Workspace CLI is the reference setup)
- A small helper script for threaded replies and one for new emails, or a CLI that handles HTML MIME parts cleanly. These are **not** included in this repo

---

## Quick start

1. **Clone the repo** and open Claude Code in it:

   ```bash
   git clone https://github.com/th1-ai/email-draft-agent.git
   cd email-draft-agent
   claude
   ```

2. **Run the first-run setup.** Paste this into Claude Code:

   > Read the README and set this skill up with me. Ask me for each placeholder in the Customising table, one at a time, then write my answers into `.claude/skills/email-draft/SKILL.md` and into a new `.env` copied from `.env.example`. Do not guess any value. When you are done, check that no double-brace placeholders are left in the skill file.

   Prefer to do it by hand? Copy `.env.example` to `.env`, then edit [`.claude/skills/email-draft/SKILL.md`](.claude/skills/email-draft/SKILL.md) and replace the placeholders described in [Customising](#customising).

3. **Use the skill.** Ask in plain words, or type `/email-draft`:

   > "Draft a reply to that supplier email saying we'll pay next week."

To use the skill inside another project, copy the `.claude/skills/email-draft/` folder into that project's `.claude/skills/` folder.

---

## Verify it works

1. Type `/` in Claude Code. `email-draft` must be in the list. (Or ask "What skills are available?")
2. Ask for a test draft to yourself: "Draft a new email from the primary account to `<your own address>` with the subject Test."
3. Check three things: Claude showed you the text before creating anything, the draft is in the Drafts folder of the right mailbox with its formatting intact, and nothing was sent.
4. Reply to any real thread as a second test and check that the draft sits inside that thread.

---

## File structure

```
email-draft-agent/
├── README.md                                  # This file
├── AUTONOMY.md                                # The level, limits and kill switch (you edit this)
├── .env.example                               # Record of your setup values
├── .gitignore
├── LICENSE
├── runs/
│   ├── README.md                              # Log, proposal and request formats
│   └── .gitkeep                               # LOG.md, proposals/ and handoff/ appear here (git-ignored)
└── .claude/
    ├── settings.example.json                  # Example permissions + hook for unattended runs
    ├── hooks/
    │   └── autonomy-guard.py                  # Example hook: blocks sends, enforces the level
    └── skills/
        └── email-draft/
            └── SKILL.md                       # The skill definition
```

---

## Customising

The skill file uses placeholders so it can be adapted to any email stack. Replace the following before first run:

| Placeholder | What to put | Example |
|---|---|---|
| `{{INBOX_PRIMARY}}` | B2B / supplier inbox | `info@yourhotel.com` |
| `{{INBOX_BOOKINGS}}` | Hotel-room guest inbox | `bookings@yourhotel.com` |
| `{{INBOX_RENTALS}}` | Whole-property / villa inbox | `rentals@yourhotel.com` |
| `{{EMAIL_CLI}}` | Email-provider CLI wrapper (reads mail, creates drafts) | `gws` |
| `{{DRAFT_REPLY_TOOL}}` | Threaded-reply helper | `tools/create_draft_reply.py` |
| `{{DRAFT_NEW_TOOL}}` | New-email / forward helper | `tools/create_draft_email.py` |
| `{{OPERATOR_NAME}}` | Name to sign off with | `Jane Doe` |
| `{{HOTEL_NAME}}` | Hotel name for formal sign-offs | `Your Hotel` |

The reference setup uses scripts named `tools/create_draft_reply.py` and `tools/create_draft_email.py`. Yours can live anywhere and use any names. The command lines in the skill file are examples: change the flags to the ones your helper or CLI really accepts.

`{{EMAIL_CLI}}`, `{{DRAFT_REPLY_TOOL}}` and `{{DRAFT_NEW_TOOL}}` also appear in [`.claude/settings.example.json`](.claude/settings.example.json). That file does nothing until you copy it; see [Run it on its own](#run-it-on-its-own).

**Fewer than three inboxes?** Delete the rows you do not have from the Accounts table in the skill file, and adjust the routing rule to match. With one inbox, the routing rule has nothing to decide and you can remove it.

**`.env` is not read by the skill.** Claude Code does not substitute `.env` values into a skill file, so the values must be written into `SKILL.md` itself. `.env` is a record of your setup and the place for whatever credentials your own CLI or helper scripts need.

To replace placeholders from the shell (macOS shown; on Linux use `sed -i` without the `''`):

```bash
sed -i '' \
  -e 's|{{INBOX_BOOKINGS}}|bookings@yourhotel.com|g' \
  -e 's|{{EMAIL_CLI}}|gws|g' \
  -e 's|{{OPERATOR_NAME}}|Jane Doe|g' \
  .claude/skills/email-draft/SKILL.md
```

---

## Run it on its own

Out of the box the skill runs when you ask. It can also run on a schedule and work through a queue of draft requests. How far it goes is set by one line in [`AUTONOMY.md`](AUTONOMY.md):

| Level | What a scheduled run does |
|---|---|
| PAUSED | Nothing. It logs why and stops. A missing file or an invalid `Level:` line counts as PAUSED. |
| 0 | Nothing. On request only. |
| 1 (default) | Reads the requests and threads, writes proposed text to `runs/proposals/`. Nothing in any mailbox. |
| 2 | Also creates the drafts in the mailbox (10 per run, 30 per day, one per thread). You send. |
| 3 | Same as 2. This agent has no Level 3 actions: it never sends. |

Sensitive topics (complaints, refunds, legal, medical, safety), forwards and anything unclear are never drafted unattended. They are listed under "Needs you" at the top of the run report.

**Where the work comes from.** A scheduled run does not scan the inbox; that is the job of [`email-triage-agent`](https://github.com/th1-ai/email-triage-agent) and [`email-processor-agent`](https://github.com/th1-ai/email-processor-agent). It reads request files in `runs/handoff/email-requests/`, one per email, in the format shown in [`runs/README.md`](runs/README.md). You can write one by hand, or have a sibling agent in the same project write them.

### 1. Set the permissions (example)

A scheduled run has nobody to click "allow", so it needs its permissions up front. [`.claude/settings.example.json`](.claude/settings.example.json) is a least-privilege example. Finish the first-run setup first, then:

```bash
cp .claude/settings.example.json .claude/settings.local.json
```

Open the copy and replace the three placeholders with the commands exactly as Claude runs them (if your helper is started as `python3 tools/create_draft_reply.py`, the rule is `Bash(python3 tools/create_draft_reply.py *)`). `settings.local.json` is git-ignored. What the example does:

- **allows** your email CLI, your two draft helpers, and file writes inside `runs/`. Reading files in the project needs no rule;
- **denies** reading `.env`, editing `AUTONOMY.md` or anything under `.claude/`, `rm`, `curl`, `wget`, `git push`, and the web tools;
- **registers one hook**, [`.claude/hooks/autonomy-guard.py`](.claude/hooks/autonomy-guard.py) (needs `python3`). It blocks any command that looks like a mail send, at every level and in your own sessions too. In a scheduled run it also blocks everything when `AUTONOMY.md` is at `Level: PAUSED` or `Level: 0` (a missing file, a missing or repeated `Level:` line and an unknown value count as PAUSED), and blocks draft-creating commands below Level 2.

Allowing your email CLI also allows its send subcommand, which is why the hook is there. The hook matches command text, so treat it as a seat belt: if your CLI's send or draft commands are named differently, edit the patterns at the top of the script and test it:

```bash
echo '{"tool_name":"Bash","permission_mode":"dontAsk","cwd":"'"$PWD"'","tool_input":{"command":"YOUR SEND COMMAND HERE"}}' \
  | .claude/hooks/autonomy-guard.py; echo "exit code $?"   # 2 = blocked, 0 = not blocked
```

Because the copy denies edits under `.claude/`, Claude can no longer change the skill file for you. Remove that line for a moment if you re-run the setup.

### 2. Run it once by hand

```bash
claude -p "/email-draft scheduled run" --permission-mode dontAsk
```

`-p` runs Claude Code without the interactive screen and prints the report. `dontAsk` denies every action that would otherwise ask for approval, so only the rules in your settings file apply. Check the output and `runs/LOG.md`.

### 3. Schedule it (cron example, macOS or Linux)

```
# weekdays at 07:00, 11:00 and 15:00 (crontab -e)
0 7,11,15 * * 1-5  cd /path/to/email-draft-agent && /full/path/to/claude -p "/email-draft scheduled run" --permission-mode dontAsk >> runs/cron.log 2>&1
```

Use the full path from `command -v claude`, because cron has a short `PATH`. This line is an example and was not run as part of this template; the machine must be on and logged in to Claude Code. The Claude Code docs describe other schedulers ([desktop scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks), [cloud routines](https://code.claude.com/docs/en/routines)); those run in a different environment and are not covered here.

Scheduled use of a personal Pro or Max plan is subject to Anthropic's usage policy, which assumes ordinary individual use; for a heavy or business-critical schedule, use an API key or a Team or Enterprise plan.

### 4. Move up a level

1. Run at Level 1 for a week. Read `runs/proposals/` and the "Needs you" items in `runs/LOG.md` each day.
2. When the proposals are ones you would send with little change, change `Level: 1` to `Level: 2` in `AUTONOMY.md`. The first 5 drafts at the new level are still written as proposals only.
3. To stop at any time, change the line to `Level: PAUSED` (or `Level: 0`).

---

## Teaching it your preferences

A skill has no memory of its own. Two Claude Code features carry what it learns between sessions:

- **`CLAUDE.md`** in the project root: rules you write, loaded in every session. Use it for things that must always hold, for example "the laundry supplier is always addressed formally".
- **Auto memory**: notes Claude writes itself when you correct it or say "remember this". It is stored on your machine per project, outside the repo. Run `/memory` to read or edit it.

Useful things to record:

- **Per-supplier sign-off variations** (formal vs. first-name)
- **Recipient -> account routing exceptions** you have decided on
- **HTML quirks** discovered with your email client (e.g. specific clients that need extra escaping)

Keep it concise — one line per pattern.

---

## Troubleshooting

| Problem | What to check |
|---|---|
| `/email-draft` is not in the `/` menu | Claude Code must be started in the folder that contains `.claude/`. The file must be at `.claude/skills/email-draft/SKILL.md`, and the `---` of its header must be the first line. |
| Claude stops and lists placeholders | Text in double curly braces is still in `SKILL.md`. Run the first-run setup again or replace it by hand. |
| "command not found" or "no such file" | The `{{EMAIL_CLI}}`, `{{DRAFT_REPLY_TOOL}}` or `{{DRAFT_NEW_TOOL}}` value does not point at something installed on this machine. Run the command yourself in a terminal first. |
| The draft arrives as one block of text | Your helper created a plain-text message. It must set the MIME type to `text/html`. |
| The reply is not inside the thread | Your helper must set `threadId` plus the `In-Reply-To` and `References` headers from the original message. |
| A scheduled run does nothing | Read the last line of `runs/LOG.md`. `AUTONOMY.md` is at `Level: 0` or `Level: PAUSED` (or has no valid `Level:` line), placeholders are left in the skill file, or there is no request file in `runs/handoff/email-requests/`. |
| A scheduled run reports denied commands | The `allow` rules in `.claude/settings.local.json` do not match the command as Claude writes it. Run step 2 by hand and compare. |
| The hook blocks a command it must not block | A word such as "send" or "draft" is in the command outside quotes (a file name, a flag). Adjust the patterns at the top of `.claude/hooks/autonomy-guard.py`. |
| The draft is on the wrong account | Tell Claude the correct one, then add a routing line to `CLAUDE.md` so it holds next time. |

---

## Related agents

This skill is the draft-creation step that these agents can hand off to:

- [`booking-inquiry-agent`](https://github.com/th1-ai/booking-inquiry-agent) — drafts warm, personalised replies to guest inquiries
- [`pre-arrival-outreach-agent`](https://github.com/th1-ai/pre-arrival-outreach-agent) — drafts welcome messages for upcoming premium guests
- [`email-processor-agent`](https://github.com/th1-ai/email-processor-agent) — classifies incoming mail and decides which emails need a draft
- [`email-triage-agent`](https://github.com/th1-ai/email-triage-agent) — surfaces what needs a reply in the first place
- [`agent-notification-agent`](https://github.com/th1-ai/agent-notification-agent) — notifies travel agents of price changes; use this skill when one of them needs a bespoke message

- [`concierge-agent`](https://github.com/th1-ai/concierge-agent) — handles guest concierge requests; its replies to guests can go through this skill
- [`morning-routine-agent`](https://github.com/th1-ai/morning-routine-agent) — the daily briefing; it can read the last entry of this repo's `runs/LOG.md` for the "Needs you" items

Each is its own template repo; none of them calls this one automatically. To combine them, copy the skill folders into one project. The handoff is a file: a sibling (or you) writes a request into `runs/handoff/email-requests/` in the format in [`runs/README.md`](runs/README.md), and the next scheduled run picks it up.

The full set: [21 AI Agents That Run a Real Hotel](https://th1.ai/agent-stack).

---

## License

MIT — see [LICENSE](LICENSE).
