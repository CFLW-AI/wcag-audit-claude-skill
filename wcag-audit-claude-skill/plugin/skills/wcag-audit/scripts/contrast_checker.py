#!/usr/bin/env python3
"""
WCAG 2.2 Color Contrast Verification Utilities

Implements the exact WCAG relative luminance and contrast ratio formulas.
Use these functions to programmatically verify all color pairs on a page.

Usage as a library:
    from contrast_checker import contrast_ratio, check_pair, find_passing_color

Usage standalone (demo):
    python3 contrast_checker.py
"""

import sys
import json
from typing import Tuple, List, Optional


def hex_to_rgb(h: str) -> Tuple[float, float, float]:
    """Convert hex color to normalized RGB (0.0-1.0)."""
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def relative_luminance(r: float, g: float, b: float) -> float:
    """
    Compute relative luminance per WCAG 2.2 definition.
    https://www.w3.org/TR/WCAG22/#dfn-relative-luminance
    Input: r, g, b as floats in [0.0, 1.0]
    """
    def linearize(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def contrast_ratio(hex1: str, hex2: str) -> float:
    """
    Compute contrast ratio between two hex colors.
    Returns a value >= 1.0 (e.g., 4.5 for 4.5:1).
    """
    l1 = relative_luminance(*hex_to_rgb(hex1))
    l2 = relative_luminance(*hex_to_rgb(hex2))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def check_pair(label: str, fg: str, bg: str, min_ratio: float = 4.5) -> dict:
    """
    Check a single foreground/background pair against a minimum ratio.
    Returns a dict with label, colors, ratio, required, and pass/fail.
    """
    cr = contrast_ratio(fg, bg)
    return {
        "label": label,
        "foreground": fg,
        "background": bg,
        "ratio": round(cr, 2),
        "required": min_ratio,
        "passes": cr >= min_ratio
    }


def check_all(pairs: List[Tuple[str, str, str, float]]) -> dict:
    """
    Check a list of (label, fg, bg, min_ratio) tuples.
    Returns summary with individual results and totals.
    """
    results = []
    for label, fg, bg, min_ratio in pairs:
        results.append(check_pair(label, fg, bg, min_ratio))

    total = len(results)
    passed = sum(1 for r in results if r["passes"])

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "all_pass": passed == total,
        "results": results
    }


def rgba_on_bg(fg_hex: str, alpha: float, bg_hex: str) -> str:
    """
    Compute the effective opaque color when an rgba foreground is composited
    on a known background. Useful for checking semi-transparent overlays.

    Returns the resulting hex color string.
    """
    fr, fg_g, fb = hex_to_rgb(fg_hex)
    br, bg_g, bb = hex_to_rgb(bg_hex)

    r = fr * alpha + br * (1 - alpha)
    g = fg_g * alpha + bg_g * (1 - alpha)
    b = fb * alpha + bb * (1 - alpha)

    return '#{:02x}{:02x}{:02x}'.format(
        int(round(r * 255)),
        int(round(g * 255)),
        int(round(b * 255))
    )


def find_passing_color(base_hex: str, bg_hex: str, min_ratio: float = 4.5,
                        direction: str = "darken", steps: int = 100) -> Optional[str]:
    """
    Starting from base_hex, progressively darken or lighten until the color
    passes min_ratio against bg_hex. Returns the first passing color, or None.

    This is useful for finding the minimum adjustment to fix a failing color
    while preserving as much of the original hue as possible.
    """
    r, g, b = hex_to_rgb(base_hex)

    for i in range(1, steps + 1):
        factor = i / steps
        if direction == "darken":
            nr = r * (1 - factor)
            ng = g * (1 - factor)
            nb = b * (1 - factor)
        else:  # lighten
            nr = r + (1 - r) * factor
            ng = g + (1 - g) * factor
            nb = b + (1 - b) * factor

        candidate = '#{:02x}{:02x}{:02x}'.format(
            int(round(nr * 255)),
            int(round(ng * 255)),
            int(round(nb * 255))
        )

        if contrast_ratio(candidate, bg_hex) >= min_ratio:
            return candidate

    return None


def print_results(summary: dict) -> None:
    """Pretty-print contrast check results to stdout."""
    for r in summary["results"]:
        status = "PASS ✅" if r["passes"] else "FAIL ❌"
        print(f"  {r['label']}: {r['foreground']} on {r['background']} "
              f"→ {r['ratio']}:1 (need {r['required']}:1) [{status}]")

    print()
    print(f"{'=' * 60}")
    total, passed = summary["total"], summary["passed"]
    print(f"TOTALS: {passed}/{total} pairs pass")
    if summary["all_pass"]:
        print("🎉 ALL COLOR CONTRAST CHECKS PASS WCAG 2.2 AA!")
    else:
        print(f"⚠️  {summary['failed']} pair(s) failing")
    print(f"{'=' * 60}")


# --- Demo / standalone usage ---
if __name__ == "__main__":
    print("WCAG 2.2 Contrast Checker — Demo")
    print("=" * 60)

    demo_pairs = [
        ("Black on white", "#000000", "#ffffff", 4.5),
        ("Dark gray on white", "#595959", "#ffffff", 4.5),
        ("Medium gray on white", "#767676", "#ffffff", 4.5),
        ("Light gray on white (likely fail)", "#999999", "#ffffff", 4.5),
        ("Focus indicator (3:1)", "#767676", "#ffffff", 3.0),
    ]

    summary = check_all(demo_pairs)
    print_results(summary)

    print()
    print("--- find_passing_color demo ---")
    failing = "#999999"
    bg = "#ffffff"
    fixed = find_passing_color(failing, bg, 4.5, "darken")
    if fixed:
        cr = contrast_ratio(fixed, bg)
        print(f"  {failing} fails on {bg}")
        print(f"  Darkened to {fixed} → {cr:.2f}:1 ✅")
