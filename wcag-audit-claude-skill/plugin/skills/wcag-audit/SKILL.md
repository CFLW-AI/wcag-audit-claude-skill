---
name: wcag-audit
description: >
  Perform a comprehensive WCAG 2.2 AA accessibility audit on any web page or HTML file, with
  programmatic color contrast verification and a professional styled audit report. Use this skill
  whenever the user asks about accessibility compliance, WCAG conformance, color contrast checking,
  or wants to know if a page "passes" accessibility standards. Also trigger when the user mentions
  "accessibility audit", "a11y check", "WCAG 2.2", "contrast ratio", "screen reader compatible",
  "ADA compliant", or asks whether a website or HTML file meets accessibility requirements. If the
  user asks to FIX accessibility issues after the audit, this skill also covers the remediation
  workflow. Trigger broadly — if accessibility or WCAG is mentioned at all, this skill applies.
---

# WCAG 2.2 AA Accessibility Audit

This skill performs a rigorous, systematic accessibility audit against all 28 WCAG 2.2 Level AA
success criteria. It combines manual code review with programmatic contrast verification to produce
a professional audit report.

What makes this audit valuable is that it doesn't just eyeball things — it extracts every color
pair from the CSS, computes contrast ratios using the WCAG relative luminance formula, and tests
them all against the required thresholds. This catches issues that visual inspection misses,
especially in alternate themes.

## Accepted Inputs

- **URL** — Fetch the live page via `curl -s -L` and audit the source
- **Local/uploaded HTML file** — Read from the filesystem directly
- **Screenshot** — For visual-only checks (contrast estimation, target size, layout), note in the
  report that only visual criteria could be evaluated

## Workflow Overview

### Phase 1: Source Acquisition

For URLs, fetch the raw HTML:
```bash
curl -s -L "<url>" -o source.html
```

For uploaded files, copy to the working directory. Read the entire file — you need to see all CSS
custom properties, media queries, JavaScript-driven state changes, and ARIA attributes.

### Phase 2: CSS Color Extraction

This is the foundation of the audit. You need to find **every foreground/background color pair**
that appears in the rendered page. This means:

1. **CSS custom properties** (e.g., `--text-primary`, `--bg`, `--accent`) from `:root` and any
   theme variants (`[data-theme="light"]`, `[data-theme="dark"]`, `@media (prefers-color-scheme: ...)`)
2. **Hardcoded colors** in element styles (hex, rgb, hsl, named colors)
3. **Contextual pairs** — colors that sit on top of specific backgrounds (e.g., text inside cards
   where the card has its own background, colored badge text on badge backgrounds, white text on
   accent-colored circles)
4. **Interactive state colors** — hover, focus, active states
5. **Computed overlay colors** — if `rgba()` values are used on known backgrounds, compute the
   effective opaque color

Build a complete list of `(label, foreground, background, required_ratio)` tuples. The required
ratio is:
- **4.5:1** for normal text (< 18pt or < 14pt bold)
- **3:1** for large text (≥ 18pt or ≥ 14pt bold)
- **3:1** for non-text contrast (UI components, focus indicators, graphical objects per SC 1.4.11)

### Phase 3: Programmatic Contrast Verification

Run the bundled contrast checker script against all extracted pairs. This script implements the
exact WCAG relative luminance algorithm:

```bash
python3 <skill-path>/scripts/contrast_checker.py
```

But because each page has different colors, you'll write a verification script specific to the page
being audited. Use the contrast functions from `scripts/contrast_checker.py` as your foundation
(import or copy them), then define all the color pairs you extracted in Phase 2.

The script should output:
- Each pair with its computed ratio and PASS/FAIL status
- A summary line: `X/Y pairs pass`

### Phase 4: Manual Criteria Review

Evaluate all 28 WCAG 2.2 AA success criteria against the source code. See
`references/wcag-22-criteria.md` for the complete checklist with what to look for in each.

Key things that catch people off guard and deserve extra attention:

**SC 1.3.1 Info and Relationships** — Semantic HTML matters. Are headings actual `<h1>`–`<h6>`?
Are lists `<ul>`/`<ol>`? Are form labels associated with inputs via `for`/`id`?

**SC 1.4.11 Non-text Contrast** — This isn't just about text. Focus outlines, form field borders,
icon-only buttons, chart segments, custom checkboxes — all need 3:1 against adjacent colors.

**SC 2.4.7 Focus Visible** — Every interactive element must show a visible focus indicator.
Check `:focus-visible` styles. If `outline: none` appears without a replacement, that's a fail.

**SC 2.5.8 Target Size (Minimum)** — New in WCAG 2.2. All interactive targets need at least
24×24 CSS pixels, *or* have sufficient spacing from adjacent targets. Small dots, tiny icons,
and inline links in dense text are common failures. The `::before`/`::after` pseudo-element
technique (invisible expanded touch target) is a valid fix.

**SC 2.4.11 Focus Not Obscured (Minimum)** — New in WCAG 2.2. Focus indicator must not be
entirely hidden by other content. Check for `z-index` issues, sticky headers covering focused
elements, overlapping modals.

### Phase 5: Report Generation

Generate a professional, self-contained HTML audit report. The report should be visually polished
— this is a deliverable the user may share with stakeholders.

Report structure:
1. **Header** — page title, URL, audit date
2. **Verdict banner** — PASS (green) or FAIL (red) with summary counts
3. **KPI cards** — criteria checked, pass count, fail count, warning count
4. **Color contrast table** — every pair tested, with foreground/background swatches,
   computed ratio, required ratio, and pass/fail badge
5. **Full criteria review table** — all 28 criteria with status and evidence/notes
6. **Footer** — methodology note, audit date

Design notes for the report HTML:
- Self-contained (inline CSS, no external dependencies except Google Fonts)
- Support both light and dark modes via `@media (prefers-color-scheme)`
- Use `prefers-reduced-motion: reduce` to disable animations
- Professional editorial aesthetic: clean typography (IBM Plex Sans/Mono or similar),
  subtle animations, color-coded badges
- Responsive layout

## Remediation Workflow (When Requested)

If the user asks to fix the issues found in the audit, follow this process:

### Fix Strategy

1. **Color contrast failures** — Darken (for light backgrounds) or lighten (for dark backgrounds)
   the failing color. Use `scripts/contrast_checker.py` to find the minimum adjustment that passes.
   Choose the closest passing color to preserve the original design intent — don't over-correct.
   If a color serves as both text foreground AND background for other text (e.g., accent-colored
   circles with white text), verify both directions.

2. **Target size failures** — Use the invisible `::before` pseudo-element technique:
   ```css
   .small-target {
       position: relative;
   }
   .small-target::before {
       content: '';
       position: absolute;
       top: 50%; left: 50%;
       transform: translate(-50%, -50%);
       width: 24px; height: 24px;
   }
   ```
   This expands the touch area without changing the visual design.

3. **Focus indicator failures** — Ensure `:focus-visible` outline has 3:1 contrast against
   adjacent colors and add `z-index: 10` so it isn't obscured.

4. **Structural/semantic fixes** — Add missing ARIA attributes, fix heading hierarchy,
   associate labels with inputs, add `aria-current` for active navigation states.

5. **Missing meta tags** — Add `<meta name="color-scheme" content="dark light">` if the page
   supports both themes.

### After Fixing

Re-run the full audit (Phases 2–5) on the fixed HTML and generate a new report. The fixed-version
report should include a "Changes Applied" section documenting each fix with before/after values.

## File Organization

Save outputs to the workspace folder:
- `wcag-audit-report.html` — The audit report
- The fixed HTML (if remediation was requested), named descriptively (e.g., `page-fixed.html`)

## Common Pitfalls

- **Theme variants are easy to miss.** If the page has light/dark modes, test BOTH. Most failures
  hide in the less-tested theme.
- **rgba() on varying backgrounds.** Compute the effective opaque color before checking contrast.
  `rgba(0,0,0,0.5)` on `#ffffff` is `#808080`, not `#000000`.
- **Hover/focus states.** These need their own contrast checks — a link that passes in its default
  state might fail on hover if the hover color is lighter.
- **Text on images/gradients.** If text sits on a non-uniform background, check contrast against
  the worst-case (lightest) area behind the text.
