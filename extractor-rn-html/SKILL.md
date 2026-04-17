---
name: extractor-rn-html
description: Use only when the user sends `extractor-rn-html <link>`. This skill handles the X11/Xephyr GUI Chrome flow that opens the link, expands comments and replies, exports expanded HTML, runs the bundled Ollama-compatible analysis, then runs image recognition on the extractor output and writes results into `manifest.json` and `REPORT.md`. Do not trigger for screenshot-only parsing, curl/headless scraping, or ordinary coding work.
---

# Chrome HTML Extractor (X11)

Use this skill for tasks like:

- "extractor-rn-html https://example.com/post/123"

## Rules

- `extractor-rn-html` is an independent skill. Do not treat it as depending on `chrome-extractor-rn`.
- Keep the current X11/Xephyr framework. Do not rewrite the flow into screenshots, curl scraping, CDP scraping, or a headless browser pipeline.
- Keep the local GUI Chrome workflow and preserve the existing comment expansion logic, including visible `展开 n 条回复` actions and comment-panel scrolling.
- The main extractor is `scripts/extractor_x11.py`. The post-analysis image recognizer is `scripts/analyse_x11.py`.
- After comments and replies are expanded as far as the page allows, export the current page HTML and use that HTML as the primary analysis input.
- `scripts/extractor_x11.py` should export HTML, split and clean it for model analysis, extract `title`、`正文`、`评论`、`互动数据`、`图片`、`视频`, download note images, and write `manifest.json` plus `REPORT.md`.
- After `scripts/extractor_x11.py` finishes successfully, run `scripts/analyse_x11.py` automatically on the same output directory and write `图片识别` back into each `manifest.json`.
- If no reusable session exists, `scripts/extractor_x11.py` should start a new Xephyr session, open Chrome for manual login, then stop. At that point the assistant must end the current flow immediately, tell the user to log in manually, and tell the user that they need to send a new `extractor-rn-html <link>` request after login. Do not continue in the background, and do not treat it as the current session's rerun.
- Both scripts must use an Ollama-compatible chat endpoint; allow model name, base URL, API path, and timeout overrides from user arguments.
- Default to `gemma4:26b` for HTML parsing in `extractor_x11.py`, and `qwen3-vl:8b` for image recognition in `analyse_x11.py`, unless the user specifies other compatible values.
- Treat image and video extraction as model-side analysis from the expanded HTML and downloaded media, not screenshot OCR.
- For videos, only recognize the visible cover, poster, or current frame that is actually available to the model input. Do not infer unseen content.
- `title`、`正文`、`评论`、`互动数据` must stay close to the source content. Do not rewrite them into polished prose.
- `互动数据` should be formatted as `点赞: xx, 收藏: xx, 评论: xx, 分享：xx`.
- Emojis in text and comments should be output as `![emoji](emoji_url)` if possible (often found with `class="xxx-emoji"` tags).
- `评论` should be formatted as markdown blocks for each parent-comment, for example:

```markdown
- x:msg
    - ...可能多条
    - 可能 xx(作者):msg
    - ...可能多条
```

## Quick Workflow

1. Confirm the user input is `extractor-rn-html <link>`.
2. Run `scripts/extractor_x11.py`.
3. If the script reports no reusable session and opens a fresh login session, stop there, tell the user to finish login manually, and end the current model flow. The next extraction must come from a new user message `extractor-rn-html <link>`, not from a background rerun in the current session.
4. If a reusable session exists, let the extractor open the link, expand visible comments and replies, export the expanded page HTML, and write parsed fields plus downloaded images into each `item_n/manifest.json`.
5. Immediately run `scripts/analyse_x11.py` on that same output directory and write `图片识别` into each manifest.
6. Return the final output directory containing refreshed manifests and `REPORT.md`.

## Execution Notes

- Prefer the bundled implementation under `extractor-rn-html/`.
- When the user supplies a model or endpoint override, pass it through to the bundled implementation instead of hardcoding defaults in the prompt.
- The current Linux X11 flow starts with:

```bash
python3 extractor-rn-html/scripts/extractor_x11.py '<url1>' '<url2>'
```

- After extraction succeeds, run image analysis on the same output directory:

```bash
python3 extractor-rn-html/scripts/analyse_x11.py --out-dir <extractor_output_dir>
```

- Common overrides:
  `--ollama-base-url <url>`
  `--ollama-api-path <path>`
  `--ollama-model <model>`
  `--ollama-timeout <seconds>`
  `--xephyr-session <session_name>`
  `--image-limit <n>`
  `--video-limit <n>`
  `--wait-seconds <seconds>`
  `--skip-comment-scroll`

## Output

- `item_n/expanded_page.html`: expanded HTML exported from the current Chrome page.
- `item_n/expanded_page_analyse.html`: cleaned HTML chunk source written before model analysis.
- `item_n/images/`: downloaded note images referenced by the parsed result.
- `item_n/manifest.json`: capture metadata plus parsed `title`、`正文`、`评论`、`互动数据`、`图片`、`视频`; after `analyse_x11.py`, it also contains `图片识别`.
- `REPORT.md`: merged report generated from the parsed manifests.
