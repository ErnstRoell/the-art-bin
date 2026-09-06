---
aliases: [missing-composite, tree-walk-branches-on-node-kind]
language: python
python: ">=3.0"
severity: taste
category: maintainability
topic: control-flow
tags: [composite, recursion, polymorphism, trees]
keywords: ["isinstance(node", "node.children", "for child in", "hasattr(", "isinstance(child, list)", "recursion"]
signature: "Every walk over a tree branches on whether a node is a leaf or a group, so the same case analysis is repeated in each traversal."
distinguish: "Fine when leaves and groups genuinely support different operations, so a uniform interface would be a lie the callers have to see through anyway."
added: 2026-09-06
source: refactoring.guru
---

# Leaf and branch handled by the caller

## Smell

```python
def total_size(node):
    if isinstance(node, File):
        return node.size
    total = 0
    for child in node.children:
        if isinstance(child, File):
            total += child.size          # the leaf case, handled twice in one function
        else:
            total += total_size(child)
    return total


def render(node, depth=0):
    if isinstance(node, File):
        return "  " * depth + node.name
    lines = ["  " * depth + node.name + "/"]
    for child in node.children:
        lines.append(render(child, depth + 1))
    return "\n".join(lines)


def newest(node):
    if isinstance(node, File):
        return node.mtime
    return max(newest(child) for child in node.children)   # crashes on an empty folder
```

## Why it's bad

- The tree knows its own shape and refuses to say so, so every function over it re-derives the same two cases.
  Three traversals, three copies of "is this a leaf".
- The copies are not even consistent. `total_size` handles the leaf case twice — once at the top and once
  inside the loop — while `newest` handles the empty group not at all, and each divergence has to be found by
  reading rather than by asking the type.
- A new node kind means editing every traversal, and nothing enumerates them. The failure is a `Symlink` that
  three functions handle and the fourth silently treats as a folder.
- This is `isinstance-chain-instead-of-dispatch` in its recursive form: the branch is on leaf-versus-group
  rather than on a list of classes, which is why it survives review — it reads like the structure of the
  problem instead of a type switch.

## Better

```python
class File:
    def __init__(self, name, size, mtime):
        self.name, self.size, self.mtime = name, size, mtime

    def total_size(self):
        return self.size

    def render(self, depth=0):
        return "  " * depth + self.name

    def newest(self):
        return self.mtime


class Folder:
    """Same interface as File, so no caller has to know which it holds."""

    def __init__(self, name, children=()):
        self.name, self.children = name, list(children)

    def total_size(self):
        return sum(child.total_size() for child in self.children)

    def render(self, depth=0):
        lines = ["  " * depth + self.name + "/"]
        return "\n".join(lines + [c.render(depth + 1) for c in self.children])

    def newest(self):
        return max((child.newest() for child in self.children), default=None)
```

Each operation is written once per kind rather than once per traversal, the empty-folder case is stated where
it belongs, and adding `Symlink` means writing one class instead of editing every function that walks a tree.
