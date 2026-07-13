---
name: backend-project-validator
description: "Run a backend project and validate it against design documents, then fix confirmed implementation, data, rate-limit, or algorithm issues. Use for requests such as 'check project', 'audit project'. Do not use for code-style-only reviews, frontend work, or reviews that must not modify files."
---

# Backend Project Validator

## Inputs

```
check project:
+ design: <design-directory>
+ project: <project-path>
```

- Design directory: user-provided.If no design directory is provided, ask user.
- Project path: default to `code`. If `code` does not exist, ask user.
- Runtime environment: default to `<project-path>/.venv`.

## Workflow

1. Read every relevant design document and turn its claims into verifiable checks.
2. Inspect the project structure, dependency files, entry points, tests, and configuration. Read `<project-path>/.env.dev` when needed, but never echo or expose secrets.
3. Run the real project with its virtual environment. Exercise representative workflows with realistic data and record commands, failures, and observable results.
4. Compare behavior with the design. Identify design defects, placeholder or unreachable implementations, invalid data, external rate limits, and misleading results. Distinguish project defects from unavailable external services.
5. Audit cross-validation and technical algorithms closely:
   - Confirm that the algorithm matches the task, dataset size, target, and evaluation objective.
   - Check split strategy, leakage, grouping, temporal ordering, class balance, preprocessing scope, random seeds, baselines, metrics, parameter ranges, and uncertainty.
   - Recompute or reproduce reported results where practical; reject conclusions unsupported by held-out evidence.
   - Prefer the smallest defensible algorithm or parameter change and explain its tradeoff.
6. Modify all affected code, configuration, tests, and design content together when a confirmed issue prevents the project from meeting its stated design.
7. Rerun focused tests and the real workflow. Report remaining external limits or unverifiable assumptions with evidence.

Do not replace execution with pseudocode or claim success from static inspection alone. Preserve existing unrelated changes and avoid destructive operations.
