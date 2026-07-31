# obsidianlib

Python library for parsing and analyzing Obsidian markdown notes.

## Installation

```bash
pip install obsidianlib
```

## Wikilinks and backlinks

Extract unique backlink destinations from Markdown content:

```python
from obsidianlib import extract_wikilinks

links = extract_wikilinks(
    "See [[Project]], [[Project#Status|current status]], and ![[diagram.png]]."
)

for link in links:
    print(link.destination, link.alias, link.embedded)
```

The parser supports regular links, heading links, aliases, and embedded links.
Duplicate destinations are removed in order of first appearance by default.
Pass `deduplicate=False` to keep every occurrence or `include_embeds=False` to
ignore embeds.

Files can be read directly with `extract_wikilinks_from_file(path)`. The
`extract_backlinks` and `extract_backlinks_from_file` names are equivalent
aliases for backlink-indexing code.

The package also installs a JSON-producing CLI:

```bash
obsidian-backlinks note.md
cat note.md | obsidian-backlinks
obsidian-backlinks --keep-duplicates --exclude-embeds note.md
```

## Development

Build the package locally:

```bash
python -m build
```

Run the unit tests:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```
