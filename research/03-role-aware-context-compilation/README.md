# Role-Aware Context Compilation

This is the higher-risk discovery track: compile agent context into storage and inference roles before it becomes one flat prompt.

## Research Question

Can agent context be compiled into role-tagged spans that guide restore, recompute, fallback, and quality checks better than naive prefix caching?

## Contrarian Assumption

Most cache systems treat recompute as waste. This track treats selective recompute as a possible quality repair tool.

## Context Roles To Explore

- immutable system/developer rules
- tool schemas
- repo facts
- memory summaries
- reasoning anchors
- task instructions
- volatile tool output
- discardable logs
- answer constraints

## Core Hypotheses

H1: Some spans are cheap to recompute but disproportionately important for quality.

H2: Role labels predict safe reuse better than token position alone.

H3: Recomputing small anchor spans can recover reasoning quality while preserving most cache savings.

H4: A role-aware planner can decide between restore, recompute, visible-prefix replay, and full fallback.

## Smallest Useful Test

Take a failed reasoning-over-prefix case from track 01 and compare:

1. full prompt
2. session-tail
3. session-tail plus visible task constraints
4. restored prefix plus recomputed reasoning anchors
5. full fallback

Measure pass/fail, prompt time, restored bytes, and failure class.

## Success Shape

A good result would show a mechanism: which context roles must be visible or recomputed for quality, and which can safely live as restored state.
