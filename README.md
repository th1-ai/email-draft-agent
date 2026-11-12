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
├── .env.example                               # Record of your setup values
├── .gitignore
├── LICENSE
└── .claude/
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
| The draft is on the wrong account | Tell Claude the correct one, then add a routing line to `CLAUDE.md` so it holds next time. |

---

## Related agents

This skill is the draft-creation step that these agents can hand off to:

- [`booking-inquiry-agent`](https://github.com/th1-ai/booking-inquiry-agent) — drafts warm, personalised replies to guest inquiries
- [`pre-arrival-outreach-agent`](https://github.com/th1-ai/pre-arrival-outreach-agent) — drafts welcome messages for upcoming premium guests
- [`email-processor-agent`](https://github.com/th1-ai/email-processor-agent) — classifies incoming mail and decides which emails need a draft
- [`email-triage-agent`](https://github.com/th1-ai/email-triage-agent) — surfaces what needs a reply in the first place
- [`agent-notification-agent`](https://github.com/th1-ai/agent-notification-agent) — notifies travel agents of price changes; use this skill when one of them needs a bespoke message

Each is its own template repo; none of them calls this one automatically. To combine them, copy the skill folders into one project.

The full set: [21 AI Agents That Run a Real Hotel](https://th1.ai/agent-stack).

---

## License

MIT — see [LICENSE](LICENSE).
