from typing import Dict, Any, Optional
from backend.services.hindsight_service import hindsight_service

class DesignAgent:
    """Selects high-conversion color palettes, typography, and component styling based on business niche."""

    NICHE_PALETTES = {
        "hotel": {
            "primary": "#b45309",       # Amber/Gold 700 (Luxury Hospitality)
            "primary_hover": "#92400e", # Amber 800
            "secondary": "#0f172a",     # Midnight Slate 900
            "accent": "#10b981",        # Emerald
            "bg_light": "#fffbeb",      # Warm Luxury Amber 50
            "text_dark": "#0f172a",     # Slate 900
            "tag": "Luxury Hospitality & Accommodations"
        },
        "dental": {
            "primary": "#0284c7",       # Sky 600
            "primary_hover": "#0369a1", # Sky 700
            "secondary": "#0d9488",     # Teal 600
            "accent": "#f59e0b",        # Amber 500
            "bg_light": "#f8fafc",      # Slate 50
            "text_dark": "#0f172a",     # Slate 900
            "tag": "Clean Medical & Wellness"
        },
        "plumbing": {
            "primary": "#1d4ed8",       # Blue 700
            "primary_hover": "#1e40af", # Blue 800
            "secondary": "#ea580c",     # Orange 600 (Emergency contrast)
            "accent": "#10b981",        # Emerald 500
            "bg_light": "#f8fafc",
            "text_dark": "#0f172a",
            "tag": "Urgent Home Trade & Services"
        },
        "restaurant": {
            "primary": "#b91c1c",       # Red 700
            "primary_hover": "#991b1b",
            "secondary": "#d97706",     # Amber 600
            "accent": "#059669",        # Green for freshness
            "bg_light": "#fffbeb",      # Warm amber 50
            "text_dark": "#1c1917",     # Stone 900
            "tag": "Hospitality & Dining"
        },
        "cafe": {
            "primary": "#78350f",       # Roasted Coffee Brown 900
            "primary_hover": "#451a03",
            "secondary": "#d97706",     # Warm Amber
            "accent": "#059669",
            "bg_light": "#fefce8",      # Cream
            "text_dark": "#1c1917",
            "tag": "Artisan Cafe & Coffee"
        },
        "legal": {
            "primary": "#1e293b",       # Slate 800
            "primary_hover": "#0f172a",
            "secondary": "#d97706",     # Gold / Amber 600
            "accent": "#2563eb",
            "bg_light": "#f8fafc",
            "text_dark": "#020617",
            "tag": "Corporate & Legal Authority"
        },
        "default": {
            "primary": "#2563eb",       # Royal Blue
            "primary_hover": "#1d4ed8",
            "secondary": "#10b981",     # Emerald (WhatsApp synergy)
            "accent": "#f59e0b",
            "bg_light": "#f8fafc",
            "text_dark": "#0f172a",
            "tag": "Modern High-Conversion Local Business"
        }
    }

    def choose_design_system(self, category: str, instructions: Optional[str] = None) -> Dict[str, Any]:
        cat_lower = category.lower()
        inst_lower = (instructions or "").lower()

        matched = "default"
        for key in self.NICHE_PALETTES:
            if key in cat_lower or key in inst_lower:
                matched = key
                break

        palette = dict(self.NICHE_PALETTES[matched])

        # Voice instruction color overrides
        if "gold" in inst_lower or "luxury" in inst_lower:
            palette["primary"] = "#d97706"
            palette["primary_hover"] = "#b45309"
        elif "dark" in inst_lower and "slate" in inst_lower:
            palette["primary"] = "#0f172a"
        elif "green" in inst_lower or "emerald" in inst_lower:
            palette["primary"] = "#059669"
            palette["primary_hover"] = "#047857"
        elif "purple" in inst_lower:
            palette["primary"] = "#7c3aed"
            palette["primary_hover"] = "#6d28d9"

        # Convert durable Hindsight preferences into an explicit visual mode.
        # This makes recalled memory change the generated site, not merely the prompt.
        luxury_dark = (
            ("black" in inst_lower or "dark" in inst_lower)
            and ("gold" in inst_lower or "luxury" in inst_lower)
        )
        if luxury_dark:
            palette.update({
                "primary": "#D4AF37",
                "primary_hover": "#F0D878",
                "secondary": "#0A0A0A",
                "accent": "#FFFFFF",
                "bg_light": "#F5F3EE",
                "text_dark": "#0A0A0A",
                "tag": "Memory-Learned Noir & Gold"
            })

        # Check Hindsight memory for any user-overridden design constraints
        memories = hindsight_service.recall(
            query=f"design system styling guidelines for {category}",
            tags=["design", "ui_ux"],
            max_results=2
        )

        return {
            "theme_name": palette["tag"],
            "palette": palette,
            "typography": {
                "font_family": "Plus Jakarta Sans, system-ui, sans-serif",
                "heading_weight": "font-extrabold tracking-tight",
                "body_size": "text-slate-600 text-base leading-relaxed"
            },
            "memory_theme": "luxury_dark" if luxury_dark else "default",
            "components": {
                "button_radius": "rounded-xl",
                "card_shadow": "shadow-sm hover:shadow-md transition-shadow duration-200 border border-slate-100",
                "sticky_header": True,
                "floating_whatsapp": True
            },
            "recalled_design_rules": [m["content"] for m in memories]
        }

design_agent = DesignAgent()
