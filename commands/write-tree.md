# write-tree Command

`git write-tree` command is used to create a tree object from the current state of the "staging area". The staging area is a place where changes go when you run `git add`.

## Working

`write-tree` command works by.

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
