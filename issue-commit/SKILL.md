---
name: issue-commit
description: "当用户输入包含 issue 标题和编号的内容时触发，例如“issue commit: #25 ...”。它负责解析 issue 信息、将对应改动直接推送到远程 `fix/issue_code` 分支，且完全不创建本地分支；不用于普通无 issue 关联的提交或处理未跟踪文件。"
---

# Issue Commit

## 适用场景

- 用户提供了一个或多个 issue 的详细信息（如从 GitHub 复制的列表），要求按 issue 提交代码。
- 需要将改动直接推送到远程的 `fix/issue_code` 分支，但**完全不需要**在本地创建任何新分支。
- 提交信息需要符合 `Closes:(#issue_code)issue_title` 格式。

## 核心流程

1. **信息解析**：从输入文本中提取每个 issue 的编号（如 #25）和标题。
2. **输入校验**：如果用户只输入了 "issue commit:" 而没有后续内容，提示用户补充信息。
3. **改动分析**：获取当前工作区所有已跟踪文件的改动。
4. **改动映射**：将每个改动的文件映射到最相关的 issue。
5. **按 Issue 直接推送（不留痕迹）**：
   - 针对每个 issue 及其映射的文件，执行以下原子操作：
     - **提交**：`git commit -m "Closes:(#issue_code)issue_title" <文件列表>`。
     - **推送**：`git push origin HEAD:fix/issue_code`（将当前分支的最顶端提交推送到远程目标分支）。
     - **回滚**：`git reset --soft HEAD~1`（本地撤销该提交，保留改动。这确保了本地不产生额外的 commit 记录，且不改变分支结构）。
6. **汇总**：列出已成功推送到远程的 issue 分支及其对应的文件清单。

## 强约束

- **零本地分支**：严禁使用 `git checkout -b` 或 `git branch` 创建新分支。
- **直接推送远程**：通过 `HEAD:remote_branch` 语法直接更新远程引用。
- **提交格式**：Message 必须严格遵守 `Closes:(#issue_code)issue_title`。
- **本地状态保持**：推送完成后，通过 `git reset --soft` 确保本地工作区改动依然存在（或处于 staged 状态），不污染本地提交历史。
- **作用范围**：仅处理已跟踪的文件。严禁访问或添加未跟踪文件。
- **TODO 检查**：如果变更代码中包含 `todo`，必须提醒用户并终止提交。
- **禁区路径**：禁止提交 `.idea/`、`.env`、`application.yml` 等敏感或配置目录。
- **输入缺失**：如果用户未提供 issue 内容，停止执行并提示：“请先输入 issue 标题和编号信息”。

