---
aliases: [dangerously-set-inner-html-with-user-content]
language: typescript
typescript: ">=3.0"
severity: bug
category: security
topic: strings
tags: [xss, dom, html, react, javascript]
keywords: [".innerHTML =", ".innerHTML +=", ".outerHTML =", "insertAdjacentHTML(", "dangerouslySetInnerHTML", "__html:"]
signature: "A string containing user data is assigned to innerHTML or passed to dangerouslySetInnerHTML, so markup in the data is parsed and its event handlers run."
distinguish: "Fine when the HTML is a constant or has been through a sanitizer such as DOMPurify or a Trusted Types policy, or when text is written with textContent, which never parses markup."
added: 2026-09-30
source: MDN
---

# Untrusted string assigned to innerHTML

## Smell

```typescript
type Comment = { author: string; body: string };

export function renderComment(list: HTMLElement, comment: Comment): void {
  const item = document.createElement("li");
  item.innerHTML = `<b>${comment.author}</b>: ${comment.body}`;
  list.append(item);
}
```

## Why it's bad

- A comment body of `<img src=x onerror=alert(1)>` runs script in every reader's session. `innerHTML` does not
  execute `<script>` elements, which is why "we strip script tags" feels like a defence and is not one.
- React's `dangerouslySetInnerHTML={{ __html: post.body }}` is the same sink under a different name; React
  escapes everything else, so this is where XSS in a React app usually lives.
- Escaping by hand inside the template is easy to get subtly wrong across attributes, URLs and text, and the
  next edit to the template silently drops it.

## Better

```typescript
type Comment = { author: string; body: string };

export function renderComment(list: HTMLElement, comment: Comment): void {
  const item = document.createElement("li");
  const author = document.createElement("b");
  author.textContent = comment.author;
  item.append(author, document.createTextNode(`: ${comment.body}`));
  list.append(item);
}
```
