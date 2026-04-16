---
name: extractor-rn-html
description: Use when the user sends `extractor-rn-html <link>` or asks to use v2 to open links in local GUI Chrome, expand comments and replies, export the fully expanded page HTML, and send that HTML plus media to an Ollama-compatible model endpoint to extract `title`、`正文`、`评论`、`互动数据`、图片和视频 into `manifest.json` and `REPORT.md`. Default to `qwen3.5 27b` unless the user provides another compatible model or endpoint. Do not trigger for screenshot-based parsing, curl/headless-browser scraping, or ordinary coding work.
---

# Chrome HTML Extractor (v2)

Use this skill for tasks like:

- "extractor-rn-html https://example.com/post/123"
- "用 v2 抓这个链接，评论全部展开后把 html 丢给 ollama 分析"
- "extractor-rn-html 这几个链接用 qwen3.5 27b 跑一下"

## Rules

- `extractor-rn-html` is an independent skill. Do not treat it as depending on `chrome-extractor-rn`.
- Keep the current v2 framework. Replace the parsing stage only; do not rewrite the whole flow into a different architecture.
- Keep the local GUI Chrome workflow and preserve the existing comment expansion logic, including visible `展开 n 条回复` actions and comment-panel scrolling.
- After comments and replies are expanded as far as the page allows, export the current page HTML and use that HTML as the primary analysis input.
- Do not switch the parsing stage to screenshots, `view_image`, hardcoded DOM extraction, `curl`, CDP scraping, or headless Chrome.
- Send the expanded HTML to an Ollama-compatible model endpoint to extract `title`、`正文`、`评论`、`互动数据`、图片和视频.
- Default to `gemma4:26b` (or `qwen3.5 27b` if preferred), but allow the model name and compatible endpoint address to follow user-provided arguments.
- Image recognition must also use the same Ollama-compatible protocol. Later endpoints may differ by base URL, but the request/response protocol stays Ollama-compatible.
- Treat image and video extraction as model-side analysis from the HTML/media references, not screenshot OCR.
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

1. Confirm the user provided one or more links, usually with the wake word `extractor-rn-html`.
2. Run the bundled v2 implementation for the current OS and desktop session. Keep the GUI Chrome opening and reply-expansion flow.
3. Expand visible comments and replies as fully as the current page allows.
4. Export the expanded page HTML for each item.
5. Send the HTML to the configured Ollama-compatible model endpoint and parse `title`、`正文`、`评论`、`互动数据`、图片和视频.
6. If media recognition is needed, send the media inputs to the configured compatible model instead of relying on screenshot reading.
7. Write the parsed fields back into each `item_n/manifest.json`.
8. Generate the final `REPORT.md` from the parsed manifests.

## Execution Notes

- Prefer the bundled implementation under `extractor-rn-html/` for platform-specific execution.
- When the user supplies a model or endpoint override, pass it through to the bundled implementation instead of hardcoding defaults in the prompt.
- The current Linux implementation is `python3 extractor-rn-html/scripts/extractor_rn_v2.py '<url1>' '<url2>'`.
- Common overrides:
  `--ollama-base-url <url>`
  `--ollama-api-path <path>`
  `--ollama-model <model>`
  `--ollama-timeout <seconds>`
  `--xephyr-session <session_name>`
  `--prepare-login`

## Output

- `item_n/expanded_page.html`: expanded HTML exported from the current Chrome page.
- `item_n/manifest.json`: capture metadata plus parsed `title`、`正文`、`评论`、`互动数据`、图片和视频.
- `REPORT.md`: merged report generated from the parsed manifests.
