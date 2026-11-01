---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: control-flow
tags: [state, discriminated-unions, flags, lifecycle]
keywords: ["isDraft = true", "isInReview = false", "isPublished", "isArchived", "if (this.is", "reviewer?: string"]
signature: "Several boolean properties encode one lifecycle state, so the object can hold combinations no real state corresponds to and every method re-tests the flags."
distinguish: "Fine when the flags are genuinely independent facts about the object that combine freely, so every combination is a real state."
added: 2026-09-30
source: refactoring.guru
---

# Lifecycle spread across boolean properties

## Smell

```typescript
export class Doc {
  isDraft = true;
  isInReview = false;
  isPublished = false;
  isArchived = false;
  reviewer?: string;
  text = "";

  submit(reviewer: string): void {
    if (this.isArchived) throw new Error("archived");
    this.isDraft = false;
    this.isInReview = true;
    this.reviewer = reviewer;
  }

  publish(): void {
    if (!this.isInReview && !this.isDraft) throw new Error("cannot publish");   // which states is this?
    this.isInReview = false;
    this.isPublished = true;           // reviewer stays set, isDraft stays true if never submitted
  }

  edit(text: string): void {
    if (this.isPublished && !this.isDraft) throw new Error("published");
    this.text = text;
  }

  archive(): void {
    this.isArchived = true;
    this.isPublished = false;          // a straight-to-publish doc is now draft and archived at once
  }
}
```

## Why it's bad

- Four booleans describe one state, so the class permits sixteen combinations for four real states. A document
  published straight from draft and then archived is `isDraft && isArchived`, and `edit` accepts it.
- Every method re-derives the state from the flags in its own dialect. `publish` asks "not review and not
  draft" where `edit` asks "published and not draft", and no reader can tell whether those are one question.
- `reviewer` is optional because it only means something in one state, so every reader has to check it for
  `undefined` or assert it with `!`, even in code that only runs during review.
- The legal transitions are written nowhere. Nothing says draft goes to review goes to published, so the
  diagram lives in a wiki page and the code is checked against it by hand.

## Better

```typescript
export type Doc =
  | { status: "draft"; text: string }
  | { status: "review"; text: string; reviewer: string }
  | { status: "published"; text: string; publishedAt: Date }
  | { status: "archived"; text: string };

const refuse = (doc: Doc, action: string): never => {
  throw new Error(`cannot ${action} from ${doc.status}`);
};

export const submit = (doc: Doc, reviewer: string): Doc =>
  doc.status === "draft" ? { status: "review", text: doc.text, reviewer } : refuse(doc, "submit");

export const publish = (doc: Doc): Doc =>
  doc.status === "review" ? { status: "published", text: doc.text, publishedAt: new Date() } : refuse(doc, "publish");

export const edit = (doc: Doc, text: string): Doc =>
  doc.status === "draft" ? { ...doc, text } : refuse(doc, "edit");

export const archive = (doc: Doc): Doc =>
  doc.status === "published" ? { status: "archived", text: doc.text } : refuse(doc, "archive");

export function label(doc: Doc): string {
  switch (doc.status) {
    case "draft": return "Draft";
    case "review": return `With ${doc.reviewer}`;          // reviewer exists here, and only here
    case "published": return `Published ${doc.publishedAt.toDateString()}`;
    case "archived": return "Archived";
  }
}
```

There is one `status`, so impossible combinations cannot be written, each state carries exactly the data that
belongs to it, and each transition names the one state it starts from. With `strictNullChecks`, a fifth status
makes `label` a compile error until it is handled. When each state has a lot of behaviour, the class-per-state
form of the pattern does the same job with methods instead of functions.
