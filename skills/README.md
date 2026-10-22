# Skills

Skills are reusable, versioned analysis contracts. They define how a focused review is performed; they do not execute commands or make approvals by themselves.

Each skill has a stable ID, owner, applicable policies, trigger, inputs, procedure, output contract, severity/confidence guidance, and human review requirements.

The [`foundation`](foundation/SKILL.md) skill provides repository lifecycle commands for assessing, initializing, and
adopting the foundation. Its deterministic helper is `skills/foundation/foundation.py`; it delegates quality checks to
the vendored Plumbline gate and keeps human approvals outside automation.
