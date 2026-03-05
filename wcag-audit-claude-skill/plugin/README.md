# WCAG 2.2 Audit Plugin

Comprehensive WCAG 2.2 Level AA accessibility auditing for web pages and HTML files.

## What it does

This plugin adds a skill that performs rigorous accessibility audits against all 28 WCAG 2.2 AA success criteria. It combines manual code review with programmatic contrast verification using the WCAG relative luminance formula.

## How to use

Ask Claude to audit any web page or HTML file for accessibility. Trigger phrases include:

- "Is this page WCAG compliant?"
- "Run an accessibility audit on this URL"
- "Check the contrast ratios on this page"
- "Does this HTML meet WCAG 2.2?"

The skill accepts URLs, local HTML files, or uploaded files as input.

## Evaluation results

Tested across 10 purpose-built test pages with 56 documented accessibility failures:

- **100% true positive rate** — all 56 known failures detected
- **0 false positives** — verified by manual investigation
- **28 success criteria** covered across all four WCAG principles
- Caught real SC 1.4.11 failures that the test designer missed

## Components

| Component | Purpose |
|-----------|---------|
| `skills/wcag-audit` | Core audit workflow and methodology |
| `scripts/contrast_checker.py` | Programmatic WCAG contrast ratio computation |
| `references/wcag-22-criteria.md` | Complete 28-criteria checklist |
