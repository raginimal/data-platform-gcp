# AI Evaluation Review Skill

- Skill ID: `AI-SK-003`
- Version: `1.0.0`
- Owner: AI evaluation owner placeholder
- Applicable policies: `AI-EVAL-001` through `AI-EVAL-005`, `AI-004`

## Purpose
Review evaluation purpose, dataset permission, metrics, thresholds, regression coverage, human review, and release behavior.

## When to run
Run for model, prompt, RAG, tool, guardrail, or AI workflow changes that can alter behavior.

## Inputs
Evaluation definition, dataset metadata, baseline results, regression results, thresholds, and release decision.

## Analysis procedure
Check representative and adversarial coverage, privacy, threshold interpretation, failure policy, evaluator limitations, and production monitoring.

## Expected output
Never present an AI-generated score as sufficient evidence. Reference `AI-EVAL-*` and identify human decision points.

## Human review

AI evaluation and risk owners decide whether thresholds, dataset limitations, or ambiguous results permit release.
