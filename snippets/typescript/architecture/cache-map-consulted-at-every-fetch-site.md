---
aliases: []
language: typescript
typescript: ">=3.0"
severity: trap
category: correctness
topic: classes
tags: [proxy, caching, invalidation, interfaces]
keywords: ["cache.get(", "cache.set(", "cache.delete(", "new Map<string", "Date.now() -", "await api.fetchUser("]
signature: "The check-cache, fetch, store sequence around an expensive call is retyped at every call site, so key layout, expiry and invalidation are decided independently in each one."
distinguish: "Fine at a single call site with one key, where the caching is a local optimisation of that function and nothing else fetches the same thing."
added: 2026-09-30
source: refactoring.guru
---

# Cache map consulted at every fetch site

## Smell

```typescript
const cache = new Map<string, { user: User; at: number }>();

export async function profilePage(id: string): Promise<string> {
  const hit = cache.get(`user:${id}`);
  if (hit && Date.now() - hit.at < 60_000) return renderProfile(hit.user);
  const user = await api.fetchUser(id);
  cache.set(`user:${id}`, { user, at: Date.now() });
  return renderProfile(user);
}

export async function invoicePdf(id: string): Promise<Uint8Array> {
  const hit = cache.get(`users/${id}`);          // a second key for the same user
  if (hit) return renderInvoice(hit.user);       // and no expiry at all
  const user = await api.fetchUser(id);
  cache.set(`users/${id}`, { user, at: Date.now() });
  return renderInvoice(user);
}

export async function changeAddress(id: string, address: Address): Promise<void> {
  await api.updateAddress(id, address);
  cache.delete(`user:${id}`);                    // clears one of the two keys
}
```

## Why it's bad

- One upstream object is cached under two keys with two lifetimes, so which answer you get about a user
  depends on which function you called.
- Invalidation can only be partial, because it has to know every key any caller invented. `changeAddress`
  clears `user:` and leaves `users/` holding the old address forever, so invoices go to the old address and
  nobody can reproduce it after a restart.
- The next feature copies the block again. There is no seam for metrics, a TTL change or a swap to Redis, and
  no way for a test to run uncached except by clearing a module-level `Map`.

## Better

```typescript
interface UserApi {
  fetchUser(id: string): Promise<User>;
  updateAddress(id: string, address: Address): Promise<void>;
}

/** Proxy: implements the client's interface, so callers cannot tell it is there. */
export class CachedUserApi implements UserApi {
  private readonly entries = new Map<string, { user: User; at: number }>();

  constructor(private readonly inner: UserApi, private readonly ttlMs = 60_000) {}

  async fetchUser(id: string): Promise<User> {
    const hit = this.entries.get(id);
    if (hit && Date.now() - hit.at < this.ttlMs) return hit.user;
    const user = await this.inner.fetchUser(id);
    this.entries.set(id, { user, at: Date.now() });
    return user;
  }

  async updateAddress(id: string, address: Address): Promise<void> {
    await this.inner.updateAddress(id, address);
    this.entries.delete(id);
  }
}

export async function invoicePdf(users: UserApi, id: string): Promise<Uint8Array> {
  return renderInvoice(await users.fetchUser(id));
}
```

The key, expiry and invalidation exist once, and because the proxy satisfies `UserApi`, a test passes the
real client to run uncached without the callers changing. A JavaScript `Proxy` object is not needed for this;
an ordinary class implementing the interface is the clearer proxy.
