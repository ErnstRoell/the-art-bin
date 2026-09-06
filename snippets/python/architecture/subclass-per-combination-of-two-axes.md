---
aliases: [missing-bridge, subclass-cross-product]
language: python
python: ">=3.0"
severity: taste
category: maintainability
topic: classes
tags: [bridge, composition, inheritance, combinatorics]
keywords: ["class Urgent", "class Sms", "(EmailNotifier)", "(Notifier)", "super().send", "class "]
signature: "One class hierarchy varies along two independent axes at once, so the number of subclasses is the product of the two lists rather than their sum."
distinguish: "Fine when only one axis actually varies, or when the handful of combinations each behave genuinely differently rather than mechanically."
added: 2026-09-06
source: refactoring.guru
---

# Subclass per combination of two axes

## Smell

```python
class EmailNotifier:
    def send(self, user, text):
        smtp_send(user.email, text)


class SmsNotifier:
    def send(self, user, text):
        sms_send(user.phone, text)


class UrgentEmailNotifier(EmailNotifier):
    def send(self, user, text):
        smtp_send(user.email, "URGENT: " + text)
        smtp_send(user.manager.email, "URGENT: " + text)


class UrgentSmsNotifier(SmsNotifier):
    def send(self, user, text):
        sms_send(user.phone, "URGENT: " + text)
        sms_send(user.manager.phone, "URGENT: " + text)


class QuietEmailNotifier(EmailNotifier):
    def send(self, user, text):
        if not user.do_not_disturb:
            smtp_send(user.email, text)
```

## Why it's bad

- Two things vary — how a message is delivered, and what urgency does to it — and inheritance can only express
  one of them. So the classes enumerate pairs, and the next transport adds one class per urgency while the next
  urgency adds one per transport.
- The urgency rule is written once per transport. `"URGENT: "` and "also tell the manager" appear in two
  classes that share no code, so changing the escalation rule means finding all of them and the compiler will
  not help.
- The combinations that nobody wrote are indistinguishable from the ones nobody wanted. There is no
  `QuietSmsNotifier`, and nothing says whether that is a deliberate policy or an oversight.
- It presents as a bug fixed for email notifications and still live for SMS, or as a new channel that took a
  week because it was five classes rather than one.

## Better

```python
class EmailTransport:
    def deliver(self, person, text):
        smtp_send(person.email, text)


class SmsTransport:
    def deliver(self, person, text):
        sms_send(person.phone, text)


class Notifier:
    """The abstraction. Holds a transport rather than being one."""

    def __init__(self, transport):
        self._transport = transport

    def send(self, user, text):
        self._transport.deliver(user, text)


class UrgentNotifier(Notifier):
    def send(self, user, text):
        for person in (user, user.manager):
            self._transport.deliver(person, "URGENT: " + text)


class QuietNotifier(Notifier):
    def send(self, user, text):
        if not user.do_not_disturb:
            self._transport.deliver(user, text)
```

Three urgencies and two transports are now five classes instead of six, and a third transport adds one class
rather than three. The escalation rule exists once, so changing it is one edit.
