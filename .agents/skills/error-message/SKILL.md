---
name: error-message
description: 'Write, review, or improve user-facing error messages. Use when drafting validation errors, empty/error states, toast/banner/modal errors, API failure copy, fallback messages, or product guidance for error handling.'
argument-hint: 'What error message or flow should be improved?'
user-invocable: true
---

# Error Message

Use this skill to write error messages that help users understand what happened, what was affected, and what to do next.

## Source Principle

Based on Jenni Nadler's Wix UX article, good error messages:
- Explain what happened and, when known, why.
- Reassure users about what was not affected.
- Avoid blame, shame, technical jargon, and cute tone.
- Help users fix the issue with a clear next action.
- Give a way out when the user cannot fix it.
- Treat repeated generic errors as product or engineering work, not only copy work.

## Required Inputs

Collect or infer these before writing:

- User action: what the user was trying to do.
- Failure cause: what actually failed, and whether the cause is known.
- Impact: what changed, what did not change, and whether user data is safe.
- Recovery: what the user can do now.
- Escape path: support, retry, back, save draft, contact admin, or later review.
- Surface and space: inline validation, toast, banner, modal, page state, log, or API response.

If cause, impact, or recovery is unknown, say that explicitly and ask for the missing implementation or product detail when it matters.

## Writing Workflow

1. Identify the user's goal and the failed operation.
2. Replace vague phrasing like "Something went wrong" with the most specific truthful statement available.
3. State impact before instructions when the user may worry about data loss.
4. Choose tone based on severity: calm for normal failures, direct for blocking failures, never playful for high-stakes issues.
5. Write one primary action. Add a secondary escape path only when useful.
6. Review whether the message blames the user, vendor, network, or system unnecessarily.
7. If the same generic message covers multiple causes, recommend mapping the trigger paths before finalizing copy.

## Message Pattern

Use this order when space allows:

```text
<What happened>. <Impact or reassurance>. <What to do next>.
```

Examples:

- "We couldn't publish your site because the payment method was declined. Your changes are saved as a draft. Update your payment method and try again."
- "We couldn't connect to the calendar service. Your existing bookings were not changed. Try reconnecting your calendar."
- "This file is too large to upload. Choose a file under 10 MB."

For tight UI surfaces:

- Inline validation: "Enter a valid email address."
- Toast: "Couldn't save changes. Try again."
- Button or link: "Retry", "Reconnect", "Contact support", "Learn how to fix this"

## Review Checklist

- Specific: Does it say what happened instead of only saying an error occurred?
- Honest: Does it avoid inventing a cause when the system does not know?
- Useful: Does it tell the user what to do next?
- Reassuring: Does it state what is safe or unchanged when relevant?
- Respectful: Does it avoid blame, shame, jokes, and panic language?
- Plain: Does it remove internal terms, stack traces, status codes, and implementation details unless the audience needs them?
- Accountable: Does it avoid blaming third parties when "we're having trouble connecting" is enough?
- Complete: If the user cannot fix it, does it provide a way out?

## When Copy Is Not Enough

Do not only rewrite the sentence when the product needs more information. Recommend engineering or product work when:

- The message is generic because multiple failure paths share one catch-all handler.
- The system knows the cause but does not expose it to the UI.
- The user needs state preservation, retry behavior, support diagnostics, or recovery links.
- The error is frequent or blocks a core flow.
- A newly launched feature still uses temporary fallback errors.

In those cases, propose mapping trigger paths, logging error reason codes, prioritizing by frequency and blocked flows, and reviewing real errors after launch.
