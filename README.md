# Git Implementation

This is basic implementation of Git in Python. I decided to make this project when I was learning about Git internals and how a version control works under the hood.

For a detailed explanation of the Git Protocol, check out: [LLD.md](/commands/LLD.md)

For deeper insights on the design architecture of Git, check out [DESIGN.md](DESIGN.md)

For deeper insights on each command and their usage, check out:
| Command | Page |
|---------------|----------------------------------------|
| `init` | [init.md](/commands/init.md) |
| `cat-file` | [cat-file.md](/commands/cat-file.md) |
| `hash-object` | [hash-object.md](/commands/hash-object.md) |
| `ls-tree` | [ls-tree.md](/commands/ls-tree.md) |
| `write-tree` | [write-tree.md](/commands/write-tree.md) |
| `commit-tree` | [commit-tree.md](/commands/commit-tree.md) |
| `clone` | [clone.md](/commands/clone.md) |

## Installation

```bash
git clone https://github.com/bkandh30/git-implementation.git
cd git-implementation

# Install dependencies (if any)
pip install -r requirements.txt
```

## Local Testing

For testing the script locally, you can use shell alias:

```bash
alias mygit=/path-to-your-repo/mygit.sh

mkdir -p /tmp/test_dir && cd /tmp/test_dir
mygit init

echo -n "Hello World" > test.txt
```

## Basic Usage

```bash
# Initialize a new repository
mygit init

# Read contents from the blob
mygit cat-file -p <blob_sha>

# Compute SHA hash of Git object
mygit hash-object -w test.txt

# Inspect Tree Object
mygit ls-tree --name-only <blob_sha>

# Create a tree object of the current state
mygit write-tree

#Create a new commit with the new tree SHA
mygit commit-tree <tree_sha> -p <commit_sha> -m <message>

#Clone a repository
mygit clone https://github.com/code/repository/url <some_dir>
```

## 📚 References

- [Git Internals Documentation](https://git-scm.com/docs)
- [Codecrafters: Build your own Git](https://app.codecrafters.io/courses/git/overview)
- [KodeKloud: How Git Works](https://kodekloud.com/blog/how-git-works/)
- [Write yourself a Git!](https://wyag.thb.lt/)
- [Build Your Own Git from Scratch in Go](https://medium.com/@duggal.sarthak12/building-your-own-git-from-scratch-in-go-01166fcb18ad)
- [StackOverflow: What does the Git Smart HTTP(S) protocol fully look like in all its glory?](https://stackoverflow.com/questions/68062812/what-does-the-git-smart-https-protocol-fully-look-like-in-all-its-glory)
- [Git-Protocol](https://i27ae15.github.io/git-protocol-doc/docs/git-protocol/intro)
