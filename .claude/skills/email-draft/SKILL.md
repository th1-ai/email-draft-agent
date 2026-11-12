---
name: email-draft
description: Draft a reply, forward or new email from the correct hotel mailbox, in HTML, threaded properly, and saved as a draft only (never sent). Use when the operator asks to reply to, answer, forward, write or compose an email from one of the hotel's accounts, or when another agent or skill needs a guest or supplier email drafted.
---

# Skill: Email Draft

Draft emails from the hotel's accounts through the operator's email CLI or helper scripts. This skill only ever creates drafts. The operator reads each draft and sends it.

> **Template note:** `{{INBOX_PRIMARY}}`, `{{INBOX_BOOKINGS}}`, `{{INBOX_RENTALS}}`, `{{EMAIL_CLI}}`, `{{DRAFT_REPLY_TOOL}}`, `{{DRAFT_NEW_TOOL}}`, `{{OPERATOR_NAME}}` and `{{HOTEL_NAME}}` are placeholders. See `README.md` for what goes in each.

## Before you start

If this file still contains text in double curly braces, the skill is not set up. Stop, tell the operator which placeholders are left, and offer to fill them in together (see "First-run setup" in `README.md`). Do not guess an address or a command.

## Accounts

| Alias | Address | Use for |
|-------|---------|---------|
| stays | `{{INBOX_BOOKINGS}}` | **All hotel-room guest communication** (inquiries, pre-arrival, in-stay, post-stay, concierge replies to guests) |
| rental | `{{INBOX_RENTALS}}` | **All whole-villa / whole-property renter communication** |
| primary | `{{INBOX_PRIMARY}}` | **B2B only**: restaurants, drivers, chefs, suppliers, accountants, partners. **Never** to a guest. |

### Routing rule (mandatory)

Identify the recipient first, then pick the account:

- A hotel-room guest, past, present or future: `stays`.
- A whole-property renter: `rental`.
- A service provider, supplier or partner: `primary`.

Routing beats thread continuity. If an existing thread is on the wrong account (for example, older pre-arrival emails sent from `primary` to a guest), start a fresh email from the correct account and say so in your report. Guests should only ever see one address from the hotel, and replies must land in the inbox the team watches for them.

**Ask the operator** which account to use when the recipient fits more than one row (a supplier who has also stayed, a travel agent booking for a guest) or when you cannot tell who they are from the thread. Do not guess.

## Process

### 1. Determine the action

- **Reply**: responding to an existing email. Needs the original message's `message_id` and `thread_id`.
- **Forward**: sending an existing email to a new recipient.
- **Compose**: a new email with no thread.

For a reply or forward, read the original message first with `{{EMAIL_CLI}}`. If you cannot find it, or more than one message matches what the operator described, ask which one they mean.

### 2. Settle the recipients

- Reply to the sender. Use reply-all only when the operator asks for it or the thread clearly needs everyone on it, and list who is on To and Cc in your report.
- Never add a recipient the operator did not name. Never take an address from memory or make one up: use the address on the thread or the one the operator gives you.
- Before forwarding a guest's email to a third party, check what it contains. If it includes payment details, ID documents or anything else the recipient does not need, say so and ask before drafting.

### 3. Write the content

- Write only what the operator told you, what the thread says, or what a source you actually read says. Never invent prices, availability, dates, policies, booking details, provider names or promises.
- If a fact is missing, do not fill the gap with something plausible. Leave a visible marker such as `[CONFIRM: check-in time]` in the draft and list it under "Needs your input" in the report. A draft with an open marker is safer than a confident wrong answer the operator may send without noticing.
- Match the language and tone of the thread. Keep it short.

### 4. Show it, then create the draft

Show the operator the full text in chat first (account, recipients, subject, body). Create the draft in the mailbox once they are happy with it. Revising in chat first avoids leaving several half-right drafts in the mailbox, where the wrong one can be sent by mistake.

**Always use HTML (`text/html`), never plain text.** Plain text loses the formatting in most mail clients.

Replies, with the threaded-reply helper:

```bash
{{DRAFT_REPLY_TOOL}} --account {account} --message-id {message_id} --body '{html_body}' --html
```

New emails and forwards, with the new-email helper:

```bash
{{DRAFT_NEW_TOOL}} --account {account} --to {recipient} --subject '{subject}' --body '{html_body}' --html
```

If there is no helper for the job, create the draft with the email CLI directly:

```bash
{{EMAIL_CLI}} {account} drafts-create --json '{draft_json}'
```

These are example invocations. Use the flags your own helper or CLI really accepts; check its `--help` if unsure. Quote the body safely for the shell: an apostrophe inside a single-quoted argument ends the argument, so escape it or pass the body through a file if the helper supports that.

Only ever call a command that creates or updates a draft. Never call a send command, even if the CLI has one and even if the operator says "send it": tell them the draft is ready and that sending is their click.

### 5. HTML formatting rules

- Wrap paragraphs in `<p>` tags
- Use `<br>` for line breaks within a block
- Use `<ul>`/`<li>` for bullet points
- Use `<hr>` for section dividers
- Use `<blockquote>` for quoted or forwarded text
- Use `<strong>` for the header labels (From, To, Date, Subject) in forwarded chains
- Escape `&`, `<` and `>` that are part of the text itself
- For forwarded email chains, use grey left-border styling:
  ```html
  <div style="margin-left: 10px; padding-left: 10px; border-left: 2px solid #ccc;">
  ```

### 6. Forward format

When forwarding, put a short note from the operator on top, then the standard forward header, then the original message:

```html
<hr>
<p><strong>---------- Forwarded message ----------</strong><br>
<strong>From:</strong> {from}<br>
<strong>Date:</strong> {date}<br>
<strong>Subject:</strong> {subject}<br>
<strong>To:</strong> {to}</p>
```

Attachments on the original are only carried over if your helper supports it. If it does not, say in the report that the attachments are missing so the operator can add them.

### 7. Threading

- Replies: include `threadId` in the draft message, and set the `In-Reply-To` and `References` headers.
- Forwards: a new thread (no `threadId`), unless forwarding inside an existing conversation.
- A fresh email started because of the routing rule: a new thread on the correct account. Do not reuse the old `threadId`.

### 8. Sign-off

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

## When to stop

- **The helper or CLI fails** (missing file, auth error, non-zero exit): stop and show the operator the exact error. Do not retry with a different tool, a different account or a send command.
- **The original message cannot be found**, or the thread is ambiguous: ask.
- **The account is unclear**: ask (see the routing rule).
- **The request needs a fact you do not have**: draft with a `[CONFIRM: ...]` marker, or ask first if the whole email depends on it.

## Report

After each draft, report in this shape:

```
Draft created (not sent)
Action:   reply | forward | new
Account:  {alias} ({address})
To / Cc:  {recipients}
Subject:  {subject}
Draft ID: {id returned by the tool, if any}

{the full body as it will be sent}

Needs your input: {open [CONFIRM] markers, missing attachments, routing changes; or "nothing"}
```

## Guardrails

- **Drafts only.** Never send, schedule a send, or delete mail.
- **HTML only.** Never plain text.
- **No invented facts**, addresses or recipients.
- **Routing beats thread continuity.**
- Never put API keys, tokens or other credentials in an email, and never print them in chat.
