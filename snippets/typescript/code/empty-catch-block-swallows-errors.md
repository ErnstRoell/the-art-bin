---
aliases: [silent-catch]
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: exceptions
tags: [error-handling, silent-failure, javascript]
keywords: ["catch {}", "catch (e) {}", "catch (err) {}", ".catch(() => {})", "no-empty"]
signature: "A catch block or catch handler is empty, so every failure of the guarded code, expected or not, disappears without a trace."
distinguish: "Fine when the catch is narrow, the ignored failure is genuinely expected, and a comment says why doing nothing is correct."
added: 2026-09-30
source: ESLint
---

# Empty catch block swallows errors

## Smell

```typescript
async function syncProfile(user: User): Promise<void> {
  try {
    const remote = await crm.fetchContact(user.email);
    await db.users.update(user.id, mergeProfile(user, remote));
  } catch {}

  analytics.track("profile_synced", { id: user.id }).catch(() => {});
}
```

## Why it's bad

- The `try` covers a network call, a merge and a database write. An empty `catch` hides all of them alike,
  including a bug in `mergeProfile` that fails on every user.
- The function reports success regardless, so the symptom is stale data noticed weeks later with nothing in
  the logs to show when it started.
- ESLint's `no-empty` flags empty blocks and accepts one that contains a comment, and the Google TypeScript
  Style Guide requires that comment: doing nothing in a catch is very rarely correct, so the reason must be
  written down.

## Better

```typescript
async function syncProfile(user: User): Promise<void> {
  let remote: Contact | undefined;
  try {
    remote = await crm.fetchContact(user.email);
  } catch (err) {
    log.warn("CRM unavailable, keeping local profile", { id: user.id, err });
    return;
  }
  await db.users.update(user.id, mergeProfile(user, remote));

  // Analytics is best-effort; a lost event must not fail the sync.
  analytics.track("profile_synced", { id: user.id }).catch((err) => log.debug("track failed", err));
}
```
