import sys
import os
import zlib
import hashlib
import time
import datetime

def create_blob_entry(path, write=True):
    with open(path, "rb") as f:
        data = f.read()
        header = f"blob {len(data)}\0".encode("utf-8")
        store = header + data
        sha = hashlib.sha1(store).hexdigest()
        if write:
            os.makedirs(f".git/objects/{sha[:2]}", exist_ok=True)
            with open(f".git/objects/{sha[:2]}/{sha[2:]}", "wb") as f:
                f.write(zlib.compress(store))
    return sha

def write_tree(path:str):
    if os.path.isfile(path):
        return create_blob_entry(path)
    
    contents = sorted(
        os.listdir(path),
        key=lambda x: x if os.path.isfile(os.path.join(path, x)) else f"{x}/",
    )

    s = b""
    for item in contents:
        if item == ".git":
            continue
        full = os.path.join(path, item)
        if os.path.isfile(full):
            s += f"100644 {item}\0".encode()
        else:
            s += f"40000 {item}\0".encode()
        sha1 = int.to_bytes(int(write_tree(full), base=16), length=20, byteorder="big")
        s += sha1

    s = f"tree {len(s)}\0".encode() + s
    sha1 = hashlib.sha1(s).hexdigest()
    os.makedirs(f".git/objects/{sha1[:2]}", exist_ok= True)
    with open(f".git/objects/{sha1[:2]}/{sha1[2:]}", "wb") as f:
        f.write(zlib.compress(s))
    return sha1

def commit_tree(args):
    if len(args) < 3:
        raise RuntimeError("Usage: commit-tree <tree-hash> -p <parent-commit> -m <message>")
    
    tree_hash = args[0]
    parent_hash = None
    message = None

    i = 1

    while i < len(args):
        if args[i] == "-p" and i + 1 < len(args):
            parent_hash = args[i + 1]
            i += 2
        elif args[i] == "-m" and i + 1 < len(args):
            message = args[i + 1]
            i += 2
        else:
            i += 1

    if not message:
        raise RuntimeError("Commit message is required")
    
    content = f"tree {tree_hash}\n"
    if parent_hash:
        content += f"parent {parent_hash}\n"
    
    author = "bhavya.kandhari.eng@gmail.com"

    content += f"author {author} {int(time.time())} {time.timezone}\n"
    content += f"committer {author} {int(time.time())} {time.timezone}\n"
    content += f"\n{message}\n"

    #Create commit object
    header = f"commit {len(content)}\0"
    store = (header + content).encode("utf-8")
    sha = hashlib.sha1(store).hexdigest()

    #Write commit object
    os.makedirs(f".git/objects/{sha[:2]}", exist_ok=True)
    with open(f".git/objects/{sha[:2]}/{sha[2:]}", "wb") as f:
        f.write(zlib.compress(store))

    print(sha)
    return sha

def main():
    
    print("Logs from your program will appear here!", file=sys.stderr)

    command = sys.argv[1]
    if command == "init":
        os.mkdir(".git")
        os.mkdir(".git/objects")
        os.mkdir(".git/refs")
        with open(".git/HEAD", "w") as f:
            f.write("ref: refs/heads/main\n")
        print("Initialized git directory")
    elif command == "cat-file" and sys.argv[2] == "-p":
        obj_name = sys.argv[3]
        folder_name = obj_name[:2]
        file_name = obj_name[2:]
        with open(f"./.git/objects/{folder_name}/{file_name}","rb") as f:
            raw = zlib.decompress(f.read())
            content = (raw.split(b"\0"))[1]
            print(content.decode(encoding="utf-8"), end="")
    elif command == "hash-object" and sys.argv[2] == "-w":
        obj_name = sys.argv[3]
        with open(obj_name, "r") as f:
            content = f.read()
        
        header = f"blob {len(content)}\x00"
        store = (header + content).encode()

        sha = hashlib.sha1(store).hexdigest()

        directory = f".git/objects/{sha[0:2]}"
        if not os.path.exists(directory):
            os.mkdir(directory)

        with open(f"{directory}/{sha[2:]}", "wb") as f:
            f.write(zlib.compress(store))
        
        print(sha, end="")
    elif command == "ls-tree" and sys.argv[2] == "--name-only":
        tree_sha = sys.argv[3]
        folder_name = tree_sha[:2]
        file_name = tree_sha[2:]
        with open(f".git/objects/{folder_name}/{file_name}","rb") as f:
            data = zlib.decompress(f.read())
            _, binary_data = data.split(b"\x00",maxsplit=1)
            while binary_data:
                mode, binary_data = binary_data.split(b"\x00",maxsplit=1)
                _, name = mode.split()
                binary_data = binary_data[20:]
                print(name.decode(encoding="utf-8"))
    elif command == "write-tree":
        print(write_tree("./"))
    elif command == "commit-tree":
        commit_tree(sys.argv[2:])
    else:
        raise RuntimeError(f"Unknown command #{command}")

if __name__ == "__main__":
    main()
