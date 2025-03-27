# cat-file Command

`git cat-file` command is used to view the type of an object, its size and its content.

## Working

`git cat-file` command works by reading the content of the blob object file from the `.git/objects` directory. The contents are then decompressed using **Zlib**. The headers are removed from the file and the actual content is then extracted. The results are then displayed to the user.

## Command Usage

```bash
mkdir /tmp/test_dir && cd /tmp/test_dir

mygit init

echo "Sample Text" > test.txt

mygit hash-object -w test.txt
# Returns a 40 character hash value: a7e2c9f0b3d81e5a4f6c0d9b8a3e7f1d5c8b0a4e

mygit cat-file -p a7e2c9f0b3d81e5a4f6c0d9b8a3e7f1d5c8b0a4e
# Returns: Sample Text
```
