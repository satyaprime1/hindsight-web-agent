import re
from typing import Dict, Any, List

class UICritic:
    """Evaluates layout hierarchy, contrast, balance, and visual structure."""
    name = "UI/UX Critic"

    def evaluate(self, html: str, business_data: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        score = 100

        # Check for core structural sections
        required_sections = ["header", "services", "testimonials", "contact", "footer"]
        for sec in required_sections:
            if sec not in html.lower():
                issues.append(f"Missing distinct '{sec}' visual section or landmark.")
                score -= 15

        # Check for hero headline
        if "<h1" not in html:
            issues.append("Missing primary <h1> visual anchor for hero banner.")
            score -= 20

        # Check for contrast / backdrop cues
        if "text-slate" not in html and "text-gray" not in html and "text-white" not in html:
            issues.append("Lack of standard high-contrast typography utility classes.")
            score -= 10

        return {
            "critic": self.name,
            "score": max(score, 0),
            "passed": score >= 80,
            "issues": issues,
            "summary": "Visual hierarchy is balanced and engaging." if score >= 80 else f"Found {len(issues)} UI/UX issues."
        }


class FunctionalityCritic:
    """Evaluates WhatsApp integration, booking modals, forms, and interactive triggers."""
    name = "Functionality Critic"

    def evaluate(self, html: str, business_data: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        score = 100

        # WhatsApp Check (Hindsight Core Directive)
        if "wa.me/" not in html:
            issues.append("CRITICAL: WhatsApp link is missing or not formatted as https://wa.me/<number>.")
            score -= 30
        elif "wa.me/+" in html or "wa.me/ " in html:
            issues.append("WhatsApp link contains illegal '+' or spaces in URL protocol.")
            score -= 20

        # Booking form / modal check
        if "booking-modal" not in html and "<form" not in html:
            issues.append("Missing interactive booking form or modal container.")
            score -= 25

        # Check for inert buttons (buttons without onclick or type=submit)
        inert_button_match = re.findall(r'<button(?![^>]*(?:onclick|type="submit"))[^>]*>', html)
        if inert_button_match:
            issues.append(f"Detected {len(inert_button_match)} inert button(s) lacking click handlers.")
            score -= 15

        # Check for feedback feedback toasts/alerts
        if "showToast" not in html and "alert(" not in html and "modal" not in html:
            issues.append("No user confirmation feedback on form submission.")
            score -= 15

        return {
            "critic": self.name,
            "score": max(score, 0),
            "passed": score >= 80,
            "issues": issues,
            "summary": "All interactive triggers and contact CTAs functioning." if score >= 80 else f"Found {len(issues)} functional flaws."
        }


class MobilePerfCritic:
    """Evaluates viewport, responsive prefixes, and mobile hamburger interactions."""
    name = "Performance & Responsiveness Critic"

    def evaluate(self, html: str, business_data: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        score = 100

        # Viewport check
        if 'name="viewport"' not in html:
            issues.append("CRITICAL: Missing mobile viewport meta tag.")
            score -= 40

        # Responsive utility classes
        responsive_tags = ["sm:", "md:", "lg:"]
        missing_responsive = [tag for tag in responsive_tags if tag not in html]
        if missing_responsive:
            issues.append(f"Limited responsive layout prefixes. Missing: {', '.join(missing_responsive)}.")
            score -= 20

        # Mobile navigation menu
        if "mobile-menu" not in html and "toggleMobileMenu" not in html:
            issues.append("Missing mobile responsive drawer/hamburger navigation.")
            score -= 20

        return {
            "critic": self.name,
            "score": max(score, 0),
            "passed": score >= 80,
            "issues": issues,
            "summary": "Mobile responsive and touch-ready." if score >= 80 else f"Found {len(issues)} mobile responsiveness issues."
        }


class CodeQualityCritic:
    """Evaluates HTML5 structure, semantic tags, and script safety."""
    name = "Code Quality & Validation Critic"

    def evaluate(self, html: str, business_data: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        score = 100

        # Doctype & standard tags
        if "<!DOCTYPE html>" not in html:
            issues.append("Missing <!DOCTYPE html> declaration.")
            score -= 20

        if "<html" not in html or "</html>" not in html:
            issues.append("Missing root <html> tags.")
            score -= 20

        if "<body" not in html or "</body>" not in html:
            issues.append("Missing <body> tags.")
            score -= 20

        # Unclosed script checks
        script_opens = len(re.findall(r'<script', html))
        script_closes = len(re.findall(r'</script>', html))
        if script_opens != script_closes:
            issues.append(f"Mismatched script tags: {script_opens} open vs {script_closes} close.")
            score -= 30

        return {
            "critic": self.name,
            "score": max(score, 0),
            "passed": score >= 80,
            "issues": issues,
            "summary": "Clean, standard-compliant HTML5 structure." if score >= 80 else f"Found {len(issues)} code syntax/structural issues."
        }


class CriticPanel:
    """Coordinates the 4-critic evaluation panel"""
    def __init__(self):
        self.critics = [
            UICritic(),
            FunctionalityCritic(),
            MobilePerfCritic(),
            CodeQualityCritic()
        ]

    def evaluate_all(self, html: str, business_data: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        total_score = 0
        all_issues = []

        for c in self.critics:
            res = c.evaluate(html, business_data)
            results.append(res)
            total_score += res["score"]
            all_issues.extend(res["issues"])

        average_score = round(total_score / len(self.critics), 1)
        passed = average_score >= 85 and len(all_issues) == 0

        return {
            "average_score": average_score,
            "passed": passed,
            "critic_results": results,
            "all_issues": all_issues
        }

critic_panel = CriticPanel()
