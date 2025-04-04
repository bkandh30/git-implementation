import enum
import sys
import os
import zlib
from hashlib import sha1
import time
import urllib.request
import struct
from pathlib import Path
import re

# Global configuration for Git author details
GIT_AUTHOR_EMAIL = "bhavya.kandhari.eng@gmail.com"
GIT_AUTHOR_NAME = "Bhavya Kandhari"

# Enum for Git object types
class ObjectType(enum.Enum):
    COMMIT = 1
    TREE = 2
    BLOB = 3
    TAG = 4
    OFS_DELTA = 6
    REF_DELTA = 7

# Enum for file mode types
class Mode(enum.IntEnum):
    FILE = 100644
    EXECUTABLE = 100755
    SYMLINK = 120000
    DIRECTORY = 40000

# Class representing an entry in a tree object
class TreeEntry:
    def __init__(self, mode, name, item_hash):
        self.mode: Mode = mode  # File mode (e.g., regular file, directory)
        self.name: str = name   # File or directory name
        self.hash: bytes = item_hash  # SHA hash of the object

def main():
    """
    Main function to handle different Git commands.
    Uses Python's structural pattern matching to determine which command to run.
    """
    match sys.argv[1:]:
        case ["init"]:
            init_repo(Path(os.getcwd()))
        case ["cat-file", "-p", object_hash]:
            cat_file(object_hash)
        case ["hash-object", write, file_name]:
            sha_hash = hash_file(file_name, write == "-w")
            print(sha_hash, end="")
        case ["ls-tree", param, tree_hash]:
            ls_tree(tree_hash, param)
        case ["write-tree"]:
            write_tree()
        case ["commit-tree", tree_sha, "-p", commit_sha, "-m", commit_message]:
            commit_tree(commit_message, commit_sha, tree_sha)
        case ["clone", url_string, dest_dir]:
            clone_repo(dest_dir, url_string)
        case _:
            raise RuntimeError(f"Unknown command #{sys.argv[1:]}")

def init_repo(path: Path):
    """
    Initializes a new Git repository by creating the required directory structure.
    """
    os.makedirs(path, exist_ok=True)
    os.makedirs(path / ".git" / "objects", exist_ok=True)
    os.makedirs(path / ".git" / "refs", exist_ok=True)
    os.makedirs(path / ".git" / "refs" / "heads", exist_ok=True)
    with open(path / ".git" / "HEAD", "w") as f:
        f.write("ref: refs/heads/main\n")
    print(f"Initialized empty Git repository in {path}")

def cat_file(object_hash: str):
    """
    Prints the contents of a Git object identified by its SHA hash.
    """
    path = f".git/objects/{object_hash[:2]}/{object_hash[2:]}"
    with open(path, "rb") as f:
        decompressed = zlib.decompress(f.read())
        # Split header from the actual content
        _, data = decompressed.split(b"\0", maxsplit=1)
        print(data.decode(), end="")

def hash_file(path: str, write: bool = True) -> str:
    """
    Creates a blob object from a file and optionally writes it to the Git object database.
    
    :param path: Path to the file.
    :param write: Whether to write the object to disk.
    :return: SHA-1 hash of the blob object.
    """
    with open(path, "r") as f:
        file_content = f.read()
        # Prepare the blob content in the format: "blob <len>\0<content>"
        to_be_hashed = f"blob {len(file_content)}\0{file_content}".encode()
        sha_hash = sha1(to_be_hashed, usedforsecurity=False).hexdigest()
        if write:
            folder_path = f".git/objects/{sha_hash[:2]}"
            hashed_file_name = sha_hash[2:]
            os.makedirs(folder_path, exist_ok=True)
            with open(f"{folder_path}/{hashed_file_name}", "wb") as hf:
                hf.write(zlib.compress(to_be_hashed))
        return sha_hash

def hash_tree(path: str, write: bool = True) -> bytes:
    """
    Recursively hashes the directory tree and returns the tree object.
    
    :param path: Directory path to hash.
    :param write: Whether to write blob objects to disk.
    :return: Serialized tree object bytes.
    """
    dir_items = os.listdir(path)
    git_items = []

    for item in dir_items:
        if item == ".git":
            continue  # Skip Git directory
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            print(f"file {item}", file=sys.stderr)
            file_hash = hash_file(item_path, write)
            git_items.append(TreeEntry(Mode.FILE, item, file_hash))
        elif os.path.isdir(item_path):
            print(f"directory {item}", file=sys.stderr)
            tree = hash_tree(item_path)
            tree_hash = sha1(tree, usedforsecurity=False).hexdigest()
            git_items.append(TreeEntry(Mode.DIRECTORY, item, tree_hash))

    # Sort items by name to have a deterministic order
    git_items.sort(key=lambda i: i.name)

    tree_content = b""
    for item in git_items:
        # Format each tree entry: "<mode> <name>\0<20-bytes hash>"
        tree_content += f"{str(item.mode)} {item.name}\0".encode()
        tree_content += int.to_bytes(int(item.hash, 16), length=20, byteorder="big")

    tree = f"tree {str(len(tree_content))}\0".encode() + tree_content
    return tree

def write_tree():
    """
    Writes the current directory tree as a tree object and prints its SHA hash.
    """
    tree = hash_tree(os.getcwd())
    hashed = sha1(tree, usedforsecurity=False).hexdigest()
    print(hashed, end="")

    folder_path = f".git/objects/{hashed[:2]}"
    hashed_file_name = hashed[2:]
    os.makedirs(folder_path, exist_ok=True)
    with open(f"{folder_path}/{hashed_file_name}", "wb") as hf:
        hf.write(zlib.compress(tree))

def commit_tree(commit_message: str, commit_sha: str, tree_sha: str):
    """
    Creates a commit object linking a tree and a parent commit.
    
    :param commit_message: Commit message.
    :param commit_sha: Parent commit SHA.
    :param tree_sha: Tree object SHA.
    """
    timestamp = int(time.time())
    timezone = time.timezone
    content = (
        f"tree {tree_sha}\n"
        f"parent {commit_sha}\n"
        f"author {GIT_AUTHOR_NAME} <{GIT_AUTHOR_EMAIL}> {timestamp} {timezone} "
        f"committer {GIT_AUTHOR_NAME} <{GIT_AUTHOR_EMAIL}> {timestamp} {timezone}\n\n"
        f"{commit_message}\n"
    )
    commit_object = f"commit {len(content)}\0{content}".encode()
    commit_hash = sha1(commit_object, usedforsecurity=False).hexdigest()

    folder_path = f".git/objects/{commit_hash[:2]}"
    hashed_file_name = commit_hash[2:]
    os.makedirs(folder_path, exist_ok=True)
    with open(f"{folder_path}/{hashed_file_name}", "wb") as hf:
        hf.write(zlib.compress(commit_object))
    print(commit_hash, end="")

def ls_tree(tree_hash: str, arg: str):
    """
    Lists the contents of a tree object.
    
    :param tree_hash: SHA hash of the tree object.
    :param arg: Additional argument; if '--name-only', only file names are printed.
    """
    tree_items = []
    object_path = f".git/objects/{tree_hash[:2]}/{tree_hash[2:]}"
    with open(object_path, "rb") as f:
        decompressed = zlib.decompress(f.read())
        # Skip the header ("tree <size>\0")
        head, data = decompressed.split(b"\0", maxsplit=1)
        if head[:4] == b"tree":
            while data:
                # Each entry: "<mode> <name>\0<20-bytes hash>"
                head, data = data.split(b"\0", maxsplit=1)
                mode, name = head.split(b" ", maxsplit=1)
                mode = int(mode)
                name = name.decode()
                item_hash = data[:20]
                tree_items.append(TreeEntry(mode, name, item_hash))
                data = data[20:]
        if arg == "--name-only":
            for item in tree_items:
                print(item.name)
        else:
            for item in tree_items:
                print(f"{item.mode} ", end="")
                if item.mode == Mode.DIRECTORY:
                    print("tree ", end="")
                else:
                    print("blob ", end="")
                print(f"{item.hash.hex()}\t{item.name}")

def read_object(path: Path, sha: str) -> (str, bytes):
    """
    Reads a Git object from the object store.
    
    :param path: Root path of the repository.
    :param sha: SHA hash of the object.
    :return: Tuple of (object type, content)
    """
    directory = sha[:2]
    file_name = sha[2:]
    p = path / ".git" / "objects" / directory / file_name
    data = p.read_bytes()
    head, content = zlib.decompress(data).split(b"\0", maxsplit=1)
    obj_type, _ = head.split(b" ")
    return obj_type, content

def write_object(path: Path, obj_type: bytes, content: bytes) -> str:
    """
    Writes a Git object (commit, tree, blob, etc.) to the object store.
    
    :param path: Repository path.
    :param obj_type: Object type as bytes (e.g., b'commit').
    :param content: Object content.
    :return: SHA hash of the written object.
    """
    # Create the object header: "<type> <size>\0"
    content = obj_type + b" " + str(len(content)).encode() + b"\0" + content
    sha = sha1(content, usedforsecurity=False).hexdigest()
    print(f"write object {sha}")

    compressed_content = zlib.compress(content, level=zlib.Z_BEST_SPEED)
    directory = sha[:2]
    file_name = sha[2:]
    p = path / ".git" / "objects" / directory / file_name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(compressed_content)
    return sha

def get_object_type_name(obj_type: int) -> str:
    """
    Returns the string representation of a Git object type.
    
    :param obj_type: Object type integer.
    :return: String name of the object type.
    """
    match obj_type:
        case ObjectType.COMMIT.value:
            return "commit"
        case ObjectType.TREE.value:
            return "tree"
        case ObjectType.BLOB.value:
            return "blob"
        case ObjectType.TAG.value:
            return "tag"
        case ObjectType.OFS_DELTA.value:
            return "ofs delta"
        case ObjectType.REF_DELTA.value:
            return "ref delta"
        case _:
            raise RuntimeError(f"Unknown object type {obj_type}")

def read_varint(data: bytes, pos: int) -> (int, int):
    """
    Reads a variable-length integer from data starting at the given position.
    
    :param data: Bytes containing the variable-length integer.
    :param pos: Starting position in data.
    :return: A tuple (result, new_position).
    """
    result: int = 0
    shift: int = 0
    while True:
        byte: int = data[pos]
        pos += 1
        result |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            break
        shift += 7
    return result, pos

def decompress_object(data: bytes, expected_size: int) -> (bytes, bytes):
    """
    Decompresses an object from its compressed representation.
    
    :param data: Compressed object data.
    :param expected_size: Expected size after decompression.
    :return: Tuple of (decompressed_data, remainder_bytes).
    """
    decompressor = zlib.decompressobj()
    decompressed = decompressor.decompress(data, expected_size)
    decompressed += decompressor.flush()
    remainder = decompressor.unused_data
    # Ensure no leftover unprocessed tail and the decompressed size is as expected
    assert decompressor.unconsumed_tail == b""
    assert len(decompressed) == expected_size
    return decompressed, remainder

def apply_ref_delta(base_obj_hash, delta_data, dest_path):
    """
    Applies a ref delta to a base object to reconstruct the target object.
    
    :param base_obj_hash: SHA hash of the base object.
    :param delta_data: Delta data bytes.
    :param dest_path: Repository path.
    :return: Tuple (base_obj_type, target_content) after applying delta.
    """
    target_content = b""
    base_obj_type, base_content = read_object(dest_path, base_obj_hash)

    # Read the source and target sizes (variable-length integers)
    src_size, pos = read_varint(delta_data, 0)
    tgt_size, pos = read_varint(delta_data, pos)
    delta_data = delta_data[pos:]

    while delta_data:
        opcode = delta_data[0]
        delta_data = delta_data[1:]
        if opcode & 0x80:  # Copy from base object
            copy_offset = 0
            copy_length = 0
            if opcode & 0x01:
                copy_offset |= delta_data[0]
                delta_data = delta_data[1:]
            if opcode & 0x02:
                copy_offset |= delta_data[0] << 8
                delta_data = delta_data[1:]
            if opcode & 0x04:
                copy_offset |= delta_data[0] << 16
                delta_data = delta_data[1:]
            if opcode & 0x08:
                copy_offset |= delta_data[0] << 24
                delta_data = delta_data[1:]
            if opcode & 0x10:
                copy_length |= delta_data[0]
                delta_data = delta_data[1:]
            if opcode & 0x20:
                copy_length |= delta_data[0] << 8
                delta_data = delta_data[1:]
            if opcode & 0x40:
                copy_length |= delta_data[0] << 16
                delta_data = delta_data[1:]
            if copy_length == 0:
                copy_length = 0x10000
            target_content += base_content[copy_offset: copy_offset + copy_length]
        else:  # Insert literal data from the delta stream
            insert_length = opcode
            target_content += delta_data[:insert_length]
            delta_data = delta_data[insert_length:]
    return base_obj_type, target_content

def build_tree(path: Path, folder: Path, sha: str):
    """
    Reconstructs a directory tree from a tree object and writes files to the filesystem.
    
    :param path: Repository path.
    :param folder: Destination folder where the tree will be built.
    :param sha: SHA hash of the tree object.
    """
    folder.mkdir(parents=True, exist_ok=True)
    _, tree = read_object(path, sha)

    while tree:
        # Parse each tree entry: mode, name, and SHA hash.
        mode, tree = tree.split(b" ", maxsplit=1)
        name, tree = tree.split(b"\0", maxsplit=1)
        sha = tree[:20].hex()
        tree = tree[20:]
        match int(mode):
            case Mode.FILE.value:
                # Write file content
                _, content = read_object(path, sha)
                with open(folder / name.decode(), "wb") as f:
                    f.write(content)
            case Mode.DIRECTORY.value:
                # Recursively build subdirectories
                build_tree(path, folder / name.decode(), sha)
            case _:
                raise RuntimeError(f"unknown mode {mode}")

def clone_repo(dest_dir, url_string):
    """
    Clones a Git repository from a remote URL to a local destination.
    
    :param dest_dir: Local destination directory.
    :param url_string: Remote repository URL.
    """
    print(f"clone {url_string} to {dest_dir}")
    dest_path = Path(dest_dir)
    init_repo(dest_path)

    # Step 1: Request references from remote repository
    body = "0014command=ls-refs\n0000"
    req = urllib.request.Request(
        f"{url_string}/git-upload-pack",
        data=body.encode(),
        headers={"git-protocol": "version=2"},
    )
    with urllib.request.urlopen(req) as f:
        data = f.read()

    # Example response:
    # 00327b8eb72b9dfa14a28ed22d7618b3cdecaa5d5be0 HEAD\n
    # 003f7b8eb72b9dfa14a28ed22d7618b3cdecaa5d5be0 refs/heads/master\n
    # 0000
    refs = extract_references(data.decode())

    # Save references (like HEAD and branch pointers)
    for name, sha in refs.items():
        (dest_path / ".git" / name).write_text(sha + "\n")

    # Step 2: Fetch objects from the remote repository
    body = (
        "0011command=fetch0001000fno-progress"
        + "".join("0032want " + sha + "\n" for sha in refs.values())
        + "0009done\n0000"
    )
    req = urllib.request.Request(
        f"{url_string}/git-upload-pack",
        data=body.encode(),
        headers={"git-protocol": "version=2"},
    )
    with urllib.request.urlopen(req) as f:
        pack_bytes: bytes = f.read()

    # Process the received packfile data
    lines = []
    while pack_bytes:
        # The first 4 bytes indicate the length in hex
        line_len = int(pack_bytes[:4], 16)
        if line_len == 0:
            break
        lines.append(pack_bytes[4:line_len])
        pack_bytes = pack_bytes[line_len:]
    # Reconstruct the pack file by removing the first byte of each line (marker)
    pack_file = b"".join(l[1:] for l in lines[1:])

    # Unpack the pack file header to get version and object count
    version_number, number_of_objects = struct.unpack(">II", pack_file[4:12])
    print(f"Version number: {version_number}", file=sys.stderr)
    print(f"Number of objects: {number_of_objects}", file=sys.stderr)

    objects = pack_file[12:]
    object_count = 0

    # Iterate through each object in the pack file
    while objects:
        object_count += 1
        c = objects[0]
        obj_type = (c >> 4) & 7
        size = c & 15
        shift = 4
        i = 1

        # Read the variable-length size
        while c & 0x80:  # Continue reading if high bit is set
            if shift > 32:
                size = 0
                break
            c = objects[i]
            i += 1
            size += (c & 0x7F) << shift
            shift += 7
        objects = objects[i:]

        print(f"{get_object_type_name(obj_type)} object, size: {size}")

        # Process object based on its type
        match obj_type:
            case (ObjectType.COMMIT.value
                  | ObjectType.TREE.value
                  | ObjectType.BLOB.value
                  | ObjectType.TAG.value):
                # Decompress and write the object
                decompressed_data, objects = decompress_object(objects, size)
                write_object(
                    dest_path,
                    get_object_type_name(obj_type).encode(),
                    decompressed_data,
                )
            case ObjectType.REF_DELTA.value:
                # Handle ref delta: apply the delta to reconstruct the object
                base_obj_hash = objects[:20].hex()
                print(f"unpacking ref delta object {base_obj_hash}")
                objects = objects[20:]
                delta_data, objects = decompress_object(objects, size)
                base_obj_type, target_content = apply_ref_delta(
                    base_obj_hash, delta_data, dest_path
                )
                write_object(dest_path, base_obj_type, target_content)
            case _:
                raise RuntimeError("Invalid object type")
        if object_count >= number_of_objects:
            print("All objects unpacked")
            break

    print(f"Unpacked {object_count} objects")

    # After fetching objects, read the HEAD commit and build the working tree
    _, commit = read_object(dest_path, refs["HEAD"])
    tree_sha = commit[5:40 + 5].decode()
    build_tree(dest_path, dest_path, tree_sha)

def extract_references(data: str) -> dict[str, str]:
    """
    Extracts reference names and their corresponding SHA hashes from a response string.
    
    :param data: The response string from a Git command.
    :return: A dictionary mapping reference names to SHA hashes.
    """
    references: dict = {}
    lines = data.strip().split("\n")
    for line in lines:
        # Example line: 00327b8eb72b9dfa14a28ed22d7618b3cdecaa5d5be0 HEAD
        # The regex captures the SHA and the reference name, ignoring the 4-digit length prefix.
        match = re.match(r"^[0-9a-f]{4}([0-9a-f]{40})\s+(.+)$", line)
        if match:
            sha, name = match.groups()
            references[name] = sha
    return references

if __name__ == "__main__":
    main()
