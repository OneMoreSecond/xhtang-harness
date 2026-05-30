---
name: decision-question-context
description: 'Use when asking clarifying questions, open questions, design questions, or decision questions. Brief current state, number each question, explain option effects, and provide concrete decision context before asking.'
argument-hint: 'Decision topic, known state, available options, effects, risks, and recommended default if known.'
---

# Decision Question Context

## Outcome

Ask questions that are easy to answer because the decision context is already visible.

## When To Use

Use this skill before asking the user to choose between designs, clarify a requirement, answer open questions, or resolve a blocker.

## Procedure

1. State current context first.

   Include the known facts, current implementation state, and why a decision is needed. Keep it brief, but concrete enough that the user can decide without reconstructing your research.

2. Number every question.

   Use stable numbering when questions are being reviewed across turns. If some previous questions are resolved, keep their number and mark the decision instead of silently renumbering in a confusing way.

3. For each question, include decision effects.

   Prefer this structure:

   ```markdown
   1. <question>
      Current state: <what is true now>
      Option A: <choice>. Effect: <behavior, risk, or implementation impact>
      Option B: <choice>. Effect: <behavior, risk, or implementation impact>
      Recommended default: <optional, only when evidence supports it>
   ```

4. Ask only for real missing decisions.

   If research or user feedback already determines the answer, record it as a decision instead of asking again.

5. Keep questions short, but not context-free.

   Avoid asking a bare question like "Should we support X?". Explain when X occurs, what the system does now, and what changes under each answer.

## Completion Check

Before sending the question, verify:

- The user can see the current state.
- Each option has a concrete effect.
- Questions are numbered.
- Already-decided items are marked as decisions, not reopened.
- The recommended default is labeled as a recommendation, not hidden as fact.
