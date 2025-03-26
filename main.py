import sys
import os
import zlib
import hashlib


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
    else:
        raise RuntimeError(f"Unknown command #{command}")

if __name__ == "__main__":
    main()
