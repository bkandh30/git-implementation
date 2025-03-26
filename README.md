# Git Implementation

This is basic implementation of Git in Python. I decided to make this project when I was learning about Git internals and how a version control works under the hood.

For deeper insights, check out [DESIGN.md](DESIGN.md)

## Features

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
mygit ls-tree --name-only random_hash_object

# Create a tree object of the current state
mygit write-tree
```
