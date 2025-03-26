# Design Documentation

## What is Git?

Git is a distributed version control system that tracks changes in computer files over time.

## .git Directory Breakdown

When we run `git init` in our project, it creates a `.git` directory under the project's root directory.

![Git File Directory](images/git-file-directory.png)

- `config`: It stores project-specific Git configurations
- `HEAD`: It contains the current head of the repository. If you are currently on the `master` directory, HEAD will point to `refs/head/master`.
- `hooks`: It contains any script that can be run before/after git does anything.
- `objects`: It stores all the commits, files, and histories in a compressed format using SHA hashes. `info` and `pack` are subfolder related to how Git stores and compresses those objects.
- `refs`: It contains references (pointers) to commits.
  - `heads/` contains branches.
  - `tags/` contains tags.

## Git Objects

Git stores the data as a series of content-addressable objects, each identified by SHA hash. These objects live in `.git/objects/`

- **Blobs:** A blob stores the actual content of a file - just the raw data, no file name or metadata. Every version of a file becomes a new blob.
- **Trees:** A tree object represents a directory. It stores file names, their associated blob hashes, permissions and other tree objects (for sub folders). Trees form a hierarchy as they connect file names (and folder structures) to blob objects
- **Commits:** A commit object points to one tree(representing the entire project at that moment), zero or more parent commits (for history) and author, message and timestamp. Commits tie everything together: blobs (file content), trees (folder structure), and history (previous commits).

## Git Object Storage

Git objects are stored in the `.git/objects` directory. The path to an object is derived from its hash. The path to an object is derived from its hash. The path for the object with the hash `a7f3d2b9e4c0f15e8a6c9b31d7f2846ab5cde987` would be:

```bash
./.git/objects/a7/f3d2b9e4c0f15e8a6c9b31d7f2846ab5cde987
```

The file is not directly placed in `./git/objects` directory. Instead, it is placed in a directory named with the first two characters of the object's hash. The remaining 38 characters are used as the file name.

## Blob Object Storage

Say when we have a file `hello.txt` with the contents:

```bash
Hello, world!
```

When we run:

```bash
git add hello.txt
```

Git creates a blob object:

- The content stored is `Hello, world!`
- Its SHA hash (example) is `2ef7bde608ce5404e97d5f042f95f89f1c232871`
- The object is saved at:

```bash
.git/objects/2e/f7bde608ce5404e97d5f042f95f89f1c232871
```

As you can notice, Git does not store full copies of your project each time you commit. It only stores new blobs when the content actually changes.

## Git Architecture

Git has three-stage model optimized for tracking changes: **the working directory**, **staging area** and **local repository**. Additionally, Git includes the concept of **remote repositories** for collaboration.

![Git Directory](images/Git-directories.png)

1. **Working Directory:** This is the actual folder where the project files and folders are saved. Modifications made to files in the working directory are considered 'untracked' until explicitly staged for commit.
2. **Staging Area (or Index):** The staging area acts as an intermediate step between the working directory and the .git directory. When you run `git add file.txt`, the file is moved from working tree to staging area. These files are staged to be included in the next commit.
3. **Local Repository:** This is the `.git` folder in your computer. It holds all the previous commits, branch history and objects. When you run `git commit`, Git takes everything from the staging area to local repository and saves a snapshot.
4. **Remote Repository:** This is a copy of your Github repository that is hosted online, which allows multiple developers to work on the same code and collaborate. The changes are pushed using `git push`. You can view changes made by other devs using `git pull`.

A typical workflow will look like:

- A developer edits files in the working tree.
- `git add` -> Stage them in the staging area.
- `git commit` -> Save them to your local repository.
- `git push` -> Send them to the remote repository (eg. Github)
