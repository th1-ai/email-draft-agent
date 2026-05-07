# Email Draft Agent

A Claude Code skill for hotel operators. It drafts replies, forwards, and new emails from the right hotel account, in HTML, threaded properly — and always as a draft, never sent.

Built on the **WAT framework** (Workflows, Agents, Tools): probabilistic AI handles reasoning, deterministic scripts handle execution.

---

## What it does

- **Picks the right account automatically** — guests go to the bookings inbox, whole-property renters to the rentals inbox, suppliers and partners to the primary B2B inbox
- **Enforces routing rule over thread continuity** — if an old thread is on the wrong account, the agent starts a fresh email from the correct one rather than perpetuating the mistake
- **HTML by default** — paragraphs, bullets, blockquotes, forward headers; never plain text (which Gmail strips of formatting)
- **Threads cleanly** — sets `threadId`, `In-Reply-To`, and `References` on replies
- **Signs off in the operator's voice** — default sign-off is configurable
- **Draft-only** — the agent never sends; the operator approves and sends

---

## What you need

- [Claude Code](https://claude.ai/code) installed
- One or more email accounts you can read/draft programmatically (Gmail via the Google Workspace CLI is the reference setup)
- A small helper script for threaded replies, or a CLI that handles HTML MIME parts cleanly

---

## Quick start

1. **Clone the repo** into a Claude Code project:

   ```bash
   git clone https://github.com/th1-ai/email-draft-agent.git
   cd email-draft-agent
   ```

2. **Copy the env template** and fill it in:

   ```bash
   cp .env.example .env
   ```

3. **Edit [`.claude/skills/email-draft/SKILL.md`](.claude/skills/email-draft/SKILL.md)** — replace the placeholders described in [Customising](#customising).

4. **Open in Claude Code** and trigger the skill:

   > "Draft a reply to that supplier email saying we'll pay next week."

---

## File structure

```
email-draft-agent/
├── README.md                                  # This file
├── .env.example                               # Account aliases + sign-off identity
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
| `{{EMAIL_CLI}}` | Email-provider CLI wrapper | `gws` |
| `{{DRAFT_REPLY_TOOL}}` | Threaded-reply helper | `tools/create_draft_reply.py` |
| `{{DRAFT_NEW_TOOL}}` | New-email helper | `tools/create_draft_email.py` |
| `{{OPERATOR_NAME}}` | Name to sign off with | `Jane Doe` |
| `{{HOTEL_NAME}}` | Hotel name for formal sign-offs | `Your Hotel` |

The reference setup uses scripts named `tools/create_draft_reply.py` and `tools/create_draft_email.py`. Yours can live anywhere and use any names — the placeholders are the only thing the skill cares about.

```bash
sed -i '' \
  -e 's|{{INBOX_BOOKINGS}}|bookings@yourhotel.com|g' \
  -e 's|{{EMAIL_CLI}}|gws|g' \
  -e 's|{{OPERATOR_NAME}}|Jane Doe|g' \
  .claude/skills/email-draft/SKILL.md
```

---

## How memory works

This skill leans on Claude Code's per-project memory. Useful patterns to record include:

- **Per-supplier sign-off variations** (formal vs. first-name)
- **Recipient -> account routing exceptions** the agent figured out
- **HTML quirks** discovered with your email client (e.g. specific clients that need extra escaping)

Keep memory concise — one line per pattern.

---

## Related agents

This skill is the underlying draft-creation primitive used by:

- [`booking-inquiry-agent`](https://github.com/th1-ai/booking-inquiry-agent) — drafts warm, personalised replies to guest inquiries
- [`pre-arrival-outreach-agent`](https://github.com/th1-ai/pre-arrival-outreach-agent) — drafts welcome messages for upcoming premium guests
- [`email-processor-agent`](https://github.com/th1-ai/email-processor-agent) — calls into this skill when classification yields a draftable email
- [`email-triage-agent`](https://github.com/th1-ai/email-triage-agent) — surfaces what needs a draft in the first place

---

## License

MIT — see [LICENSE](LICENSE).
