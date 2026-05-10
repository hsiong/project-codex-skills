---
name: github-issue-generator
description: "当用户要基于当前 Git 修改生成一个或多个 GitHub issue 草稿时触发，例如“根据这次改动写 issue”“先查重再按 diff 总结 issue”“把当前修改整理成 GitHub issue 文件”。它负责读取对应 git diff、按改动拆分 issue、联网查重，并在 `file/issue/` 下生成英文 Markdown 草稿；不用于审查现有代码问题、规划新功能或默认提交远程 issue。"
---

# GitHub Issue Generator

## 适用场景

- 用户要你根据当前仓库的 Git 修改撰写 issue。
- 用户要求先检查是否已有类似 issue，再根据 diff 决定是否新建。
- 用户要求 issue 内容遵循仓库模板、使用英文、生成 Markdown 文件。

## 强约束

- issue 内容必须来自对应的 Git 修改：优先读取 staged diff；若没有 staged diff，再读取 unstaged diff；必要时结合最近一次 commit diff。
- 不要把任务理解为“检查现有代码有什么问题并提出 issue”。
- 不要为了寻找 issue 候选去扫描或审查整个代码库；只能根据用户指定范围或已获取的 diff 总结 issue。
- 不要脱离 diff 额外扩展需求、架构建议或代码审查结论。
- 先查重，后起草。只要仓库可访问，就必须先联网检查现有 issues。
- 若已有明显相似 issue，默认不重复起草，直接返回已有 issue 链接、相似点和差异点。
- 优先遵循仓库自己的 `.github/ISSUE_TEMPLATE`、issue forms 或模板约束。
- 如果仓库没有模板，再使用通用结构起草，标题前缀按类型选择：`Bug:`、`Feature:`、`Refactor:`、`Docs:`、`Question:`。
- 输出语言必须是英文。
- 输出格式必须是 Markdown。
- 默认将草稿写入当前仓库的 `file/issue/` 目录，每个 issue 一个 `.md` 文件，不直接调用 GitHub API 或网页操作去提交 issue，除非用户明确要求。
- 一批改动可能对应多个 issue。必须先按相对独立的问题、功能、模块或行为变化拆分，再分别查重和起草；不要强行合并成一个大 issue。
- 由该 skill 新生成的 `file/issue/*.md` 文件不要自动执行 `git add`。

## 工作流

1. 获取对应的 Git 修改：
   - 先运行 `git status --short` 确认修改范围。
   - 优先读取 `git diff --cached`。
   - 如果 staged diff 为空，读取 `git diff`。
   - 如果用户明确指定 commit、branch、PR 或文件范围，只读取对应范围的 diff。
   - 如果工作区没有可用 diff，先告诉用户缺少 Git 修改上下文，不要根据现有代码自行生成 issue。
   - 获取 diff 之前，不要先做代码审查、架构分析或问题扫描。

2. 从 diff 中提炼 issue 所需上下文：
   - 目标仓库
   - 本次修改暴露或修复的问题、需求目标
   - 影响范围
   - 行为变化、相关模块、可从 diff 推断的复现信息
   - 无法从 diff 判断的关键信息用简短 `TODO` 占位

3. 拆分 issue 候选：
   - 按独立的问题、功能、模块或行为变化拆分候选 issue。
   - 如果多个改动共享同一个用户可感知问题或同一个交付目标，可以合并为一个候选。
   - 如果一批 diff 明显包含多个互不依赖的问题或需求，必须生成多个候选。
   - 对每个候选记录对应的 diff 依据，避免把无关改动写进同一个 issue。

4. 联网查重：
   - 优先搜索目标仓库的 GitHub issues。
   - 每个候选 issue 分别查重。
   - 关键词基于候选相关 diff 中的报错信息、核心行为、模块名、特性名组合。
   - 若仓库启用了 discussions，必要时一并检查是否已有同类讨论。

5. 判断是否重复：
   - 若已有高度相似 issue，返回：
     - 相似 issue 链接
     - 相似原因
     - 当前问题与已有 issue 的差异
   - 除非用户要求仍然新建，否则不再继续起草新 issue。
   - 对已判定重复的候选，不生成对应 `file/issue/*.md` 草稿。

6. 读取本地仓库模板：
   - 优先检查 `.github/ISSUE_TEMPLATE/` 下的 `.md`、`.yml`、`.yaml` 模板。
   - 若存在 issue form，按字段语义转写为 Markdown 草稿。
   - 若存在多个模板，选择与当前类型最匹配的模板。

7. 生成 issue 草稿文件：
   - 保留模板要求的标题、复选框、段落结构和字段语义。
   - 信息不足时，优先根据 diff 合理补全。
   - 若关键事实缺失且无法安全推断，使用简短占位符，例如 `TODO: add reproduction details`。
   - 确保 `file/issue/` 目录存在。
   - 每个非重复候选生成一个独立 Markdown 文件，命名为 `file/issue/<type>-<short-kebab-title>.md`；如同类型同标题冲突，追加 `-2`、`-3`。
   - 文件内容应是可直接复制到 GitHub 的 issue 正文；标题可作为文件内第一行 `# Title`。
   - 生成后不要运行 `git add` 暂存 issue 草稿文件，除非用户明确要求。

## 默认输出结构

若仓库无模板，可按下列结构生成：

```markdown
# Title

## Summary

## Steps to Reproduce

## Expected Behavior

## Actual Behavior

## Environment

## Additional Context
```

特性类 issue 可改为：

```markdown
# Title

## Summary

## Problem

## Proposed Change

## Alternatives Considered

## Additional Context
```

## 文件与输出要求

- 默认不要把完整 issue 正文全部输出到对话里；应生成到 `file/issue/*.md`。
- 最终回复只列出生成的文件路径、对应 issue 标题，以及跳过生成的相似 issue 链接。
- 如果发现相似 issue，优先输出“已有相似 issue”结论和链接列表。
- 如果起草新 issue，文件内容应可直接复制到 GitHub。
- issue 文件内容不要输出中文解释，不要附加多余操作说明，除非用户额外要求。
- 输出不要带行号
