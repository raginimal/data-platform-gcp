# Prompt Review Skill

- Skill ID: `AI-SK-002`
- Version: `1.0.0`
- Owner: AI owner placeholder
- Applicable policies: `AI-PRM-001` through `AI-PRM-004`, `AI-002`, `SEC-SEC-004`

## Purpose
Review prompt versioning, secrets, sensitive data, injection resistance, grounding, tool use, output contracts, and evaluation evidence.

## When to run
Run for prompt, instruction, retrieval, tool-use, or guardrail changes.

## Inputs
Prompt diff, model configuration, data classification, grounding sources, guardrails, and evaluation evidence.

## Analysis procedure
Separate trusted instructions from untrusted content, check for secret/data leakage, identify injection paths, and require evaluation for material behavior changes.

## Expected output
Report evidence, confidence, policy ID, recommendation, and required human review.

## Human review

AI, security, and data owners review prompts that affect decisions, tools, sensitive data, or safety behavior.
