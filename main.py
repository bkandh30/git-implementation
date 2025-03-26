import sys
import os
import zlib


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
    else:
        raise RuntimeError(f"Unknown command #{command}")

if __name__ == "__main__":
    main()
