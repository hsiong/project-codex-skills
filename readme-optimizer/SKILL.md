---
name: readme-optimizer
description: Create or overhaul repository README files as high-signal GitHub landing pages, including evidence-based positioning, project-specific information architecture, quick-start content, and real screenshots or diagrams. Use for requests like "rewrite the README," "make this look like a top GitHub project," "add screenshots to the README," or "show the project's value." Do not use for generic prose polishing, code review, implementation planning, or documentation pages unrelated to a repository README.
---

# README Optimizer

Turn a repository's real product experience into a README that helps a new visitor understand it, trust it, and try it quickly. Treat the README as a decision page, not a source-code report or a fixed essay template.

## Workflow

### 1. Establish the facts

- Read the current README, manifests, release metadata, user-facing entry points, CLI help, examples, tests, docs, and runnable demos. Inspect deeper implementation only to verify externally meaningful claims.
- Preserve applicable license, security, attribution, compatibility, and contribution information.
- Identify the primary audience, their first desired outcome, the shortest successful path, the project's maturity, and its strongest defensible proof.
- Build a private evidence map from each proposed claim to code, tests, docs, a reproducible run, or measured data. Remove unsupported superlatives and invented use cases.

### 2. Choose the story for this project

- Classify the project as a visual product, CLI/developer tool, library/API, model/research project, infrastructure/platform, agent/skill, or a justified hybrid.
- Read [references/readme-patterns.md](references/readme-patterns.md), then select only the modules that help this project's audience decide or act.
- Distill one precise promise and three to six differentiators. Lead with user-visible outcomes and proof; explain internals only when they establish trust or clarify a real design advantage.

### 3. Produce visual proof

- Read [references/visual-playbook.md](references/visual-playbook.md) and inventory existing visual assets before creating new ones.
- For a runnable visual product, launch it with safe demo data and capture the smallest set of real states that proves the core experience. Use an available browser tool or [scripts/capture_readme.py](scripts/capture_readme.py).
- For a CLI, library, model, or infrastructure project, prefer the visual evidence that best fits the claim: a terminal transcript, rendered result, benchmark chart, architecture diagram, model table, or workflow trace.
- Never fabricate a product screenshot. Generated artwork may serve as clearly decorative branding, but not as evidence of implemented behavior. If the project cannot be run, reuse verified assets or create a fact-based diagram and report the missing capture rather than disguising it.
- Store durable assets under the repository's existing documentation convention, or `docs/images/readme/` when none exists. Use descriptive names, useful alt text, and captions that state what the image proves.

### 4. Write in decision order

Build the opening viewport from the strongest available elements:

1. Recognizable project name or restrained brand asset.
2. A one-sentence promise naming the product, audience or task, and meaningful advantage.
3. A few relevant trust links or badges.
4. A primary action such as Try, Install, View demo, or Read docs.
5. Immediate proof: a real screenshot, short terminal session, output example, or benchmark.

After the opening, arrange project-specific modules such as highlights, quick start, examples, performance, architecture, compatibility, configuration, limitations, roadmap/status, support, contributing, citation, and license. Put the first successful run early, move exhaustive reference material into linked docs, and keep each section centered on one reader question.

Use the repository's audience language. Keep commands copyable, examples concrete, headings scannable, and claims proportional to evidence. Do not turn internal class names, file inventories, or every implemented feature into the story.

### 5. Implement and verify

- Update the README and every asset or local link changed by the new narrative. Keep localized README variants consistent when the repository treats them as maintained equivalents; otherwise state which variants now need translation.
- Run the documented quick start or the smallest safe validation that verifies it. Check image paths, anchor links, code fences, alt text, dark/light rendering where relevant, and GitHub-compatible markup.
- Review the rendered reading order and `git diff`. Remove duplicated claims, decorative clutter, stale instructions, and sections that delay the first useful action.
- Finish with a concise summary of the narrative, created or reused visuals, checks run, and any claim or screenshot that could not be verified.
