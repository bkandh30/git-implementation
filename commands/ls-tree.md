# ls-tree Command

`git ls-tree` command is used to view the type of an object, its size and its content.
Note: The output is alphabetically sorted.

## Working

`ls-tree --name-only` command works by reading a compressed Git tree object specified by its SHA-1 hash, decompresses it, parses the contents entry by entry, extracts only the filename from each entry and prints each filename on a new line.

## Command Usage

```bash
mygit ls-tree --name-only <tree_sha>
#Returns:
#dir1
#dir2
#dir3
```
