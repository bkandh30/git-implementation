# clone Command

`git clone`

## Working

`clone` command coordinates fetching metadata (`get_refs`), downloading bulk data (`download_packfile`), processing that data into individual objects (`write_packfile` and its helpers like `apply_delta`, `next_size_type`, etc.), and finally creating the working directory files (`render_tree` which uses `read_object`).

For more details on it, look up: [LLD](LLD.md).

## Usage

```bash
mygit clone https://github.com/blah/blah <some_dir>
```
