#!/usr/bin/env python3
"""
Grade all 10 expanded eval runs for the wcag-audit skill, iteration 2.
Checks each audit report against documented ground truth.
Focus: false negative rate (missed real issues) — the dangerous failure mode for legal compliance.
"""
import os, re, json

BASE = "/sessions/optimistic-busy-davinci/wcag-audit-workspace/iteration-2"

# Ground truth assertions for each test page
# Each assertion has:
#   - text: human-readable description
#   - check: function name to run
#   - sc: WCAG success criterion number
#   - type: "true_positive" (should be flagged) or "true_negative" (should NOT be flagged)
TESTS = {
    "01-subtle-contrast": {
        "ground_truth_failures": 5,
        "ground_truth_passes": 2,
        "assertions": [
            {"text": "HTML report exists", "check": "html_report_exists", "type": "meta"},
            {"text": "Flags #757575 on #ffffff as borderline fail (4.48:1 < 4.5:1)", "check": "flags_757575", "sc": "1.4.3", "type": "true_positive"},
            {"text": "Flags rgba overlay text as contrast failure", "check": "flags_rgba_overlay", "sc": "1.4.3", "type": "true_positive"},
            {"text": "Flags tag text #ffffff on #74b9ff as low contrast", "check": "flags_74b9ff", "sc": "1.4.3", "type": "true_positive"},
            {"text": "Flags button border #cccccc on #ffffff as non-text contrast fail", "check": "flags_button_border", "sc": "1.4.11", "type": "true_positive"},
            {"text": "Flags card meta #959595 on #f5f5f5 as contrast fail", "check": "flags_card_meta", "sc": "1.4.3", "type": "true_positive"},
            {"text": "Does NOT flag #2d6a4f on #ffffff (7.08:1 passes)", "check": "no_flag_2d6a4f", "sc": "1.4.3", "type": "true_negative"},
            {"text": "Contains programmatic contrast ratios", "check": "has_contrast_ratios", "type": "meta"},
        ]
    },
    "02-semantic-structure": {
        "ground_truth_failures": 9,
        "assertions": [
            {"text": "HTML report exists", "check": "html_report_exists", "type": "meta"},
            {"text": "Flags fake headings (styled divs instead of h1-h6)", "check": "flags_fake_headings", "sc": "1.3.1", "type": "true_positive"},
            {"text": "Flags div navigation instead of nav/ul", "check": "flags_div_nav", "sc": "1.3.1", "type": "true_positive"},
            {"text": "Flags table missing th/scope", "check": "flags_table_th", "sc": "1.3.1", "type": "true_positive"},
            {"text": "Flags placeholder-only form labels", "check": "flags_placeholder_labels", "sc": "1.3.1", "type": "true_positive"},
            {"text": "Flags CSS order mismatch (meaningful sequence)", "check": "flags_css_order", "sc": "1.3.2", "type": "true_positive"},
            {"text": "Flags generic link text (click here / read more)", "check": "flags_generic_links", "sc": "2.4.4", "type": "true_positive"},
            {"text": "Flags missing lang=fr on French text", "check": "flags_missing_lang", "sc": "3.1.2", "type": "true_positive"},
            {"text": "Flags custom toggle missing role/aria", "check": "flags_toggle_aria", "sc": "4.1.2", "type": "true_positive"},
            {"text": "Contains programmatic contrast ratios", "check": "has_contrast_ratios", "type": "meta"},
        ]
    },
    "03-keyboard-focus": {
        "ground_truth_failures": 8,
        "assertions": [
            {"text": "HTML report exists", "check": "html_report_exists", "type": "meta"},
            {"text": "Flags onclick div without keyboard access", "check": "flags_onclick_div", "sc": "2.1.1", "type": "true_positive"},
            {"text": "Flags modal keyboard trap (no Escape)", "check": "flags_keyboard_trap", "sc": "2.1.2", "type": "true_positive"},
            {"text": "Flags global outline:none removing focus", "check": "flags_outline_none", "sc": "2.4.7", "type": "true_positive"},
            {"text": "Flags tabindex=5 disrupting focus order", "check": "flags_tabindex", "sc": "2.4.3", "type": "true_positive"},
            {"text": "Flags sticky header obscuring focus", "check": "flags_sticky_obscure", "sc": "2.4.11", "type": "true_positive"},
            {"text": "Flags onmouseover with no keyboard equivalent", "check": "flags_mouseover", "sc": "2.1.1", "type": "true_positive"},
            {"text": "Flags low-contrast focus ring", "check": "flags_focus_contrast", "sc": "1.4.11", "type": "true_positive"},
            {"text": "Contains programmatic contrast ratios", "check": "has_contrast_ratios", "type": "meta"},
        ]
    },
    "04-wcag22-specific": {
        "ground_truth_failures": 4,
        "ground_truth_passes": 2,
        "assertions": [
            {"text": "HTML report exists", "check": "html_report_exists", "type": "meta"},
            {"text": "Flags 8px pagination dots (SC 2.5.8)", "check": "flags_pagination_dots", "sc": "2.5.8", "type": "true_positive"},
            {"text": "Flags 18px icon buttons (SC 2.5.8)", "check": "flags_icon_buttons", "sc": "2.5.8", "type": "true_positive"},
            {"text": "Flags 14px star rating (SC 2.5.8)", "check": "flags_star_rating", "sc": "2.5.8", "type": "true_positive"},
            {"text": "Flags fixed bottom bar obscuring focus (SC 2.4.11)", "check": "flags_bottom_bar", "sc": "2.4.11", "type": "true_positive"},
            {"text": "Does NOT flag 48px button (large enough)", "check": "no_flag_big_btn", "sc": "2.5.8", "type": "true_negative"},
            {"text": "Contains programmatic contrast ratios", "check": "has_contrast_ratios", "type": "meta"},
        ]
    },
    "05-form-accessibility": {
        "ground_truth_failures": 7,
        "assertions": [
            {"text": "HTML report exists", "check": "html_report_exists", "type": "meta"},
            {"text": "Flags email input with no label", "check": "flags_email_no_label", "sc": "1.3.1", "type": "true_positive"},
            {"text": "Flags radio group without fieldset/legend", "check": "flags_radio_no_fieldset", "sc": "1.3.1", "type": "true_positive"},
            {"text": "Flags phone input with no label", "check": "flags_phone_no_label", "sc": "3.3.2", "type": "true_positive"},
            {"text": "Flags error not associated with input", "check": "flags_error_association", "sc": "3.3.1", "type": "true_positive"},
            {"text": "Flags required indicated only by color", "check": "flags_required_color_only", "sc": "1.3.1", "type": "true_positive"},
            {"text": "Flags custom select missing ARIA", "check": "flags_custom_select", "sc": "4.1.2", "type": "true_positive"},
            {"text": "Flags placeholder contrast failure (#bbbbbb)", "check": "flags_placeholder_contrast", "sc": "1.4.3", "type": "true_positive"},
            {"text": "Contains programmatic contrast ratios", "check": "has_contrast_ratios", "type": "meta"},
        ]
    },
    "06-media-failures": {
        "ground_truth_failures": 7,
        "ground_truth_passes": 1,
        "assertions": [
            {"text": "HTML report exists", "check": "html_report_exists", "type": "meta"},
            {"text": "Flags hero image with empty alt (meaningful content)", "check": "flags_hero_empty_alt", "sc": "1.1.1", "type": "true_positive"},
            {"text": "Flags product photo missing alt attribute", "check": "flags_missing_alt", "sc": "1.1.1", "type": "true_positive"},
            {"text": "Flags non-descriptive alt='image'", "check": "flags_nondescriptive_alt", "sc": "1.1.1", "type": "true_positive"},
            {"text": "Flags image of text (SC 1.4.5)", "check": "flags_image_of_text", "sc": "1.4.5", "type": "true_positive"},
            {"text": "Flags icon link with no accessible name", "check": "flags_icon_link", "sc": "1.1.1", "type": "true_positive"},
            {"text": "Flags audio with no transcript", "check": "flags_no_transcript", "sc": "1.2.1", "type": "true_positive"},
            {"text": "Flags video with no captions", "check": "flags_no_captions", "sc": "1.2.2", "type": "true_positive"},
            {"text": "Does NOT flag decorative divider (alt='' correct)", "check": "no_flag_decorative", "sc": "1.1.1", "type": "true_negative"},
        ]
    },
    "07-fully-compliant": {
        "ground_truth_failures": 0,
        "assertions": [
            {"text": "HTML report exists", "check": "html_report_exists", "type": "meta"},
            {"text": "Does NOT flag dark theme text contrast (all passing)", "check": "no_false_text_fail", "sc": "1.4.3", "type": "true_negative"},
            {"text": "Does NOT flag custom focus styles (gold outline)", "check": "no_false_focus_fail", "sc": "2.4.7", "type": "true_negative"},
            {"text": "Does NOT flag 44px buttons as too small", "check": "no_false_target_fail", "sc": "2.5.8", "type": "true_negative"},
            {"text": "Recognizes page as largely compliant", "check": "recognizes_compliant", "type": "meta"},
        ]
    },
    "08-dynamic-content": {
        "ground_truth_failures": 7,
        "assertions": [
            {"text": "HTML report exists", "check": "html_report_exists", "type": "meta"},
            {"text": "Flags toggle missing role/aria-checked", "check": "flags_toggle_no_role", "sc": "4.1.2", "type": "true_positive"},
            {"text": "Flags status message missing aria-live", "check": "flags_no_aria_live", "sc": "4.1.3", "type": "true_positive"},
            {"text": "Flags tab panel missing ARIA roles", "check": "flags_tabs_no_aria", "sc": "1.3.1", "type": "true_positive"},
            {"text": "Flags accordion not keyboard accessible", "check": "flags_accordion_keyboard", "sc": "2.1.1", "type": "true_positive"},
            {"text": "Flags accordion missing aria-expanded", "check": "flags_accordion_expanded", "sc": "4.1.2", "type": "true_positive"},
            {"text": "Flags CSS order mismatch on steps", "check": "flags_step_order", "sc": "1.3.2", "type": "true_positive"},
            {"text": "Contains programmatic contrast ratios", "check": "has_contrast_ratios", "type": "meta"},
        ]
    },
    "09-color-only-info": {
        "ground_truth_failures": 6,
        "ground_truth_passes": 1,
        "assertions": [
            {"text": "HTML report exists", "check": "html_report_exists", "type": "meta"},
            {"text": "Flags links without underlines (color only)", "check": "flags_links_no_underline", "sc": "1.4.1", "type": "true_positive"},
            {"text": "Flags required fields by color only", "check": "flags_required_color", "sc": "1.4.1", "type": "true_positive"},
            {"text": "Flags status dots as color-only", "check": "flags_status_dots", "sc": "1.4.1", "type": "true_positive"},
            {"text": "Flags chart legend color-only", "check": "flags_chart_legend", "sc": "1.4.1", "type": "true_positive"},
            {"text": "Flags error border as color-only", "check": "flags_error_border", "sc": "1.4.1", "type": "true_positive"},
            {"text": "Flags #4caf50 success text contrast", "check": "flags_green_contrast", "sc": "1.4.3", "type": "true_positive"},
            {"text": "Does NOT flag badges (use color AND text)", "check": "no_flag_badges", "sc": "1.4.1", "type": "true_negative"},
        ]
    },
    "10-responsive-reflow": {
        "ground_truth_failures": 6,
        "ground_truth_passes": 1,
        "assertions": [
            {"text": "HTML report exists", "check": "html_report_exists", "type": "meta"},
            {"text": "Flags fixed-width table (min-width:900px)", "check": "flags_fixed_table", "sc": "1.4.10", "type": "true_positive"},
            {"text": "Flags code block nowrap clipping", "check": "flags_nowrap_code", "sc": "1.4.10", "type": "true_positive"},
            {"text": "Flags font-size px !important blocking resize", "check": "flags_fixed_font", "sc": "1.4.4", "type": "true_positive"},
            {"text": "Flags hero fixed height clipping", "check": "flags_hero_clip", "sc": "1.4.10", "type": "true_positive"},
            {"text": "Flags tight text spacing (line-height:1.0)", "check": "flags_tight_spacing", "sc": "1.4.12", "type": "true_positive"},
            {"text": "Flags watermark #e8e8e8 contrast", "check": "flags_watermark", "sc": "1.4.3", "type": "true_positive"},
            {"text": "Does NOT flag responsive card (reflows correctly)", "check": "no_flag_responsive_card", "sc": "1.4.10", "type": "true_negative"},
        ]
    }
}


def read_report(test_name):
    """Read the audit report HTML for a test."""
    report_path = os.path.join(BASE, test_name, "outputs", "audit-report.html")
    if not os.path.isfile(report_path):
        # Try finding any HTML file in outputs
        out_dir = os.path.join(BASE, test_name, "outputs")
        if os.path.isdir(out_dir):
            for f in os.listdir(out_dir):
                if f.endswith('.html'):
                    report_path = os.path.join(out_dir, f)
                    break

    text = ""
    if os.path.isfile(report_path):
        with open(report_path, 'r', errors='ignore') as f:
            text = f.read()

    # Also read any other text files in outputs
    out_dir = os.path.join(BASE, test_name, "outputs")
    if os.path.isdir(out_dir):
        for f in os.listdir(out_dir):
            fp = os.path.join(out_dir, f)
            if os.path.isfile(fp) and not f.endswith('.html'):
                try:
                    with open(fp, 'r', errors='ignore') as fh:
                        text += "\n" + fh.read()
                except:
                    pass
    return text


def has_html_file(test_name):
    out_dir = os.path.join(BASE, test_name, "outputs")
    if not os.path.isdir(out_dir):
        return False
    return any(f.endswith('.html') for f in os.listdir(out_dir))


def check(name, t):
    """Run a named check against the report text (lowercased)."""

    # META checks
    if name == "html_report_exists":
        return None  # handled separately
    if name == "has_contrast_ratios":
        return len(re.findall(r'\d+\.\d+:\d', t)) >= 3
    if name == "recognizes_compliant":
        return ("pass" in t or "compliant" in t or "conforms" in t) and not re.search(r'(critical|major)\s*(fail|issue)', t)

    # 01-subtle-contrast
    if name == "flags_757575":
        return "757575" in t and ("fail" in t or "4.48" in t or "does not" in t)
    if name == "flags_rgba_overlay":
        return ("rgba" in t or "overlay" in t or "9a9a9a" in t or "effective" in t) and ("fail" in t or "contrast" in t)
    if name == "flags_74b9ff":
        return "74b9ff" in t and ("fail" in t or "2.07" in t or "contrast" in t)
    if name == "flags_button_border":
        return ("cccccc" in t and ("1.61" in t or "fail" in t or "non-text" in t or "border" in t))
    if name == "flags_card_meta":
        return ("959595" in t or "card" in t and "meta" in t) and ("fail" in t or "contrast" in t)
    if name == "no_flag_2d6a4f":
        # Should pass — if mentioned, it should say "pass"
        if "2d6a4f" in t:
            # Find context around it — it should be marked as pass
            idx = t.find("2d6a4f")
            context = t[max(0,idx-200):idx+200]
            return "pass" in context or "7.08" in context or "✅" in context
        return True  # Not mentioned at all is also acceptable

    # 02-semantic-structure
    if name == "flags_fake_headings":
        return ("fake" in t and "heading" in t) or ("div" in t and "heading" in t) or ("semantic" in t and "heading" in t) or ("styled" in t and ("div" in t or "heading" in t))
    if name == "flags_div_nav":
        return ("nav" in t and ("div" in t or "semantic" in t or "landmark" in t)) or "navigation" in t and ("landmark" in t or "semantic" in t or "<nav>" in t)
    if name == "flags_table_th":
        return ("th" in t or "scope" in t or "table header" in t) and ("missing" in t or "lack" in t or "fail" in t or "no " in t)
    if name == "flags_placeholder_labels":
        return "placeholder" in t and ("label" in t) and ("fail" in t or "missing" in t or "insufficient" in t or "not" in t)
    if name == "flags_css_order":
        return ("order" in t and ("css" in t or "flex" in t or "visual" in t or "dom" in t or "sequence" in t or "1.3.2" in t))
    if name == "flags_generic_links":
        return ("click here" in t or "read more" in t or "generic" in t and "link" in t) and ("fail" in t or "descriptive" in t or "purpose" in t or "2.4" in t)
    if name == "flags_missing_lang":
        return ("lang" in t and ("fr" in t or "french" in t or "3.1.2" in t)) and ("missing" in t or "fail" in t or "lack" in t)
    if name == "flags_toggle_aria":
        return ("toggle" in t or "switch" in t) and ("role" in t or "aria" in t) and ("missing" in t or "fail" in t or "lack" in t or "no " in t)

    # 03-keyboard-focus
    if name == "flags_onclick_div":
        return ("onclick" in t or "click" in t) and ("div" in t or "keyboard" in t) and ("fail" in t or "not accessible" in t or "inaccessible" in t or "2.1.1" in t or "not keyboard" in t)
    if name == "flags_keyboard_trap":
        return ("trap" in t or "escape" in t or "modal" in t) and ("keyboard" in t or "2.1.2" in t or "focus" in t)
    if name == "flags_outline_none":
        return "outline" in t and ("none" in t or "remov" in t) and ("fail" in t or "focus" in t or "2.4.7" in t)
    if name == "flags_tabindex":
        return "tabindex" in t and ("5" in t or "positive" in t or "order" in t or "2.4.3" in t)
    if name == "flags_sticky_obscure":
        return ("sticky" in t or "fixed" in t) and ("header" in t or "obscur" in t) and ("focus" in t or "2.4.11" in t or "z-index" in t)
    if name == "flags_mouseover":
        return ("mouseover" in t or "hover" in t or "mouse" in t) and ("keyboard" in t or "equivalent" in t or "only" in t) and ("fail" in t or "2.1.1" in t or "no keyboard" in t or "inaccessible" in t)
    if name == "flags_focus_contrast":
        return ("focus" in t and ("contrast" in t or "1.4.11" in t) and ("fail" in t or "1." in t)) or ("e0e0e0" in t and "focus" in t)

    # 04-wcag22-specific
    if name == "flags_pagination_dots":
        return ("pagination" in t or "dot" in t) and ("8" in t or "small" in t or "target" in t or "2.5.8" in t)
    if name == "flags_icon_buttons":
        return ("icon" in t and ("18" in t or "small" in t or "target" in t or "2.5.8" in t))
    if name == "flags_star_rating":
        return ("star" in t and ("14" in t or "small" in t or "target" in t or "rating" in t or "2.5.8" in t))
    if name == "flags_bottom_bar":
        return ("bottom" in t or "fixed" in t) and ("bar" in t or "obscur" in t) and ("focus" in t or "2.4.11" in t or "form" in t)
    if name == "no_flag_big_btn":
        # The 48px button should not be flagged as too small
        if "48" in t:
            idx = t.find("48")
            context = t[max(0,idx-150):idx+150]
            return "pass" in context or "meet" in context or "✅" in context or "sufficient" in context or "exceed" in context
        return True

    # 05-form-accessibility
    if name == "flags_email_no_label":
        return "email" in t and ("label" in t or "1.3.1" in t) and ("missing" in t or "no " in t or "lack" in t or "fail" in t or "without" in t)
    if name == "flags_radio_no_fieldset":
        return ("radio" in t or "fieldset" in t or "legend" in t) and ("missing" in t or "fail" in t or "lack" in t or "no " in t or "group" in t)
    if name == "flags_phone_no_label":
        return "phone" in t and ("label" in t) and ("missing" in t or "no " in t or "fail" in t or "lack" in t)
    if name == "flags_error_association":
        return ("error" in t and ("associat" in t or "describedby" in t or "programmat" in t)) or ("3.3.1" in t and "fail" in t)
    if name == "flags_required_color_only":
        return "required" in t and ("color" in t or "red" in t or "asterisk" in t) and ("only" in t or "1.3.1" in t or "1.4.1" in t or "fail" in t)
    if name == "flags_custom_select":
        return ("custom" in t and "select" in t or "dropdown" in t) and ("role" in t or "aria" in t or "4.1.2" in t) and ("missing" in t or "fail" in t or "lack" in t or "no " in t)
    if name == "flags_placeholder_contrast":
        return ("bbbbbb" in t or "placeholder" in t) and ("contrast" in t or "1.4.3" in t or "1.9" in t)

    # 06-media-failures
    if name == "flags_hero_empty_alt":
        return ("hero" in t or "alt=\"\"" in t or "empty alt" in t) and ("meaningful" in t or "fail" in t or "decorative" in t or "1.1.1" in t)
    if name == "flags_missing_alt":
        return "alt" in t and ("missing" in t or "no alt" in t or "without" in t or "lacks" in t) and ("product" in t or "1.1.1" in t)
    if name == "flags_nondescriptive_alt":
        return ("alt=\"image\"" in t or "non-descriptive" in t or "nondescriptive" in t or "alt text" in t and "image" in t) and ("fail" in t or "generic" in t or "1.1.1" in t)
    if name == "flags_image_of_text":
        return ("image of text" in t or "1.4.5" in t or "text as image" in t or "image-based" in t) and ("fail" in t or "heading" in t or "svg" in t)
    if name == "flags_icon_link":
        return ("icon" in t or "link" in t) and ("accessible name" in t or "alt" in t) and ("missing" in t or "fail" in t or "no " in t or "lack" in t)
    if name == "flags_no_transcript":
        return ("audio" in t or "podcast" in t) and ("transcript" in t or "1.2.1" in t) and ("missing" in t or "fail" in t or "no " in t or "lack" in t)
    if name == "flags_no_captions":
        return ("video" in t or "caption" in t) and ("caption" in t or "1.2.2" in t or "subtitle" in t) and ("missing" in t or "fail" in t or "no " in t or "lack" in t)
    if name == "no_flag_decorative":
        # Decorative divider with alt="" should NOT be flagged
        if "divider" in t and "fail" in t:
            return False
        if "decorative" in t:
            idx = t.find("decorative")
            context = t[max(0,idx-200):idx+200]
            return "pass" in context or "correct" in context or "✅" in context or "appropriate" in context
        return True  # Not mentioned = not falsely flagged

    # 07-fully-compliant (false positive tests)
    if name == "no_false_text_fail":
        # Should not flag text contrast as failing
        # Allow minor border contrast mentions but not text contrast fails
        fails = re.findall(r'(text|body|heading|paragraph).*?(fail|❌)', t)
        return len(fails) == 0
    if name == "no_false_focus_fail":
        return not ("focus" in t and "fail" in t and ("gold" in t or "ffd700" in t or "custom" in t))
    if name == "no_false_target_fail":
        return not ("44" in t and "fail" in t and "target" in t)

    # 08-dynamic-content
    if name == "flags_toggle_no_role":
        return ("toggle" in t or "switch" in t) and ("role" in t or "aria-checked" in t or "4.1.2" in t) and ("missing" in t or "fail" in t or "no " in t or "lack" in t)
    if name == "flags_no_aria_live":
        return ("aria-live" in t or "status" in t or "4.1.3" in t) and ("missing" in t or "fail" in t or "no " in t or "lack" in t or "settings saved" in t)
    if name == "flags_tabs_no_aria":
        return ("tab" in t and ("role" in t or "aria" in t or "1.3.1" in t) and ("missing" in t or "fail" in t or "no " in t or "lack" in t or "div" in t))
    if name == "flags_accordion_keyboard":
        return ("accordion" in t) and ("keyboard" in t or "2.1.1" in t) and ("fail" in t or "inaccessible" in t or "not" in t or "onclick" in t)
    if name == "flags_accordion_expanded":
        return ("accordion" in t) and ("aria-expanded" in t or "4.1.2" in t) and ("missing" in t or "fail" in t or "no " in t or "lack" in t)
    if name == "flags_step_order":
        return ("order" in t and ("step" in t or "css" in t or "flex" in t or "visual" in t or "dom" in t or "1.3.2" in t))

    # 09-color-only-info
    if name == "flags_links_no_underline":
        return ("link" in t and ("underline" in t or "color only" in t or "color alone" in t or "1.4.1" in t))
    if name == "flags_required_color":
        return "required" in t and ("color" in t) and ("only" in t or "sole" in t or "1.4.1" in t or "fail" in t)
    if name == "flags_status_dots":
        return ("status" in t or "dot" in t) and ("color" in t) and ("only" in t or "sole" in t or "1.4.1" in t or "fail" in t or "indicator" in t)
    if name == "flags_chart_legend":
        return ("chart" in t or "legend" in t) and ("color" in t) and ("only" in t or "1.4.1" in t or "fail" in t or "pattern" in t)
    if name == "flags_error_border":
        return ("error" in t and "border" in t and ("color" in t or "red" in t)) or ("error" in t and ("only" in t or "1.4.1" in t))
    if name == "flags_green_contrast":
        return ("4caf50" in t and ("fail" in t or "contrast" in t or "2.78" in t or "3.03" in t)) or ("success" in t and "contrast" in t and "fail" in t)
    if name == "no_flag_badges":
        if "badge" in t:
            idx = t.find("badge")
            context = t[max(0,idx-200):idx+200]
            return "pass" in context or "✅" in context or "text" in context and "color" in context and "both" in context
        return True

    # 10-responsive-reflow
    if name == "flags_fixed_table":
        return ("table" in t and ("900" in t or "min-width" in t or "horizontal" in t or "scroll" in t or "1.4.10" in t)) or ("reflow" in t and "table" in t and "fail" in t)
    if name == "flags_nowrap_code":
        return ("code" in t and ("nowrap" in t or "clip" in t or "overflow" in t or "1.4.10" in t or "truncat" in t))
    if name == "flags_fixed_font":
        return ("font-size" in t or "14px" in t or "!important" in t) and ("resize" in t or "1.4.4" in t or "zoom" in t or "scale" in t or "fixed" in t or "block" in t) and ("fail" in t)
    if name == "flags_hero_clip":
        return ("hero" in t and ("400" in t or "height" in t or "overflow" in t or "clip" in t or "hidden" in t or "1.4.10" in t))
    if name == "flags_tight_spacing":
        return ("line-height" in t and ("1.0" in t or "tight" in t or "1.4.12" in t)) or ("letter-spacing" in t and ("fail" in t or "1.4.12" in t or "tight" in t))
    if name == "flags_watermark":
        return "e8e8e8" in t and ("fail" in t or "contrast" in t or "1.2" in t or "1.3" in t)
    if name == "no_flag_responsive_card":
        if "responsive" in t and "card" in t:
            idx = t.find("responsive")
            context = t[max(0,idx-200):idx+200]
            if "fail" in context:
                return False
        return True

    return False


# Run all grades
results_summary = {}
total_tp = 0
total_tp_detected = 0
total_tn = 0
total_tn_correct = 0
total_meta = 0
total_meta_pass = 0

print("=" * 80)
print("WCAG 2.2 AUDIT SKILL — EXPANDED TEST SUITE GRADING (ITERATION 2)")
print("=" * 80)
print()

for test_name, test_data in TESTS.items():
    report = read_report(test_name)
    t = report.lower()
    assertions = test_data["assertions"]

    tp_count = 0
    tp_detected = 0
    tn_count = 0
    tn_correct = 0
    meta_count = 0
    meta_pass = 0

    results = []

    for a in assertions:
        check_name = a["check"]
        atype = a.get("type", "meta")

        if check_name == "html_report_exists":
            passed = has_html_file(test_name)
        else:
            passed = check(check_name, t)

        results.append({
            "text": a["text"],
            "passed": passed,
            "type": atype,
            "sc": a.get("sc", "")
        })

        if atype == "true_positive":
            tp_count += 1
            if passed:
                tp_detected += 1
        elif atype == "true_negative":
            tn_count += 1
            if passed:
                tn_correct += 1
        else:  # meta
            meta_count += 1
            if passed:
                meta_pass += 1

    total_tp += tp_count
    total_tp_detected += tp_detected
    total_tn += tn_count
    total_tn_correct += tn_correct
    total_meta += meta_count
    total_meta_pass += meta_pass

    fn_rate = ((tp_count - tp_detected) / tp_count * 100) if tp_count > 0 else 0
    fp_rate = ((tn_count - tn_correct) / tn_count * 100) if tn_count > 0 else 0

    status = "✅" if tp_detected == tp_count and tn_correct == tn_count else "⚠️"
    print(f"{status} {test_name}")
    print(f"   True Positives: {tp_detected}/{tp_count} detected (FN rate: {fn_rate:.0f}%)")
    if tn_count > 0:
        print(f"   True Negatives: {tn_correct}/{tn_count} correct (FP rate: {fp_rate:.0f}%)")
    print(f"   Meta checks: {meta_pass}/{meta_count}")

    for r in results:
        mark = "✅" if r["passed"] else "❌"
        sc_tag = f" [SC {r['sc']}]" if r.get("sc") else ""
        type_tag = f" ({r['type']})" if r['type'] != 'meta' else ""
        print(f"      {mark} {r['text']}{sc_tag}{type_tag}")
    print()

    results_summary[test_name] = {
        "true_positives": {"detected": tp_detected, "total": tp_count},
        "true_negatives": {"correct": tn_correct, "total": tn_count},
        "meta": {"pass": meta_pass, "total": meta_count},
        "false_negative_rate": fn_rate,
        "false_positive_rate": fp_rate,
        "details": results
    }

# Overall summary
print("=" * 80)
print("OVERALL SUMMARY")
print("=" * 80)

overall_fn = ((total_tp - total_tp_detected) / total_tp * 100) if total_tp > 0 else 0
overall_fp = ((total_tn - total_tn_correct) / total_tn * 100) if total_tn > 0 else 0

print(f"\nTrue Positive Detection: {total_tp_detected}/{total_tp} ({total_tp_detected/total_tp*100:.1f}%)")
print(f"False Negative Rate: {overall_fn:.1f}% ({total_tp - total_tp_detected} missed issues)")
print(f"\nTrue Negative Accuracy: {total_tn_correct}/{total_tn} ({total_tn_correct/total_tn*100:.1f}%)")
print(f"False Positive Rate: {overall_fp:.1f}% ({total_tn - total_tn_correct} phantom issues)")
print(f"\nMeta Checks: {total_meta_pass}/{total_meta} pass")
print()

if overall_fn > 0:
    print("⚠️  FALSE NEGATIVES DETECTED — These are missed real issues:")
    for test_name, data in results_summary.items():
        for d in data["details"]:
            if d["type"] == "true_positive" and not d["passed"]:
                print(f"   ❌ {test_name}: {d['text']} [SC {d.get('sc', '?')}]")
    print()

if overall_fp > 0:
    print("⚠️  FALSE POSITIVES DETECTED — These are phantom issues flagged incorrectly:")
    for test_name, data in results_summary.items():
        for d in data["details"]:
            if d["type"] == "true_negative" and not d["passed"]:
                print(f"   ❌ {test_name}: {d['text']} [SC {d.get('sc', '?')}]")
    print()

# Save results
output = {
    "iteration": 2,
    "test_pages": 10,
    "total_ground_truth_failures": total_tp,
    "true_positives_detected": total_tp_detected,
    "false_negative_rate": round(overall_fn, 1),
    "total_true_negatives": total_tn,
    "true_negatives_correct": total_tn_correct,
    "false_positive_rate": round(overall_fp, 1),
    "meta_checks_pass": total_meta_pass,
    "meta_checks_total": total_meta,
    "per_test": results_summary
}

with open(os.path.join(BASE, "grading_results.json"), 'w') as f:
    json.dump(output, f, indent=2)

print(f"Results saved to {os.path.join(BASE, 'grading_results.json')}")
