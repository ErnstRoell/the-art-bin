---
aliases: [missing-factory-method, product-hardcoded-in-the-algorithm]
language: python
python: ">=3.0"
severity: taste
category: maintainability
topic: classes
tags: [factory-method, subclassing, duplication, open-closed]
keywords: ["class ", "(Exporter)", "def run(self", "Writer(", "super().", "= CsvWriter("]
signature: "A method hardcodes the concrete class it constructs, so a variant subclass copies the whole method in order to change the one line that names the product."
distinguish: "Fine when there is one product and no test needs another, since a factory method added before a second implementation exists is indirection with nothing behind it."
added: 2026-09-06
source: refactoring.guru
---

# Base class names its concrete product

## Smell

```python
class Exporter:
    def __init__(self, path):
        self.path = path

    def run(self, rows):
        writer = CsvWriter(self.path)          # the only line a variant wants to change
        writer.write_header(rows[0].keys())
        for row in rows:
            writer.write(row)
        writer.close()
        return writer.byte_count


class JsonExporter(Exporter):
    def run(self, rows):                       # the whole method, copied to swap one line
        writer = JsonWriter(self.path)
        writer.write_header(rows[0].keys())
        for row in rows:
            writer.write(row)
        writer.close()
        return writer.byte_count
```

## Why it's bad

- The thing that varies is one line; the smallest unit that can be overridden is the whole method. So the
  export algorithm — header, loop, close, count — exists twice because the writer's name exists twice.
- The copies drift, and drift silently. A fix to the header handling lands in `run` on whichever class the bug
  was reported against, and the other export keeps the bug. That is how this presents: not as a design
  complaint but as the same defect reported twice, months apart.
- A third format copies the method a third time. The cost of a new product is proportional to the length of the
  algorithm rather than to the difference between products.
- A test cannot exercise the algorithm without also writing a file, because the only way to substitute a fake
  writer is to subclass and paste the method again.

## Better

```python
class Exporter:
    def __init__(self, path):
        self.path = path

    def make_writer(self):
        """The factory method: the one line that varies, and the only thing a subclass owns."""
        return CsvWriter(self.path)

    def run(self, rows):
        writer = self.make_writer()
        writer.write_header(rows[0].keys())
        for row in rows:
            writer.write(row)
        writer.close()
        return writer.byte_count


class JsonExporter(Exporter):
    def make_writer(self):
        return JsonWriter(self.path)
```

The algorithm exists once, so a fix to it lands everywhere, and a test subclasses `make_writer` to hand in a
writer that records to memory.
