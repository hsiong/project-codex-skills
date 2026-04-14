Use this skill when the user says "English commit", "english commit", "commit", or similar.

1. Complete multiple commits in the current Git workspace using only Git-known files.
2. All commit messages must be in English and follow GitHub/Conventional Commits style.
3. Group changes by complete functional flow rather than by code module, and commit from the largest change set to the smallest.
4. Never access files that are not added to Git, and never read or commit restricted paths or anything mentioned in `.gitignore`.
5. Never modify user code without permission, and summarize the total changed lines after completion.
