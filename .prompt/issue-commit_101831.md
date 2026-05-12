# Issue Commit Skill (v4)

## Purpose
Directly push specific file changes to remote issue branches without creating local branches or persistent commits.

## Trigger
Triggered by "issue commit:" followed by issue data.

## Requirements
1. **Parse Issue Info**: Extract `#issue_code` and `issue_title`.
2. **Analyze & Map**: Match changed files to extracted issues.
3. **Direct Remote Delivery (No Local Branching)**:
   - For each issue and its mapped files:
     - Execute: `git commit -m "Closes:(#issue_code)issue_title" <mapped_files>`
     - Execute: `git push origin HEAD:fix/issue_code`
     - Execute: `git reset --soft HEAD~1` (This returns the files to the staged/unstaged state, effectively "undoing" the commit locally while the remote remains updated).
4. **Final Summary**: State which remote branches were updated and with which files.

## Constraints
- **Zero local branches**: Never run `git checkout -b` or `git branch`.
- **Atomic Commits**: Each remote branch should receive exactly one commit with the correct `Closes:` format.
- **Workspace Preservation**: The local workspace should end up with the same "dirty" state (or slightly cleaner if staged) as before, but the work is safely pushed to remote.
- Only handle tracked files.
- Mandatory TODO check.
