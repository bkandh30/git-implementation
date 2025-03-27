# commit-tree Command

`git commit-tree` command is used to create a commit object.

## Working

`git commit-tree` command works by taking a tree hash, an optional parent commit hash, and a mandatory message from its arguments. It constructs the textual content for a Git commit object, including the author/committer details (hardcoded in this case) and timestamps. It then calculates the SHA-1 hash of this content (prefixed with the standard Git object header), compresses the content, and writes it as an object file into the `.git/objects` directory structure, finally printing the commit's SHA-1 hash.

## Command Usage

```bash
mygit commit-tree <tree_sha> -p <commit_sha> -m <message>
```
