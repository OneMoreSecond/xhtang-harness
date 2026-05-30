---
name: grill-me
description: 'Stress-test a plan, design, task, or proposal by asking critical decision questions until intent, scope, assumptions, tradeoffs, and next steps are clear. Use when the user asks to be grilled, requests a deep plan critique, or wants rigorous design review before implementation.'
argument-hint: 'Plan, design, proposal, task description, or decision you want critically examined.'
user-invocable: true
---

# Grill Me

## What This Skill Produces

This skill turns a vague or risky plan into a sharper decision tree. It should produce:

- A critical read of the user's intent, scope, assumptions, and risks.
- Focused questions that reveal missing decisions or weak reasoning.
- A record of resolved decisions as the conversation progresses.
- A stopping point where the plan is clear enough to execute, revise, or reject.

## When To Use

Use this skill when the user:

- Invokes `/grill-me`.
- Says "grill me", "stress-test this", "challenge this plan", or asks for a deep plan critique.
- Presents a design, task, strategy, document, or proposal that needs critical review before work starts.
- Needs ambiguity, over-engineering, missing requirements, or decision dependencies surfaced.

Do not use it for normal implementation work after the plan is already settled, unless the user explicitly asks for another critical pass.

## Required Inputs

Collect or infer these before drilling into details:

1. Subject: the plan, design, task, or proposal being examined.
2. Goal: what the user is trying to achieve and why it matters.
3. Context: relevant codebase, constraints, stakeholders, timeline, or failure modes.
4. Decision boundary: what can still change and what is already fixed.

If a missing fact can be found by inspecting the repo or supplied context, inspect it before asking the user.

## High-Level principles

Interview the user relentlessly about every aspect of this plan until a shared understanding is reached.
Aspect examples:

- What's the intent behind the task? Any other simple solution to achieve the same goal?
- Is the task description clear and complete? Any ambiguity or missing information?
- Is the task too heavy and is a overkill for the problem?

Raise questions in most critical way, especially for ambiguity points.
Walk down each branch of the design tree resolving dependencies between decisions one by one.

If a question can be answered by exploring the codebase, explore the codebase before asking.


## Core Workflow

1. Restate the current plan in concrete terms.

   Keep this short. Include the apparent goal, proposed approach, and any fixed constraints.

2. Identify the critical branches.

   Look for intent mismatch, simpler alternatives, unclear requirements, hidden dependencies, overkill, operational risk, data/model assumptions, ownership gaps, and validation gaps.

3. Maintain the question ledger.

   Keep two visible lists: unresolved questions and resolved questions. Each unresolved question should have a short reason why it matters. Each resolved question should include the chosen answer or decision.

4. Ask only the most important next question.

   Choose the single highest-priority unresolved question that blocks the most downstream work. If the ask-question tool is available, call it with only that one question. If the tool is not available, ask the same one question directly in the response.

5. Provide options when useful.

   For each option, explain the effect on scope, complexity, risk, behavior, or validation. Mark the recommended option clearly and follow the active question tool's required format when one is available.

6. Record resolved decisions.

   When the user answers, briefly state what is now decided and what remains open.

7. Stop when shared understanding is reached.

   End with a concise decision summary, remaining risks, and the next action. If the plan is not worth doing, say so directly and explain the simpler path.

## Question Ledger

Keep this structure visible during grilling:

```markdown
Unresolved questions:
- Q1: <question>. Why it matters: <scope/risk/dependency>.
- Q2: <question>. Why it matters: <scope/risk/dependency>.

Resolved questions:
- Q3: <question>. Decision: <answer>. Effect: <what this changes>.
```

Only the current highest-priority unresolved question should be asked through the ask-question tool. Do not send the whole ledger as multiple simultaneous tool questions unless the user explicitly asks for batch review.

## Question Style

- Be critical, not theatrical.
- Ask about why before how when intent is unclear.
- Challenge over-engineering and hidden scope.
- Distinguish facts, assumptions, opinions, and decisions.
- Do not ask questions already answered by code or supplied context.
- Avoid broad lists of speculative concerns; walk the decision tree in dependency order.
- Prefer concrete tradeoffs over abstract prompts.
- mark the recommended option with "(Recommended)".

Useful question themes:

- Intent: what user problem or engineering risk does this solve?
- Necessity: is the task needed, or is there a smaller path to the same outcome?
- Scope: what is explicitly in and out?
- Ambiguity: what input, behavior, owner, or success criterion is under-specified?
- Tradeoff: what does the chosen approach make easier or harder?
- Validation: how will we know the plan worked?
- Failure: what breaks if the assumption is wrong?

## Completion Checklist

- The goal and non-goals are explicit.
- Key assumptions are marked as facts, assumptions, or open questions.
- Major alternatives were considered, including simpler options.
- The plan's risk, cost, and validation path are clear.
- Open decisions are either answered or deliberately deferred.
- Resolved and unresolved questions are visible as lists.
- Only one active question is being asked at a time unless the user asks for batch review.
- The final summary says whether to proceed, revise, or stop.

## Example Requests

- `/grill-me I want to replace this job queue with a custom scheduler.`
- `/grill-me Stress-test this migration plan before I write the implementation doc.`
- `/grill-me Challenge the scope of this feature and tell me what I am missing.`
