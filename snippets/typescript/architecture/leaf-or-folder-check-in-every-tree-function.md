---
aliases: []
language: typescript
typescript: ">=3.0"
severity: taste
category: maintainability
topic: control-flow
tags: [composite, recursion, trees, discriminated-unions]
keywords: ["node.kind === \"file\"", "node.kind === \"dir\"", "node.children", "for (const child of", ".reduce(", "type TreeNode ="]
signature: "Every function over a tree repeats the check for leaf versus branch and the recursion into children, so the same case analysis is written once per traversal."
distinguish: "Fine when there is a single traversal, or when each traversal genuinely treats branches differently, such as one that prunes hidden folders."
added: 2026-09-30
source: refactoring.guru
---

# Leaf or folder check in every tree function

## Smell

```typescript
type TreeNode =
  | { kind: "file"; name: string; size: number; modified: Date }
  | { kind: "dir"; name: string; children: TreeNode[] };

export function totalSize(node: TreeNode): number {
  if (node.kind === "file") return node.size;
  return node.children.reduce((sum, child) => sum + totalSize(child), 0);
}

export function countFiles(node: TreeNode): number {
  if (node.kind === "file") return 1;
  let count = 0;
  for (const child of node.children) count += countFiles(child);
  return count;
}

export function newest(node: TreeNode): Date | undefined {
  if (node.kind === "file") return node.modified;
  const dates = node.children.map(newest).filter((d): d is Date => d !== undefined);
  return dates.length ? new Date(Math.max(...dates.map(Number))) : undefined;
}

// and findByName, olderThan, toJson: each with its own recursion
```

## Why it's bad

- The recursion is the same in every function and only the leaf case differs, so the shape of the tree is
  restated in every traversal, each in a slightly different style.
- Adding a `symlink` kind is a type error in every function, because each fall-through branch assumes anything
  that is not a file has `children`. That beats silence, but the fix is the same lines typed once per traversal.
- Each traversal decides for itself how to walk, so two functions that should agree on what "the files under
  this folder" means can disagree, and `newest` spreads a huge array into `Math.max` on a large tree.

## Better

```typescript
export function* files(node: TreeNode): Generator<Extract<TreeNode, { kind: "file" }>> {
  if (node.kind === "file") yield node;
  else for (const child of node.children) yield* files(child);
}

export const totalSize = (node: TreeNode) => {
  let sum = 0;
  for (const file of files(node)) sum += file.size;
  return sum;
};

export const countFiles = (node: TreeNode) => [...files(node)].length;

export function newest(node: TreeNode): Date | undefined {
  let latest: Date | undefined;
  for (const file of files(node)) if (!latest || file.modified > latest) latest = file.modified;
  return latest;
}
```

The walk is written once, as a generator, and each operation is a small consumer of it. A new node kind
changes `files` and nothing else; a class hierarchy with a `size()` method on both leaf and folder is the same
idea when the nodes already are classes.
