# Skill: Email Draft

Draft and send emails from your hotel accounts via the email provider's API. Always creates drafts — never sends without explicit operator approval.

> **Template note:** Replace `{{INBOX_*}}`, `{{EMAIL_CLI}}`, `{{OPERATOR_NAME}}` and `{{HOTEL_NAME}}` with the wrappers and identifiers your setup uses. See `README.md` for guidance.

## Trigger

Operator asks to reply to, forward, or compose an email from any of the hotel's accounts.

## Accounts

| Alias | Address | Use for |
|-------|---------|---------|
| stays | `{{INBOX_BOOKINGS}}` | **All hotel-room guest communication** (inquiries, pre-arrival, in-stay, post-stay, concierge replies to guests) |
| rental | `{{INBOX_RENTALS}}` | **All whole-villa / whole-property renter communication** |
| primary | `{{INBOX_PRIMARY}}` | **B2B only** — restaurants, drivers, chefs, suppliers, accountants, partners. **Never** to a guest. |

### Routing rule (MANDATORY)

Identify the recipient first. If they were ever a guest of the hotel, use `stays`. If they are a whole-property renter, use `rental`. If they are a service provider / supplier / partner, use `primary`.

If a previous thread is already on the wrong account (e.g. older pre-arrival emails sent from `primary` to a hotel guest), **start a fresh email from the correct account**. Do not continue replying on the wrong account just to preserve threading. Routing rule beats thread continuity.

## Process

### 1. Determine the action

- **Reply** — responding to an existing email (needs `message_id` + `thread_id`)
- **Forward** — forwarding an existing email to a new recipient
- **Compose** — new email, no thread

### 2. Build the email

**CRITICAL: Always use HTML (`text/html`), never plain text.** Plain text loses all formatting.

Use a threaded-reply helper for replies:
```bash
{{DRAFT_REPLY_TOOL}} --account {account} --message-id {message_id} --body '{html_body}' --html
```

For forwards and new emails, use the email CLI directly:
```bash
{{EMAIL_CLI}} {account} drafts-create --json '{draft_json}'
```

### 3. HTML formatting rules

- Wrap paragraphs in `<p>` tags
- Use `<br>` for line breaks within a block
- Use `<ul>`/`<li>` for bullet points
- Use `<hr>` for horizontal rules / section dividers
- Use `<blockquote>` for quoted/forwarded text
- Use `<strong>` for bold headers (From, To, Date, Subject in forwarded chains)
- For forwarded email chains, use grey left-border styling:
  ```html
  <div style="margin-left: 10px; padding-left: 10px; border-left: 2px solid #ccc;">
  ```
- **Never send plain text** — always set the MIME subtype to `html`

### 4. Forward format

When forwarding, include a standard forward header:
```html
<hr>
<p><strong>---------- Forwarded message ----------</strong><br>
<strong>From:</strong> {from}<br>
<strong>Date:</strong> {date}<br>
<strong>Subject:</strong> {subject}<br>
<strong>To:</strong> {to}</p>
```

### 5. Threading

- For replies: include `threadId` in the draft message, and set `In-Reply-To` and `References` headers
- For forwards: new thread (no `threadId` needed unless forwarding within an existing conversation)

### 6. Sign-off

Default sign-off unless instructed otherwise:
```
Best regards,
{{OPERATOR_NAME}}
```

For formal / business emails:
```
Best regards,
{{OPERATOR_NAME}}
{{HOTEL_NAME}}
```

## Guardrails

- **ALWAYS create drafts** — never send directly
- **ALWAYS use HTML** — never plain text
- Show the operator the draft content for approval before anything
- Never expose API keys or credentials in email content
- Routing rule beats thread continuity — start a fresh email from the correct account if needed
