增加一下功能: - 不要把任务理解为“检查现有代码有什么问题并提出 issue”。
- 输出语言必须是英文。
- 先查重，后起草。只要仓库可访问，就必须先联网检查现有 issues。
- 若已有明显相似 issue，默认不重复起草，直接返回已有 issue 链接、相似点和差异点。
- 优先遵循仓库自己的 `.github/ISSUE_TEMPLATE`、issue forms 或模板约束。
- 默认将草稿写入当前仓库的 `file/issue/` 目录，每个 issue 一个 `.md` 文件
- 如果用户明确要求, 直接调用 `scripts/submit_issues.sh` 去提交issue，
