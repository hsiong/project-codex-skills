# README Visual Playbook

Use visuals to demonstrate a claim that text cannot prove as quickly. Every image should answer a specific visitor question.

## 1. Inventory before capture

Search the repository for existing images, recordings, diagrams, demo fixtures, seeded accounts, storybooks, and end-to-end tests. Verify that reused assets still match the current product.

Useful discovery commands:

```bash
rg --files | rg '\.(png|jpe?g|webp|gif|svg|mp4|webm)$'
rg -n 'storybook|playwright|cypress|fixture|seed|demo' .
```

## 2. Make a capture plan

For each proposed visual, define:

| Field | Question |
| --- | --- |
| Claim | What statement will this prove? |
| Surface | Which page, command, result, or diagram contains the proof? |
| State | What safe data and interaction state make it understandable? |
| Format | Screenshot, recording, terminal block, chart, SVG, or Mermaid? |
| Placement | Where does the reader need this proof? |

Prefer one strong hero plus two to four focused proof visuals. Use more only when distinct workflows genuinely need them.

## 3. Capture a web product

Start the application using its documented package manager and lockfile. Use deterministic fixtures or demo data, remove tokens and personal information, and wait until fonts, charts, and asynchronous content are stable.

When no browser capture tool is available, create a JSON file and run the bundled script:

```json
{
  "base_url": "http://127.0.0.1:3000",
  "output_dir": "docs/images/readme",
  "defaults": {
    "viewport": {"width": 1440, "height": 900},
    "color_scheme": "dark",
    "wait_ms": 500
  },
  "shots": [
    {
      "name": "overview.png",
      "path": "/dashboard?demo=1",
      "wait_for": "[data-ready='true']",
      "hide": ["[data-private]", ".dev-toolbar"]
    },
    {
      "name": "workflow.png",
      "path": "/workflows/example",
      "selector": "main"
    }
  ]
}
```

```bash
python /path/to/readme-optimizer/scripts/capture_readme.py readme-captures.json
```

The script requires Python Playwright and Chromium. If missing, install them in an isolated environment as directed by its error message. Keep the capture config when it gives maintainers a reproducible update path; otherwise remove it after producing the assets.

Use a consistent viewport and color scheme across a series. Capture a mobile viewport only when responsive behavior is part of the value. Crop to the meaningful surface, avoid mouse cursors and transient toasts, and never stage functionality the application does not implement.

## 4. Choose non-UI evidence

- CLI: use a short real terminal transcript in a code block; use a recording only when interaction or progress is important.
- Library/API: show the smallest input and returned or rendered result together.
- Performance project: produce a labeled chart or table from checked-in benchmark data and state the environment.
- Model/research project: show representative output, comparison, architecture, or evaluation with provenance.
- Infrastructure: use a diagram for relationships and a screenshot for operational experience; do not make one substitute for the other.

Prefer Mermaid for simple GitHub-native flows and SVG for controlled diagrams. Derive nodes and edges from verified repository behavior.

## 5. Prepare and embed assets

- Use stable repository-relative paths and descriptive lowercase filenames.
- Prefer PNG for sharp UI/text, WebP for smaller rich images, SVG for diagrams, and a short optimized GIF/WebM only when motion carries information.
- Avoid oversized canvases and assets that take longer to load than the surrounding README. Optimize a copy rather than degrading the source asset.
- Write alt text that conveys the demonstrated state, not `screenshot`. Add a short caption when the takeaway is not obvious.
- Use a `<picture>` element only when separate light and dark assets materially improve readability.

After embedding, open the rendered Markdown or inspect it in a GitHub-compatible preview. Verify local paths, dimensions, readability, and layout in both narrow and wide views.
