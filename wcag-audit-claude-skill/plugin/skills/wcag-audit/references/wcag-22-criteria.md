# WCAG 2.2 Level AA Success Criteria — Audit Checklist

All 28 success criteria that apply at Level AA, organized by principle.
For each criterion, the "What to check" section describes what to look for in the source code.

---

## Principle 1: Perceivable

### SC 1.1.1 Non-text Content (Level A)
Every `<img>` needs meaningful `alt` text (or `alt=""` if decorative). `<canvas>`, `<svg>`,
icon fonts, and CSS background images used to convey info also need text alternatives.
Check `<video>` and `<audio>` poster images. Role="img" elements need `aria-label`.

### SC 1.2.1 Audio-only and Video-only (Level A)
Pre-recorded audio-only needs a transcript. Pre-recorded video-only needs a transcript or
audio description. If the page has no audio/video, mark N/A.

### SC 1.2.2 Captions (Prerecorded) (Level A)
Pre-recorded video with audio needs synchronized captions (`<track kind="captions">`).
Auto-generated captions don't count unless they've been reviewed for accuracy.

### SC 1.2.3 Audio Description or Media Alternative (Level A)
Pre-recorded video needs either audio description track or a full text transcript.

### SC 1.2.5 Audio Description (Level AA)
Pre-recorded video content needs audio description track for visual-only information.

### SC 1.3.1 Info and Relationships (Level A)
Semantic HTML is the key check here:
- Headings use `<h1>`–`<h6>` (not styled `<div>`s)
- Lists use `<ul>`/`<ol>`/`<dl>`
- Tables have `<th>` and `scope` attributes
- Form inputs have associated `<label>` elements
- Landmark regions: `<header>`, `<nav>`, `<main>`, `<footer>`
- Programmatic relationships match visual relationships

### SC 1.3.2 Meaningful Sequence (Level A)
DOM order matches visual order. CSS layout (flexbox `order`, grid, `position: absolute`)
shouldn't create a reading order that contradicts the source order.

### SC 1.3.3 Sensory Characteristics (Level A)
Instructions don't rely solely on shape, color, size, visual location, or sound.
"Click the green button" fails. "Click Submit" or "Click the green Submit button" passes.

### SC 1.4.1 Use of Color (Level A)
Color isn't the only way to convey information. Links need underlines (or other non-color
indicator), form errors need icon/text in addition to red highlighting, chart data needs
patterns in addition to color coding.

### SC 1.4.2 Audio Control (Level A)
Audio that plays automatically for >3 seconds must have pause/stop/volume control.

### SC 1.4.3 Contrast (Minimum) (Level AA)
**This is where programmatic checking happens.**
- Normal text (< 18pt / < 14pt bold): **4.5:1** minimum
- Large text (≥ 18pt / ≥ 14pt bold): **3:1** minimum
- Check ALL themes/modes
- Disabled controls and decorative text are exempt

### SC 1.4.4 Resize Text (Level AA)
Text can be resized up to 200% without loss of content or functionality.
Check: no `overflow: hidden` cutting off text at 200% zoom, no fixed-height containers
that clip enlarged text.

### SC 1.4.5 Images of Text (Level AA)
Don't use images for text that could be rendered as actual text.
Exceptions: logos, text that's part of a photo/illustration.

### SC 1.4.10 Reflow (Level AA)
Content reflows at 320px width (400% zoom on a 1280px viewport) without horizontal
scrolling. Check for fixed-width containers, `overflow-x: auto` on body content,
two-dimensional scrolling requirements. Data tables and complex diagrams are exempt.

### SC 1.4.11 Non-text Contrast (Level AA)
**3:1 ratio** required for:
- UI component boundaries (form field borders, button outlines)
- Focus indicators (outlines, rings)
- Graphical objects needed to understand content (icons, chart segments)
- Custom form controls (checkboxes, toggles, sliders)

### SC 1.4.12 Text Spacing (Level AA)
Content must remain functional with: line height ≥ 1.5× font size, paragraph spacing ≥ 2×
font size, letter spacing ≥ 0.12× font size, word spacing ≥ 0.16× font size.
Check: no `overflow: hidden` on text containers that would clip adjusted text.

### SC 1.4.13 Content on Hover or Focus (Level AA)
Hover/focus-triggered content (tooltips, dropdowns) must be: dismissable (Escape),
hoverable (user can move to the tooltip), persistent (stays until dismissed).

---

## Principle 2: Operable

### SC 2.1.1 Keyboard (Level A)
All functionality available via keyboard. Check: can Tab reach every interactive element?
Do custom controls work with Enter/Space? Do dropdowns work with arrow keys?
No keyboard traps (can always Tab away).

### SC 2.1.2 No Keyboard Trap (Level A)
Focus can always move away from any component using standard keys (Tab, Shift+Tab, Escape).
Modals must trap focus within themselves but release it when closed.

### SC 2.4.3 Focus Order (Level A)
Tab order follows a logical reading sequence. Check `tabindex` values — positive `tabindex`
disrupts natural order. `-1` is fine (programmatic focus only). `0` is fine (natural order).

### SC 2.4.5 Multiple Ways (Level AA)
At least two ways to locate a page within a site: navigation menu, site map, search,
table of contents, links between pages. Single-page apps: provide navigation or TOC.

### SC 2.4.6 Headings and Labels (Level AA)
Headings and labels describe the topic or purpose. Generic labels like "Click here" or
"Read more" fail unless context makes the purpose clear.

### SC 2.4.7 Focus Visible (Level AA)
Interactive elements show a visible focus indicator. Check `:focus-visible` and `:focus`
styles. If `outline: none` appears, verify a replacement is provided. Browser defaults
are acceptable but custom styles are preferred for clarity.

### SC 2.4.11 Focus Not Obscured (Minimum) (Level AA) — **New in WCAG 2.2**
When an element receives keyboard focus, it's not entirely hidden by other content
(sticky headers, footers, modals, notifications). Partially obscured is OK at AA level.
Check `z-index` layering, `position: sticky/fixed` elements.

### SC 2.5.3 Label in Name (Level A)
For elements with visible text labels, the accessible name includes that visible text.
Button text "Search" should have accessible name that contains "Search" (not just
`aria-label="Find"` when the visible text says "Search").

### SC 2.5.8 Target Size (Minimum) (Level AA) — **New in WCAG 2.2**
Interactive targets must be at least **24×24 CSS pixels**, OR have sufficient spacing
(so a 24px circle centered on the target doesn't intersect other targets).
Common failures: small navigation dots, tiny close buttons, densely packed icon buttons,
inline links in body text (exempt due to being inline with text flow).
Fix: use `::before`/`::after` pseudo-elements to create invisible 24px hit areas.

---

## Principle 3: Understandable

### SC 3.1.1 Language of Page (Level A)
`<html>` element has a valid `lang` attribute (e.g., `lang="en"`).

### SC 3.1.2 Language of Parts (Level AA)
Content in a different language than the page default has `lang` attribute on its container.

---

## Principle 4: Robust

### SC 4.1.2 Name, Role, Value (Level A)
Custom interactive components expose correct name, role, and state to assistive tech.
Check: `role` attributes, `aria-label`/`aria-labelledby`, `aria-expanded`,
`aria-selected`, `aria-current`, `aria-checked` on custom controls.

---

## Summary Count

| Level | Count |
|-------|-------|
| A     | 16    |
| AA    | 12    |
| **Total** | **28** |

Note: WCAG 2.2 removed SC 4.1.1 (Parsing) from Level A, so the total is 28, not 29.
SC 2.4.11 and SC 2.5.8 are the two new criteria added in WCAG 2.2.
