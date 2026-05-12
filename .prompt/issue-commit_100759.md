# Issue Commit Skill (v3)

## Purpose
Commit specific files directly to **remote** issue branches without leaving local branches, based on provided issue details.

## Trigger
Triggered when the user says "issue commit:" followed by issue information.

## Requirements
1. **Parse Issue Info**: Extract `#issue_code` and `issue_title`.
2. **Verify Input**: If empty after colon, ask for content.
3. **Analyze & Map**: Map changed files to issues.
4. **Per Issue Execution (Clean Flow)**:
   - Create a **temporary** local branch (e.g., `temp_fix_code`).
   - Stage mapped files.
   - Commit with message: `Closes:(#issue_code)issue_title`.
   - **Push to remote**: `git push origin temp_fix_code:fix/issue_code`.
   - **Cleanup**: Switch back to the original branch and **delete** the temporary local branch.
   - **Sync Workspace**: Optionally, the committed changes should no longer be "dirty" in the local workspace.
5. **Summary**: List the remote branches pushed and files included.

## Constraints
- **No persistent local branches**: Do not leave `fix/issue_code` branches in the local `git branch` list.
- **Direct Remote Push**: The goal is to update the remote branch `fix/issue_code` directly.
- Only handle tracked files.
- TODO check remains mandatory.
