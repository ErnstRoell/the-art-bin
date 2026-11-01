---
aliases: []
language: typescript
typescript: ">=3.0"
severity: bug
category: security
topic: strings
tags: [injection, sql, database, pg, javascript]
keywords: ["query(`SELECT", "`SELECT * FROM", "WHERE email = '${", "= ${", "$queryRawUnsafe(", "execute(`", "+ \"' AND"]
signature: "A SQL statement is assembled by interpolating values into a template literal or concatenated string, so a value containing SQL is executed as SQL."
distinguish: "Fine when every value is passed as a bound parameter or through a library's sql tagged template that turns interpolations into parameters, and only identifiers picked from a fixed allow-list are written into the text."
added: 2026-09-30
source: OWASP SQL Injection Prevention Cheat Sheet
---

# SQL built with a template literal

## Smell

```typescript
import { Pool } from "pg";

const pool = new Pool();

export async function findUser(email: string) {
  const { rows } = await pool.query(
    `SELECT * FROM users WHERE email = '${email}'`,
  );
  return rows[0];
}
```

## Why it's bad

- An email of `' OR '1'='1` returns the first user in the table. A template literal is plain string
  concatenation, so nothing distinguishes the value from the SQL around it.
- A legitimate value with an apostrophe, such as `o'brien@example.com`, is a syntax error, which is usually how
  the bug is found first.
- Parameterised queries are the primary defence: node-postgres sends the query text unaltered and the
  parameters separately, and the server substitutes them. The look-alike to watch for is an ORM's escape hatch,
  such as Prisma's `$queryRawUnsafe`, fed an interpolated string; its tagged `$queryRaw` is parameterised.

## Better

```typescript
import { Pool } from "pg";

const pool = new Pool();

export async function findUser(email: string) {
  const { rows } = await pool.query("SELECT * FROM users WHERE email = $1", [email]);
  return rows[0];
}
```
