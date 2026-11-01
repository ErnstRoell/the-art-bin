---
aliases: []
language: rust
rust: ">=1.0"
severity: taste
category: maintainability
topic: control-flow
tags: [composite, recursion, trees, enums]
keywords: ["Node::File", "Node::Dir", "fn total_size(", "fn count_files(", "for child in children", "match node {"]
signature: "Every function over a tree repeats the match on leaf versus branch and the recursion into children, so the same case analysis is written once per traversal."
distinguish: "Fine when there is a single traversal, or when each traversal genuinely treats branches differently, such as pruning some subtrees."
added: 2026-09-23
source: refactoring.guru
---

# Tree walk repeated in every caller

## Smell

```rust
pub enum Node {
    File { name: String, size: u64 },
    Dir { name: String, children: Vec<Node> },
}

pub fn total_size(node: &Node) -> u64 {
    match node {
        Node::File { size, .. } => *size,
        Node::Dir { children, .. } => children.iter().map(total_size).sum(),
    }
}

pub fn count_files(node: &Node) -> usize {
    match node {
        Node::File { .. } => 1,
        Node::Dir { children, .. } => children.iter().map(count_files).sum(),
    }
}

pub fn largest_file(node: &Node) -> Option<(&str, u64)> {
    match node {
        Node::File { name, size } => Some((name, *size)),
        Node::Dir { children, .. } => {
            children.iter().filter_map(largest_file).max_by_key(|(_, size)| *size)
        }
    }
}

// and find_by_name, files_older_than, to_json: each with its own recursion
```

## Why it's bad

- The recursion is the same in every function and only the leaf case differs. The shape of the tree is
  therefore restated in every traversal.
- Adding a variant, such as `Node::Symlink`, is a compile error in every one of them. That is better than
  silence, but the fix is the same three lines, typed N times.
- Each traversal decides for itself whether to recurse depth-first, how deep to go, and whether to follow
  links, so two functions that should agree on what "the files under this directory" means can disagree.

## Better

```rust
impl Node {
    /// Every file under this node, depth first. The only place that knows how to walk the tree.
    pub fn files(&self) -> Box<dyn Iterator<Item = (&str, u64)> + '_> {
        match self {
            Node::File { name, size } => Box::new(std::iter::once((name.as_str(), *size))),
            Node::Dir { children, .. } => Box::new(children.iter().flat_map(Node::files)),
        }
    }
}

pub fn total_size(node: &Node) -> u64 {
    node.files().map(|(_, size)| size).sum()
}

pub fn count_files(node: &Node) -> usize {
    node.files().count()
}

pub fn largest_file(node: &Node) -> Option<(&str, u64)> {
    node.files().max_by_key(|(_, size)| *size)
}
```

The walk is written once and each operation is a one-line consumer of it. A new variant changes `files` and
nothing else.
