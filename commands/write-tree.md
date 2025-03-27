# write-tree Command

`git write-tree` command is used to create a tree object from the current state of the "staging area". The staging area is a place where changes go when you run `git add`.

## Working

`write-tree` command works consists of two functions: `create_blob_entry()` and `write_tree()`.

`create_blob_entry()` handles individual files, turning their content into Git blob objects.

`write_tree()` handles directories. It iterates through sorted directory contents, calls `create_blob_entry()` for files or recursively calls itself (`write_tree()`) for subdirectories to get their respective SHA-1 hashes, assembles these pieces of information (mode, name, binary SHA) into the specific Git tree object format, and finally creates the tree object itself. Together, they allow you to take a directory structure on disk and represent it as a hierarchy of Git tree and blob objects stored in the `.git/objects` database.

## Command Usage

```bash
mkdir test_dir && cd test_dir

echo "hello world" > test_file_1.txt

mkdir test_dir_1

echo "hello world" > test_dir_1/test_file_2.txt

mkdir test_dir_2

echo "hello world" > test_dir_2/test_file_3.txt

mygit write-tree
#Returns the SHA hash: 4b825dc642cb6eb9a060e54bf8d69288fbee4904
```
