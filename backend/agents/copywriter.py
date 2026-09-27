import json
import re
from typing import Dict, Any, List, Optional
from backend.services.llm_service import llm_service
from backend.services.hindsight_service import hindsight_service

class CopywriterAgent:
    """Generates high-converting copy, headlines, services list, and Local SEO schema."""

    def generate_copy(self, business_data: Dict[str, Any], instructions: Optional[str] = None) -> Dict[str, Any]:
        name = business_data.get("name", "Apex Solutions")
        category = business_data.get("category", "Local Service")
        location = business_data.get("location", "Downtown")
        services = business_data.get("services", "")
        # Prevent stale services from a previous category (for example hotel rooms
        # after switching to Clinic) from contaminating generated copy.
        cat_lower = category.lower()
        stale_hotel_terms = ("suite", "room", "villa", "banquet", "fine dining", "/night", "nightly")
        is_hospitality = any(term in cat_lower for term in ("hotel", "resort", "stay", "lodge", "inn"))
        if services and not is_hospitality and any(term in services.lower() for term in stale_hotel_terms):
            if "dental" in cat_lower:
                services = "Dental Checkups, Teeth Cleaning & Whitening, Restorative Care"
            elif any(term in cat_lower for term in ("clinic", "hospital", "medical", "health")):
                services = "General Consultation, Diagnostics & Screening, Follow-up Care"
            elif any(term in cat_lower for term in ("cafe", "coffee", "restaurant", "bakery")):
                services = "Specialty Coffee, Fresh Bakery & Desserts, Table & Event Reservations"
            else:
                services = f"Professional {category} Consultation, Complete Service, Priority Support"
        phone = business_data.get("phone", "+1 555-0199")
        whatsapp = business_data.get("whatsapp", phone)

        # Recall Hindsight memory regarding high-converting copy in this niche
        memories = hindsight_service.recall(
            query=f"high converting copy headlines value propositions for {category}",
            tags=["copywriting", "conversion"],
            max_results=3
        )
        memory_context = "\n".join([f"- {m['content']}" for m in memories])

        prompt = f"""
You are an expert Local Business Copywriter.
Create compelling, conversion-focused website copy for:
Business Name: {name}
Category: {category}
Location: {location}
Offered Services: {services}
WhatsApp Contact: {whatsapp}
User Specific Instructions / Voice Revisions: {instructions or 'None'}

Historical Insights from Hindsight Memory:
{memory_context}

Return a valid JSON object strictly matching this schema:
{{
  "headline": "High-impact main headline tailored to {category} in {location} (under 10 words)",
  "subheadline": "Action-oriented value proposition (1-2 sentences)",
  "cta_primary": "Call to action label (e.g. 'Book a Room' for hotel, 'Schedule Visit' for clinic)",
  "cta_secondary": "Instant WhatsApp Chat",
  "services": [
    {{"title": "Service 1", "description": "Brief benefit description"}},
    {{"title": "Service 2", "description": "Brief benefit description"}},
    {{"title": "Service 3", "description": "Brief benefit description"}}
  ],
  "why_choose_us": [
    "Reason 1 with local credibility in {location}",
    "Reason 2 with rapid response and excellence",
    "Reason 3 with satisfaction guarantee"
  ],
  "testimonials": [
    {{"name": "Local Guest 1", "quote": "Compelling authentic praise", "rating": 5}},
    {{"name": "Local Guest 2", "quote": "Great response time and service", "rating": 5}}
  ],
  "seo_meta": {{
    "title": "{name} | Leading {category} in {location}",
    "description": "Top-rated {category} in {location}. Verified luxury and service. Contact {name} today."
  }}
}}
Return ONLY valid JSON. No markdown wrappers or explanation.
"""
        response = llm_service.complete(prompt, system_prompt="You generate strictly formatted JSON copywriting data.")
        
        try:
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            data = json.loads(cleaned.strip())
            return data
        except Exception:
            # Intelligent heuristic copy generator tailored to location, category, and voice instructions
            return self._heuristic_copy(name, category, location, services, instructions)

    def _heuristic_copy(
        self,
        name: str,
        category: str,
        location: str,
        services_input: str,
        instructions: Optional[str]
    ) -> Dict[str, Any]:
        cat_lower = category.lower()
        inst_lower = (instructions or "").lower()

        # Determine Primary CTA based on voice instruction and category
        cta_primary = "Schedule Appointment"
        if "book a room" in inst_lower or "room" in inst_lower or "hotel" in cat_lower or "resort" in cat_lower or "inn" in cat_lower:
            cta_primary = "Book a Room"
        elif "reserve a table" in inst_lower or "table" in inst_lower or "cafe" in cat_lower or "restaurant" in cat_lower or "dining" in cat_lower:
            cta_primary = "Reserve a Table"
        elif "estimate" in inst_lower or "quote" in inst_lower or "plumb" in cat_lower or "repair" in cat_lower or "electric" in cat_lower:
            cta_primary = "Request Free Quote"
        elif "consult" in inst_lower or "law" in cat_lower or "legal" in cat_lower:
            cta_primary = "Book Consultation"

        # Determine Headline & Subheadline
        if "hotel" in cat_lower or "resort" in cat_lower or "stay" in cat_lower:
            headline = f"{location}'s Premier Luxury Stay & Hospitality"
            subheadline = f"Experience world-class comfort and elegance at {name} in {location}. Modern suites, fine dining, and personalized hospitality."
            services = [
                {"title": "Executive & Deluxe Suites", "description": f"Spacious, climate-controlled suites designed for business travelers and vacationers in {location}."},
                {"title": "24/7 Room Service & Dining", "description": "Gourmet multi-cuisine breakfast, lunch, and dinner delivered fresh to your suite."},
                {"title": "Banquets & Conference Halls", "description": "High-tech audio/visual conference facilities and banquet hosting for up to 300 guests."}
            ]
        elif "plumb" in cat_lower or "pipe" in cat_lower or "drain" in cat_lower:
            headline = f"{location}'s 24/7 Rapid Emergency Plumbers"
            subheadline = f"Licensed master plumbers dispatched across {location} within 45 minutes. Upfront pricing and 100% satisfaction guarantee."
            services = [
                {"title": "Emergency Burst Pipe Repair", "description": f"Immediate dispatch across {location} to stop leaks and prevent water damage."},
                {"title": "Boiler & Water Heater Service", "description": "Full diagnostic, maintenance, and certified installation of hot water units."},
                {"title": "Drain & Sewer Clearance", "description": "High-pressure hydro-jetting and camera inspections for stubborn blockages."}
            ]
        elif "cafe" in cat_lower or "coffee" in cat_lower or "restaurant" in cat_lower:
            headline = f"Artisan Handcrafted Brews & Dining in {location}"
            subheadline = f"Discover single-origin specialty coffee, fresh bakery pastries, and relaxed dining at {name} in the heart of {location}."
            services = [
                {"title": "Specialty Espresso Bar", "description": "Precision roast pour-overs, single-origin beans, and signature cold brews."},
                {"title": "Artisanal Kitchen Menu", "description": "Farm-to-table breakfast, sourdough sandwiches, and fresh seasonal pastries."},
                {"title": "Table & Private Reservations", "description": "Co-working friendly spaces, private booth bookings, and catered gatherings."}
            ]
        else:
            headline = f"{location}'s Trusted {category} Specialists"
            subheadline = f"Providing dependable, verified {category.lower()} in {location}. Transparent pricing, licensed professionals, and prompt service."
            services = [
                {"title": f"Comprehensive {category}", "description": f"Full service and diagnostic solutions tailored to clients in {location}."},
                {"title": "Express Priority Service", "description": "Rapid turnaround and dedicated client support for immediate assistance."},
                {"title": "Quality Satisfaction Guarantee", "description": "Every job is performed to the highest industry standards with full warranty."}
            ]

        # If user explicitly specified services in the input box, prioritize them.
        # Only use them when they match the selected business category; stale hotel
        # terms are ignored for clinics, cafes, and other categories.
        if services_input and len(services_input.strip()) > 3:
            stale = any(term in services_input.lower() for term in ("suite", "room", "villa", "banquet", "fine dining", "/night", "nightly"))
            if stale and not any(term in cat_lower for term in ("hotel", "resort", "stay", "lodge", "inn")):
                services_input = ""
            custom_list = [s.strip() for s in services_input.split(",") if s.strip()]
            if custom_list:
                services = [
                    {"title": item, "description": f"Professional {item.lower()} provided with guaranteed excellence in {location}."}
                    for item in custom_list[:3]
                ]

        return {
            "headline": headline,
            "subheadline": subheadline,
            "cta_primary": cta_primary,
            "cta_secondary": "Instant WhatsApp Chat",
            "services": services,
            "why_choose_us": [
                f"Consistently rated #1 for {category.lower()} in {location}",
                "Transparent upfront pricing with zero hidden fees",
                "Dedicated customer care team available on WhatsApp and phone"
            ],
            "testimonials": [
                {"name": "Priya Sharma", "quote": f"The hospitality and attention to detail at {name} in {location} was extraordinary!", "rating": 5},
                {"name": "Rajesh Kumar", "quote": "Remarkable service, quick response, and very courteous team. Will definitely visit again.", "rating": 5}
            ],
            "seo_meta": {
                "title": f"{name} - Leading {category} in {location}",
                "description": f"Top-rated {category} in {location}. Book directly with {name} for instant confirmation."
            }
        }

copywriter_agent = CopywriterAgent()
