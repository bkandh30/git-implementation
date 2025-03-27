# hash-object Command

`git hash-object` is used to compute the SHA hash of a Git object. When used with `-w` flag, it also writes the object to the `.git/objects` directory.

## Working

`git hash-object` command works by reading the entire contents of the file. The header string is concatenated into the content and later encoded to convert this string into a sequence of bytes. The **SHA-1** hash is generated which acts as the unique identifier of this object. The final object file is then compressed using **Zlib** library and it writes the compressed bytes to the object file.

## Command Usage

```bash
echo -n "Hello everyone" > test.txt

mygit hash-object -w test.txt
# Returns a hash: f3b9a1d8e0c5a7b2f4d6e9c0a3b7d1e8f5c2a0b9

file ./git/objects/f3/b9a1d8e0c5a7b2f4d6e9c0a3b7d1e8f5c2a0b9
#Returns: ./git/objects/f3/b9a1d8e0c5a7b2f4d6e9c0a3b7d1e8f5c2a0b9: zlib compressed data
```
