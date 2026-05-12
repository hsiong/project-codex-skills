# Issue Commit Skill

## Purpose
Commit specific files to issue-related branches based on provided issue details (title and code).

## Trigger
Triggered when the user says "issue commit:" followed by issue information (e.g., text from a GitHub issue list).

## Requirements
1. **Parse Issue Info**: Extract `#issue_code` and `issue_title` for every issue mentioned in the input.
2. **Verify Input**: If the user says "issue commit" but provides no content after the colon, ask: "Please provide the issue content (title and code) you'd like to commit against."
3. **Analyze Changes**: Get the current `git diff` of all tracked files.
4. **Map Files**: Intelligently map each changed file to exactly one issue based on the issue's title and description. If a file relates to multiple issues or none, ask for clarification or group them logically.
5. **Per Issue Execution**:
   - Create or switch to a branch named `fix/issue_code` (e.g., `fix/25`).
   - Stage the files mapped to this issue.
   - Execute commit with the message: `Closes:(#issue_code)issue_title`.
6. **Summary**: After all operations, list the branches created/updated and the files committed to each.

## Constraints
- Use `git checkout -b fix/issue_code` if the branch doesn't exist, otherwise `git checkout fix/issue_code`.
- Follow the exact commit message format: `Closes:(#issue_code)issue_title`.
- Only handle tracked files.
- Do not commit if no files match an issue.
