---
name: query-stress-test
description: Generate codebase-specific evaluation queries that stress retrieval and reduce repetitive grep/search calls.
---

# Query Stress Test

Use this skill when you need to evaluate whether a RAG pipeline saves tokens and time by providing useful context before an agent starts searching the repo.

## Goal

Generate questions that are hard to answer from one file, likely to require:

- multiple source files
- call-chain tracing
- config discovery
- dependency tracing
- architectural understanding

## Output

Return a list of concrete test queries only.

## Good query types

- Where is X implemented?
- How does X flow through the system?
- What uses Y?
- What breaks if Z changes?
- How is behavior configured?
- What are the main entry points?

## Constraints

- Prefer realistic developer questions.
- Avoid trivia or one-file questions.
- Avoid vague prompts that cannot be scored.
- Bias toward questions that would otherwise trigger repeated grep/search calls.
- Include both feature-level and architecture-level prompts.

## Evaluation focus

Favor queries that would likely benefit from retrieval context because they require:

- cross-file linking
- repeated symbol lookup
- understanding of data flow
- reading of tests and implementation together

