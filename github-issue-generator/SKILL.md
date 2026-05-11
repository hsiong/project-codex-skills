---
name: github-issue-generator
description: "当用户要基于当前 Git 修改生成 GitHub issue 草稿时触发，例如“根据这次改动写 issue”“先查重再按 diff 总结 issue”“把当前修改整理成 GitHub issue 文件”“这些大改动拆成多个 issue”。它负责读取对应 git diff、优先把大批量或多主题修改拆成多个 issue、联网查重，并在 `file/issue/` 下生成英文 Markdown 草稿；不用于审查现有代码问题、规划新功能或默认提交远程 issue。"
---

# GitHub Issue Generator

## 适用场景

- 用户要你根据当前仓库的 Git 修改撰写 issue。
- 用户要求先检查是否已有类似 issue，再根据 diff 决定是否新建。
- 用户要求 issue 内容遵循仓库模板、使用英文、生成 Markdown 文件。

## 强约束

- issue 内容必须来自对应的 Git 修改。
- 不要把任务理解为“检查现有代码有什么问题并提出 issue”。
- 不要脱离 diff 额外扩展需求、架构建议或代码审查结论。
- 先查重，后起草。只要仓库可访问，就必须先联网检查现有 issues。
- 若已有明显相似 issue，默认不重复起草，直接返回已有 issue 链接、相似点和差异点。
- 优先遵循仓库自己的 `.github/ISSUE_TEMPLATE`、issue forms 或模板约束。
- 如果仓库没有模板，再使用通用结构起草，标题前缀按类型选择：`Bug:`、`Feature:`、`Refactor:`、`Docs:`、`Question:`。
- 输出语言必须是英文。
- 输出格式必须是 Markdown。
- 默认将草稿写入当前仓库的 `file/issue/` 目录，每个 issue 一个 `.md` 文件，不直接调用 GitHub API 或网页操作去提交
  issue，除非用户明确要求。
- 一批改动默认先按多个候选 issue 处理。必须先按相对独立的问题、功能、模块或行为变化拆分，再分别查重和起草；不要因为用户用了单数“issue”或
  diff 来自同一批修改就合并成一个大 issue。
- 拆分维度包括独立问题、模块、构建、工程拓扑、运行时归属、API 和行为语义，尽可能细。
- 一个 issue 如果同时包含 build、runtime、public API、docs、deploy 等多个维度，必须重新拆分，除非能逐项证明不可分。
- 如果最终只生成一个 issue，最终回复必须简短说明为什么所有改动属于同一个 issue。
- 由该 skill 新生成的 `file/issue/*.md` 文件不要自动执行 `git add`。

## Granularity Rules

Before drafting issues, classify each diff candidate by change dimension:

- build/project topology
- dependency or version management
- public API or annotation/contract semantics
- runtime configuration keys or environment contract
- module ownership or package relocation
- runtime bean/configuration ownership
- business behavior
- documentation
- deployment/operations
- tests

Each distinct dimension should become a separate issue by default.

Do not merge changes only because they support the same broad refactor goal. A shared direction such as "make the framework standalone", "clean up modules", or "modernize the project" is not
enough to merge candidates.

An issue must not mix multiple high-impact dimensions unless the changes are mechanically inseparable. If merged, the draft must explicitly explain why they cannot be split.


## 工作流

1. 获取对应的 Git 修改：
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
    - 先列出候选主题，再决定候选边界。
    - 对每个候选记录对应的 diff 依据。

4. 联网查重：
    - 优先搜索目标仓库的 GitHub issues。
    - 关键词基于候选相关 diff 中的报错信息、核心行为、模块名、特性名组合。
    - 若仓库启用了 discussions，必要时一并检查是否已有同类讨论。

5. 判断是否重复：
    - 对每个候选给出重复判断。
    - 对重复候选记录已有 issue 链接、相似原因和差异点。

6. 读取本地仓库模板：
    - 检查 `.github/ISSUE_TEMPLATE/` 下的 `.md`、`.yml`、`.yaml` 模板。
    - 若存在 issue form，按字段语义转写为 Markdown 草稿。
    - 若存在多个模板，选择与当前类型最匹配的模板。

7. 生成 issue 草稿文件：
    - 保留模板要求的标题、复选框、段落结构和字段语义。
    - 信息不足时，优先根据 diff 合理补全。
    - 若关键事实缺失且无法安全推断，使用简短占位符，例如 `TODO: add reproduction details`。
    - 确保 `file/issue/` 目录存在。
    - 每个非重复候选生成一个独立 Markdown 文件，命名为 `file/issue/<type>-<short-kebab-title>.md`；如同类型同标题冲突，追加
      `-2`、`-3`。
    - 文件内容应是可直接复制到 GitHub 的 issue 正文；标题可作为文件内第一行 `# Title`。

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
