# WCAG 2.2 Audit — Claude Cowork Skill

A Claude Cowork plugin that performs comprehensive WCAG 2.2 Level AA accessibility audits on web pages and HTML files, with programmatic contrast verification and professional audit reports.

## Results

Evaluated across 10 purpose-built test pages with 56 documented accessibility failures covering all 28 WCAG 2.2 AA success criteria:

| Metric | Result |
|--------|--------|
| True positive rate | **100%** (56/56 known failures detected) |
| False negatives | **0** |
| False positives | **0** (verified by manual investigation) |
| SC coverage | **28/28** WCAG 2.2 AA criteria |

The skill also caught real SC 1.4.11 non-text contrast failures in the "fully compliant" test page that the test designer had missed — demonstrating its thoroughness for programmatic contrast checking where visual inspection is unreliable.

[View the full evaluation report →](https://cflw-ai.github.io/wcag-audit-claude-skill/eval-report.html)

## Install

Download [`wcag-audit.plugin`](./wcag-audit.plugin) and open it in Claude Desktop. The plugin will appear as an installable card — click Accept to install.

Alternatively, copy the `plugin/` directory into your Claude skills folder.

## Usage

Ask Claude to audit any web page or HTML file. Trigger phrases include:

- "Is this page WCAG compliant?"
- "Run an accessibility audit on this URL"
- "Check the contrast ratios on this page"
- "Does this HTML meet WCAG 2.2?"

The skill accepts URLs, local HTML files, or uploaded files as input.

## How It Works

The audit follows a 5-phase methodology:

1. **Source Acquisition** — Fetch the page via URL or read from the filesystem
2. **CSS Color Extraction** — Parse every color declaration from stylesheets
3. **Programmatic Contrast Verification** — Compute contrast ratios using the WCAG relative luminance formula via `contrast_checker.py`
4. **Manual Criteria Review** — Evaluate all 28 success criteria through code analysis
5. **Report Generation** — Produce a professional styled HTML audit report

## Repository Structure

```
├── wcag-audit.plugin          # Installable plugin file
├── plugin/                    # Plugin source files
│   ├── .claude-plugin/        #   Plugin manifest
│   └── skills/wcag-audit/     #   Skill, scripts, and WCAG criteria reference
├── evals/                     # Evaluation suite
│   ├── test-pages/            #   10 test pages with ground truth (HTML comments)
│   ├── reports/               #   Audit reports generated during evaluation
│   ├── grade_all.py           #   Automated grading script
│   └── grading_results.json   #   Structured results
├── docs/                      # GitHub Pages
│   └── eval-report.html       #   Interactive evaluation dashboard
└── original-work/             # Original OKLIS-2026 audit that inspired this skill
    ├── index.html             #   WCAG-fixed presentation
    └── audit-report.html      #   Audit report for the fixed version
```

## Evaluation Test Pages

| # | Focus Area | Known Failures | Detected |
|---|-----------|---------------|----------|
| 01 | Subtle contrast (borderline ratios, rgba, non-text) | 5 | 5 |
| 02 | Semantic structure (headings, landmarks, lang) | 8 | 8 |
| 03 | Keyboard & focus (traps, visibility, tabindex) | 7 | 7 |
| 04 | WCAG 2.2 specific (target size, focus obscured) | 4 | 4 |
| 05 | Form accessibility (labels, fieldsets, ARIA) | 7 | 7 |
| 06 | Media (alt text, captions, transcripts) | 7 | 7 |
| 07 | Fully compliant (false positive test) | 0* | — |
| 08 | Dynamic content (widgets, ARIA states, live regions) | 6 | 6 |
| 09 | Color-only information (links, status, errors) | 6 | 6 |
| 10 | Responsive & reflow (viewport, text resize, spacing) | 6 | 6 |

*Page 07 was designed to be fully compliant, but the audit correctly found real SC 1.4.11 border contrast failures in the dark theme that the designer missed.

## Limitations

This skill performs static code analysis. It cannot test dynamic interactions in a live browser (e.g., actual keyboard navigation, screen reader behavior, or JavaScript-driven state changes). For full compliance verification, combine this audit with manual testing using assistive technologies.

## License

MIT
