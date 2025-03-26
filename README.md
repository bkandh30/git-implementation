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

## Basic Usage

```bash
# Initialize a new repository
./mygit init

# Stage a file
./mygit add README.md

# Commit changes
./mygit commit -m "Initial commit"

# View commit history
./mygit log

# Create and switch to a new branch
./mygit branch new-feature
./mygit checkout new-feature
```
