import re
from typing import Dict, Any, List, Optional
from backend.services.llm_service import llm_service
from backend.services.hindsight_service import hindsight_service

class CodeGeneratorAgent:
    """Generates fully functional, responsive HTML/Tailwind/JS code for local businesses with multimedia assets."""

    def generate_website(
        self,
        business_data: Dict[str, Any],
        copy_data: Dict[str, Any],
        design_system: Dict[str, Any],
        instructions: Optional[str] = None,
        critique_patch_instructions: Optional[str] = None,
        existing_html: Optional[str] = None
    ) -> str:
        # Check if voice instruction is an exact text replacement command (e.g. change X to "Y" or replace X with Y)
        if instructions and existing_html:
            modified = self._try_exact_voice_replacement(existing_html, instructions)
            if modified:
                return modified

        name = business_data.get("name", "Apex Solutions")
        category = business_data.get("category", "Professional Services")
        location = business_data.get("location", "Austin, TX")
        phone = business_data.get("phone", "+1 512-555-0198")
        whatsapp = business_data.get("whatsapp", phone)

        # Standardize WhatsApp URL format per Hindsight Directives
        clean_wa = re.sub(r"[^\d]", "", whatsapp)
        wa_url = f"https://wa.me/{clean_wa}"

        palette = design_system.get("palette", {})
        primary_color = palette.get("primary", "#2563eb")

        # Check for asset payloads
        assets = business_data.get("assets", {})

        # If LLM is active and instructions exist, ask LLM
        if (instructions or critique_patch_instructions) and llm_service.client:
            prompt = f"""
You are an expert Frontend Architect.
Generate a complete, single-file HTML website with Tailwind CSS CDN and Lucide icons.
Business Name: {name}
Category: {category}
Location: {location}
WhatsApp URL: {wa_url}
Primary Color: {primary_color}
Assets: {assets}
User Voice Instructions: {instructions or 'None'}
Critique Self-Healing Feedback: {critique_patch_instructions or 'None'}

Incorporate logo, product photo gallery, pricing tiers, and brochure if present.
Return ONLY valid HTML inside ```html ... ``` code block.
"""
            llm_response = llm_service.complete(prompt, system_prompt="You write pristine, production-ready HTML with zero syntax errors.")
            if "```html" in llm_response:
                html_code = llm_response.split("```html")[1].split("```")[0].strip()
                return html_code

        # Default battle-tested template with full asset support
        return self._build_template(business_data, copy_data, design_system, wa_url, assets, instructions)

    def _try_exact_voice_replacement(self, html: str, instructions: str) -> Optional[str]:
        """
        Detects exact change requests like:
        - change book a room to "book room"
        - change "schedule appointment" to "book room"
        - rename X to Y
        - replace X with Y
        """
        inst = instructions.strip()
        
        # Regex to capture: change <target> to ["]?<replacement>["]?
        pattern = re.search(r'(?:change|rename|replace|update)\s+["\']?(.+?)["\']?\s+(?:to|with)\s+["\']?(.+?)["\']?$', inst, re.IGNORECASE)
        if pattern:
            target = pattern.group(1).strip().strip('"').strip("'")
            replacement = pattern.group(2).strip().strip('"').strip("'")
            
            # Case-insensitive replacement while preserving structure
            if target and replacement and target.lower() in html.lower():
                # Perform regex case-insensitive replacement
                pattern_re = re.compile(re.escape(target), re.IGNORECASE)
                updated_html = pattern_re.sub(replacement, html)
                return updated_html
        return None

    def _build_template(
        self,
        business_data: Dict[str, Any],
        copy_data: Dict[str, Any],
        design_system: Dict[str, Any],
        wa_url: str,
        assets: Dict[str, Any],
        instructions: Optional[str] = None
    ) -> str:
        name = business_data.get("name", "Austin Smile Studio")
        category = business_data.get("category", "Dental Clinic")
        location = business_data.get("location", "Austin, TX")
        phone = business_data.get("phone", "+1 (512) 555-0198")
        
        palette = design_system.get("palette", {})
        primary = palette.get("primary", "#b45309")
        primary_hover = palette.get("primary_hover", "#92400e")
        secondary = palette.get("secondary", "#0d9488")
        accent = palette.get("accent", "#f59e0b")
        memory_theme = design_system.get("memory_theme", "default")

        headline = copy_data.get("headline", f"{location}'s Premier {category}")
        subheadline = copy_data.get("subheadline", f"Trusted by thousands in {location}. Providing world-class care and verified excellence.")
        
        cta_primary = copy_data.get("cta_primary", "Schedule Appointment")
        cta_secondary = copy_data.get("cta_secondary", "Instant WhatsApp Chat")

        # Check for user instructions targeting primary CTA
        if instructions:
            inst_lower = instructions.lower()
            if "book room" in inst_lower and "a room" not in inst_lower:
                cta_primary = "Book Room"
            elif "book a room" in inst_lower:
                cta_primary = "Book a Room"
            elif "reserve a table" in inst_lower:
                cta_primary = "Reserve a Table"

        services = copy_data.get("services", [])
        testimonials = copy_data.get("testimonials", [])
        why_us = copy_data.get("why_choose_us", [])

        # Category-aware section heading; never carry hotel language into a clinic/cafe site.
        cat_lower = category.lower()
        if "hotel" in cat_lower or "resort" in cat_lower or "stay" in cat_lower or "lodge" in cat_lower:
            offerings_label = "Tailored Hospitality"
            offerings_heading = "Stay, Dine & Unwind"
            offerings_subtitle = f"Thoughtfully designed hospitality experiences in {location}."
        elif "dental" in cat_lower:
            offerings_label = "Patient-Focused Care"
            offerings_heading = "Complete Dental Care"
            offerings_subtitle = f"Modern dental services focused on comfort, clarity, and confident care in {location}."
        elif any(term in cat_lower for term in ("clinic", "hospital", "medical", "health")):
            offerings_label = "Patient-Focused Care"
            offerings_heading = "Care Designed Around You"
            offerings_subtitle = f"Professional healthcare services with clear guidance and compassionate support in {location}."
        elif any(term in cat_lower for term in ("cafe", "coffee", "restaurant", "bakery")):
            offerings_label = "Signature Experiences"
            offerings_heading = "Made for Good Moments"
            offerings_subtitle = f"Fresh flavors, welcoming spaces, and memorable experiences in {location}."
        else:
            offerings_label = "Our Services"
            offerings_heading = f"Trusted {category} Services"
            offerings_subtitle = f"Professional services tailored to customers in {location}."

        # Assets extraction
        logo_url = assets.get("logo_url", "").strip()
        photos = assets.get("photos", [])
        video_url = assets.get("video_url", "").strip()
        brochure_url = assets.get("brochure_url", "").strip()
        pricing_tiers = assets.get("pricing_tiers", [])

        # Default rich photo gallery if none provided
        if not photos:
            if "hotel" in category.lower():
                photos = [
                    {"url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80", "title": "Luxury Suite", "desc": "Spacious king suites with panoramic views"},
                    {"url": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80", "title": "Fine Dining Lounge", "desc": "World-class gourmet culinary experience"},
                    {"url": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=800&q=80", "title": "Wellness & Spa", "desc": "Full rejuvenation and relaxation retreat"}
                ]
            elif "cafe" in category.lower():
                photos = [
                    {"url": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=800&q=80", "title": "Single-Origin Brew", "desc": "Artisan espresso and cold brew selections"},
                    {"url": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=800&q=80", "title": "Artisanal Bakery", "desc": "Fresh daily baked sourdough and pastries"},
                    {"url": "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?auto=format&fit=crop&w=800&q=80", "title": "Relaxed Atmosphere", "desc": "Co-working friendly indoor and terrace seating"}
                ]
            else:
                photos = [
                    {"url": "https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=800&q=80", "title": "State-of-the-Art Facility", "desc": "Modern equipment ensuring precision care"},
                    {"url": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=800&q=80", "title": "Certified Specialists", "desc": "Licensed, background-checked professionals"},
                    {"url": "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=800&q=80", "title": "Patient Comfort", "desc": "Dedicated care with satisfaction guarantee"}
                ]

        # Protect against stale pricing from a previous category. If a clinic/cafe/etc.
        # receives hotel-specific tiers from the UI, discard them and derive category-safe defaults.
        category_lower = category.lower()
        hotel_terms = ("suite", "room", "villa", "king bed", "room service", "/night", "/ night")
        has_hotel_pricing = any(any(term in str(v).lower() for term in hotel_terms) for tier in pricing_tiers for v in tier.values())
        if not pricing_tiers or ("hotel" not in category_lower and "resort" not in category_lower and has_hotel_pricing):
            if "hotel" in category_lower or "resort" in category_lower or "stay" in category_lower:
                pricing_tiers = [
                    {"name": "Standard Deluxe", "price": "₹3,999", "period": "/ night", "badge": "Popular", "features": ["King Size Bed", "High-Speed Wi-Fi", "Complimentary Breakfast", "24/7 Room Service"]},
                    {"name": "Executive Suite", "price": "₹6,499", "period": "/ night", "badge": "Best Value", "features": ["City View Balcony", "Jacuzzi & Lounge", "Airport Transit Included", "Free Spa Access"]},
                    {"name": "Presidential Villa", "price": "₹12,999", "period": "/ night", "badge": "Luxury", "features": ["Private Butler Service", "Complimentary Fine Dining", "Private Terrace Pool", "VIP Lounge Access"]}
                ]
            elif "dental" in category_lower:
                pricing_tiers = [
                    {"name": "Dental Checkup", "price": "₹499", "period": "", "badge": "Basic", "features": ["Consultation", "Oral Examination", "Basic Screening"]},
                    {"name": "Smile Care", "price": "₹2,499", "period": "", "badge": "Popular", "features": ["Cleaning", "Whitening Consultation", "Follow-up"]},
                    {"name": "Complete Dental Care", "price": "₹5,999", "period": "", "badge": "Complete", "features": ["Advanced Consultation", "Treatment Plan", "Follow-up"]}
                ]
            elif any(x in category_lower for x in ("clinic", "hospital", "medical", "health")):
                pricing_tiers = [
                    {"name": "Consultation", "price": "₹499", "period": "", "badge": "Basic", "features": ["Doctor Consultation", "Basic Assessment", "Digital Prescription"]},
                    {"name": "Complete Care", "price": "₹1,499", "period": "", "badge": "Popular", "features": ["Consultation", "Diagnostics", "Follow-up Support"]},
                    {"name": "Priority Care", "price": "₹2,999", "period": "", "badge": "Priority", "features": ["Priority Appointment", "Advanced Diagnostics", "Dedicated Support"]}
                ]
            elif any(x in category_lower for x in ("cafe", "coffee", "restaurant", "bakery")):
                pricing_tiers = [
                    {"name": "Coffee & Pastry", "price": "₹299", "period": "", "badge": "Starter", "features": ["Fresh Brew", "Pastry", "Dine-in Seating"]},
                    {"name": "Tasting Experience", "price": "₹799", "period": "", "badge": "Popular", "features": ["Specialty Coffee Flight", "Dessert Pairing", "Table Reservation"]},
                    {"name": "Cafe Membership", "price": "₹1,499", "period": "/ month", "badge": "Member", "features": ["Member Discounts", "Priority Seating", "Free Beverage"]}
                ]
            else:
                pricing_tiers = [
                    {"name": "Basic Service", "price": "₹999", "period": "", "badge": "Basic", "features": ["Initial Consultation", "Basic Service", "Summary Report"]},
                    {"name": "Complete Service", "price": "₹2,499", "period": "", "badge": "Recommended", "features": ["Full Assessment", "Professional Service", "Follow-up"]},
                    {"name": "Priority Service", "price": "₹4,999", "period": "", "badge": "Priority", "features": ["Priority Support", "Advanced Service", "Dedicated Assistance"]}
                ]

        # Logo Markup
        if logo_url:
            logo_markup = f'<img src="{logo_url}" alt="{name} Logo" class="h-10 w-auto object-contain rounded-lg max-w-[140px]">'
        else:
            logo_markup = f"""
            <div class="w-10 h-10 rounded-xl bg-amber-600 text-white flex items-center justify-center font-extrabold text-xl shadow-md shadow-amber-600/20">
                <i data-lucide="sparkles" class="w-5 h-5"></i>
            </div>
            """

        # Form adaptation
        is_hotel = "hotel" in category.lower() or "room" in cta_primary.lower() or "stay" in category.lower()
        if is_hotel:
            form_title = f"{cta_primary} Directly"
            form_subtitle = "Instant booking confirmation with zero prepayment"
            service_select_html = """
                <option>Standard Deluxe Room</option>
                <option>Executive Suite</option>
                <option>Presidential Villa</option>
                <option>Banquet & Conference Hall</option>
            """
            date_label = "Check-in / Check-out Dates"
        else:
            form_title = f"Reserve Your Service"
            form_subtitle = "Immediate confirmation via SMS / WhatsApp"
            service_select_html = f"""
                <option>Standard {category} Service</option>
                <option>Express Diagnostic & Care</option>
                <option>Urgent / Priority Service</option>
            """
            date_label = "Preferred Date & Time"

        # Pricing Tiers HTML
        pricing_html = ""
        for p in pricing_tiers:
            badge = p.get("badge", "")
            badge_html = f'<span class="px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-900 uppercase tracking-wider">{badge}</span>' if badge else ''
            
            features_html = "".join([
                f'<li class="flex items-center space-x-2.5 text-slate-600 text-xs sm:text-sm"><i data-lucide="check" class="w-4 h-4 text-emerald-600 flex-shrink-0"></i><span>{feat}</span></li>'
                for feat in p.get("features", [])
            ])

            pricing_html += f"""
            <div class="bg-white rounded-3xl p-8 border border-slate-200/80 shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col justify-between relative group hover:-translate-y-1">
                <div>
                    <div class="flex items-center justify-between mb-4">
                        <h4 class="text-xl font-bold text-slate-900">{p.get('name', 'Package')}</h4>
                        {badge_html}
                    </div>
                    <div class="mb-6 flex items-baseline space-x-1">
                        <span class="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">{p.get('price', '$99')}</span>
                        <span class="text-xs text-slate-500 font-semibold">{p.get('period', '')}</span>
                    </div>
                    <ul class="space-y-3 mb-8">
                        {features_html}
                    </ul>
                </div>
                <button onclick="selectTier('{p.get('name', '')}')" class="w-full bg-slate-900 group-hover:bg-amber-600 text-white font-bold py-3 rounded-xl transition-colors duration-200 text-sm flex items-center justify-center space-x-2">
                    <span>Select {p.get('name', 'Plan')}</span>
                    <i data-lucide="arrow-right" class="w-4 h-4"></i>
                </button>
            </div>
            """

        # Photos Gallery HTML
        photos_html = ""
        for photo in photos:
            p_url = photo.get("url", photo) if isinstance(photo, dict) else photo
            p_title = photo.get("title", f"{name} Showcase") if isinstance(photo, dict) else "Featured Showcase"
            p_desc = photo.get("desc", f"Verified excellence in {location}") if isinstance(photo, dict) else ""

            photos_html += f"""
            <div class="group relative rounded-3xl overflow-hidden shadow-md hover:shadow-2xl transition-all duration-300 bg-slate-900 h-80">
                <img src="{p_url}" alt="{p_title}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 opacity-90 group-hover:opacity-100">
                <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/20 to-transparent flex flex-col justify-end p-6">
                    <h4 class="text-white font-bold text-lg mb-1">{p_title}</h4>
                    <p class="text-slate-300 text-xs leading-relaxed">{p_desc}</p>
                </div>
            </div>
            """

        # Video Section HTML (if provided)
        video_section_html = ""
        if video_url:
            # Check for YouTube embed conversion
            embed_url = video_url
            if "watch?v=" in video_url:
                v_id = video_url.split("watch?v=")[1].split("&")[0]
                embed_url = f"https://www.youtube.com/embed/{v_id}"
            elif "youtu.be/" in video_url:
                v_id = video_url.split("youtu.be/")[1].split("?")[0]
                embed_url = f"https://www.youtube.com/embed/{v_id}"

            video_section_html = f"""
            <section class="py-16 bg-slate-950 text-white">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <span class="text-xs font-bold text-amber-500 uppercase tracking-widest mb-2 block">Virtual Tour</span>
                    <h3 class="text-3xl font-extrabold mb-8">Experience {name} in Motion</h3>
                    <div class="max-w-4xl mx-auto rounded-3xl overflow-hidden shadow-2xl border border-slate-800 aspect-video">
                        <iframe src="{embed_url}" class="w-full h-full border-none" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
                    </div>
                </div>
            </section>
            """

        # Brochure Button Markup
        brochure_btn_html = ""
        if brochure_url:
            brochure_btn_html = f"""
            <a href="{brochure_url}" target="_blank" download class="inline-flex items-center space-x-2 text-xs font-bold text-slate-700 bg-white border border-slate-200 px-4 py-2.5 rounded-xl shadow-sm hover:bg-slate-50 transition">
                <i data-lucide="file-text" class="w-4 h-4 text-amber-600"></i>
                <span>Download Brochure (PDF)</span>
            </a>
            """

        services_html = ""
        for s in services:
            services_html += f"""
            <div class="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm hover:shadow-lg transition-all duration-300 group">
                <div class="w-12 h-12 rounded-xl bg-amber-50 flex items-center justify-center text-amber-700 mb-6 group-hover:scale-110 transition-transform">
                    <i data-lucide="check-circle" class="w-6 h-6"></i>
                </div>
                <h3 class="text-xl font-bold text-slate-900 mb-2">{s.get('title', 'Certified Service')}</h3>
                <p class="text-slate-600 leading-relaxed">{s.get('description', 'High-quality care tailored to your specific requirements.')}</p>
            </div>
            """

        testimonials_html = ""
        for t in testimonials:
            testimonials_html += f"""
            <div class="bg-slate-50 p-6 rounded-2xl border border-slate-200/60 shadow-sm">
                <div class="flex items-center space-x-1 text-amber-400 mb-4">
                    <i data-lucide="star" class="w-4 h-4 fill-current"></i>
                    <i data-lucide="star" class="w-4 h-4 fill-current"></i>
                    <i data-lucide="star" class="w-4 h-4 fill-current"></i>
                    <i data-lucide="star" class="w-4 h-4 fill-current"></i>
                    <i data-lucide="star" class="w-4 h-4 fill-current"></i>
                </div>
                <p class="text-slate-700 italic mb-4">"{t.get('quote', 'Exceptional service and quick response!')}"</p>
                <div class="font-semibold text-slate-900 text-sm">{t.get('name', 'Verified Client')}</div>
                <div class="text-xs text-slate-500">Verified • {location}</div>
            </div>
            """

        why_html = ""
        for w in why_us:
            why_html += f"""
            <li class="flex items-start space-x-3">
                <div class="mt-1 flex-shrink-0 w-5 h-5 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center">
                    <i data-lucide="check" class="w-3.5 h-3.5"></i>
                </div>
                <span class="text-slate-700 font-medium">{w}</span>
            </li>
            """

        if memory_theme == "luxury_dark":
            memory_style = """
        /* HINDSIGHT-LEARNED VISUAL SYSTEM: black / white / gold, restrained motion */
        :root { --memory-gold:#D4AF37; --memory-gold-soft:#F0D878; --memory-black:#090909; --memory-ink:#111111; --memory-paper:#F5F3EE; }
        body { background:#F5F3EE !important; color:#111111 !important; }
        header { background:rgba(245,243,238,.94) !important; border-color:rgba(212,175,55,.28) !important; }
        .bg-amber-600,.bg-amber-700 { background-color:var(--memory-gold) !important; }
        .hover\:bg-amber-700:hover,.hover\:bg-amber-600:hover { background-color:var(--memory-gold-soft) !important; }
        .text-amber-500,.text-amber-600,.text-amber-700,.text-amber-800,.text-amber-900 { color:var(--memory-gold) !important; }
        .bg-amber-50,.bg-amber-100 { background-color:rgba(212,175,55,.10) !important; }
        .border-amber-100,.border-amber-200 { border-color:rgba(212,175,55,.28) !important; }
        .bg-slate-900,.bg-slate-950 { background-color:var(--memory-black) !important; }
        .bg-slate-50 { background-color:#F5F3EE !important; }
        .border-slate-200,.border-slate-100 { border-color:rgba(17,17,17,.10) !important; }
        .bg-gradient-to-b,.bg-gradient-to-tr,.bg-gradient-to-r { background-image:none !important; }
        button,a { transition:transform .22s ease, box-shadow .22s ease, background-color .22s ease, color .22s ease !important; }
        button:hover,a:hover { transform:translateY(-2px); }
        .shadow-lg,.shadow-xl,.shadow-2xl { box-shadow:0 18px 50px rgba(9,9,9,.10) !important; }
        """
        else:
            memory_style = ""

        html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} | {category} in {location}</title>
    <meta name="description" content="Top-rated {category} in {location}. Call {phone} or chat on WhatsApp for fast booking.">
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Lucide Icons CDN -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
        }}
        {memory_style}
    </style>
</head>
<body class="bg-slate-50 text-slate-900 antialiased selection:bg-amber-500 selection:text-white">

    <!-- Top Announcement Bar -->
    <div class="bg-slate-900 text-white text-xs py-2 px-4 text-center font-medium flex items-center justify-center space-x-3">
        <span>📍 Proudly serving {location} & surrounding neighborhoods</span>
        <span class="hidden md:inline">•</span>
        <span class="hidden md:inline">🕒 Instant Confirmation on WhatsApp</span>
    </div>

    <!-- Navigation Header -->
    <header class="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/80 transition-all duration-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                {logo_markup}
                <div>
                    <span class="text-xl font-extrabold tracking-tight text-slate-900">{name}</span>
                    <span class="block text-xs font-medium text-slate-500">{category}</span>
                </div>
            </div>

            <!-- Desktop Nav -->
            <nav class="hidden md:flex items-center space-x-8 text-sm font-semibold text-slate-600">
                <a href="#gallery" class="hover:text-amber-600 transition-colors">Showcase</a>
                <a href="#services" class="hover:text-amber-600 transition-colors">Services</a>
                <a href="#pricing" class="hover:text-amber-600 transition-colors">Pricing & Rates</a>
                <a href="#why-us" class="hover:text-amber-600 transition-colors">Why Us</a>
                <a href="#contact" class="hover:text-amber-600 transition-colors">Location</a>
            </nav>

            <!-- Header Actions -->
            <div class="hidden sm:flex items-center space-x-3">
                {brochure_btn_html}
                <a href="tel:{phone.replace(' ', '')}" class="flex items-center space-x-2 text-sm font-semibold text-slate-700 hover:text-amber-600 px-3 py-2 rounded-lg transition-colors">
                    <i data-lucide="phone" class="w-4 h-4 text-amber-600"></i>
                    <span>{phone}</span>
                </a>
                <button onclick="openBookingModal()" class="bg-amber-600 hover:bg-amber-700 text-white px-5 py-2.5 rounded-xl font-semibold text-sm shadow-md shadow-amber-600/20 hover:shadow-lg transition-all duration-200 flex items-center space-x-2">
                    <i data-lucide="calendar" class="w-4 h-4"></i>
                    <span>{cta_primary}</span>
                </button>
            </div>

            <!-- Mobile Hamburger -->
            <button onclick="toggleMobileMenu()" class="md:hidden p-2 rounded-lg text-slate-700 hover:bg-slate-100">
                <i data-lucide="menu" class="w-6 h-6"></i>
            </button>
        </div>

        <!-- Mobile Menu Dropdown -->
        <div id="mobile-menu" class="hidden md:hidden px-4 pt-2 pb-6 bg-white border-b border-slate-200 space-y-3">
            <a href="#gallery" onclick="toggleMobileMenu()" class="block py-2 text-slate-700 font-medium">Showcase Gallery</a>
            <a href="#services" onclick="toggleMobileMenu()" class="block py-2 text-slate-700 font-medium">Services</a>
            <a href="#pricing" onclick="toggleMobileMenu()" class="block py-2 text-slate-700 font-medium">Pricing</a>
            <a href="#why-us" onclick="toggleMobileMenu()" class="block py-2 text-slate-700 font-medium">Why Us</a>
            <a href="#contact" onclick="toggleMobileMenu()" class="block py-2 text-slate-700 font-medium">Contact</a>
            <button onclick="openBookingModal(); toggleMobileMenu();" class="w-full bg-amber-600 text-white py-3 rounded-xl font-semibold shadow-md">
                {cta_primary}
            </button>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="relative overflow-hidden pt-12 pb-20 lg:pt-20 lg:pb-28 bg-gradient-to-b from-white via-amber-50/30 to-slate-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
                <div class="lg:col-span-7 space-y-6 text-center lg:text-left">
                    <div class="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-amber-100 text-amber-900 text-xs font-bold tracking-wide uppercase">
                        <i data-lucide="shield-check" class="w-4 h-4 text-amber-700"></i>
                        <span>Verified & Premier Experience in {location}</span>
                    </div>

                    <h1 class="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-slate-900 tracking-tight leading-tight">
                        {headline}
                    </h1>

                    <p class="text-lg sm:text-xl text-slate-600 leading-relaxed max-w-2xl mx-auto lg:mx-0">
                        {subheadline}
                    </p>

                    <!-- Trust Stats -->
                    <div class="pt-2 flex flex-wrap justify-center lg:justify-start gap-4 text-xs font-semibold text-slate-500">
                        <div class="flex items-center space-x-1.5 bg-white px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm">
                            <i data-lucide="star" class="w-4 h-4 text-amber-500 fill-amber-500"></i>
                            <span>4.9/5 Rating (500+ Reviews)</span>
                        </div>
                        <div class="flex items-center space-x-1.5 bg-white px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm">
                            <i data-lucide="clock" class="w-4 h-4 text-emerald-600"></i>
                            <span>Instant WhatsApp Support</span>
                        </div>
                    </div>

                    <!-- Hero CTAs -->
                    <div class="pt-4 flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4">
                        <button onclick="openBookingModal()" class="w-full sm:w-auto bg-amber-600 hover:bg-amber-700 text-white px-8 py-4 rounded-xl font-bold text-base shadow-lg shadow-amber-600/30 hover:shadow-xl hover:-translate-y-0.5 transition-all flex items-center justify-center space-x-2">
                            <i data-lucide="calendar" class="w-5 h-5"></i>
                            <span>{cta_primary}</span>
                        </button>
                        <button onclick="openLiveChat()" class="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-700 text-white px-8 py-4 rounded-xl font-bold text-base shadow-lg shadow-emerald-600/30 hover:shadow-xl hover:-translate-y-0.5 transition-all flex items-center justify-center space-x-2">
                            <i data-lucide="message-circle" class="w-5 h-5"></i>
                            <span>{cta_secondary}</span>
                        </button>
                    </div>
                </div>

                <!-- Hero Card / Quick Booking Preview -->
                <div class="lg:col-span-5">
                    <div class="bg-white rounded-3xl p-8 border border-slate-200 shadow-xl shadow-slate-200/50 relative">
                        <div class="flex items-center justify-between pb-6 border-b border-slate-100">
                            <div>
                                <h3 class="text-lg font-bold text-slate-900">{form_title}</h3>
                                <p class="text-xs text-slate-500">{form_subtitle}</p>
                            </div>
                            <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">
                                ● Online
                            </span>
                        </div>

                        <form id="hero-quick-form" onsubmit="handleHeroSubmit(event)" class="space-y-4 pt-6">
                            <div>
                                <label class="block text-xs font-semibold text-slate-700 mb-1">Your Full Name</label>
                                <input type="text" required placeholder="Guest Name" class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-amber-500 focus:outline-none text-sm">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-slate-700 mb-1">Phone / WhatsApp Number</label>
                                <input type="tel" required placeholder="{phone}" class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-amber-500 focus:outline-none text-sm">
                            </div>
                            <div>
                                <label class="block text-xs font-semibold text-slate-700 mb-1">Select Option</label>
                                <select class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-amber-500 focus:outline-none text-sm bg-white">
                                    {service_select_html}
                                </select>
                            </div>
                            <button type="submit" class="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-3.5 rounded-xl shadow-md transition-all text-sm flex items-center justify-center space-x-2">
                                <span>Confirm {cta_primary}</span>
                                <i data-lucide="arrow-right" class="w-4 h-4"></i>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Product / Photo Showcase Gallery Section -->
    <section id="gallery" class="py-20 bg-white border-b border-slate-200/80">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center max-w-3xl mx-auto mb-16">
                <h2 class="text-xs font-bold text-amber-700 uppercase tracking-widest mb-2">Visual Showcase</h2>
                <h3 class="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">Experience Our Spaces & Products</h3>
                <p class="text-slate-600 mt-4 text-base">Curated photos and assets from {name} in {location}.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                {photos_html}
            </div>
        </div>
    </section>

    <!-- Video Showcase (if present) -->
    {video_section_html}

    <!-- Pricing & Packages Section -->
    <section id="pricing" class="py-20 bg-slate-50 border-b border-slate-200/80">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center max-w-3xl mx-auto mb-16">
                <h2 class="text-xs font-bold text-amber-700 uppercase tracking-widest mb-2">Transparent Pricing</h2>
                <h3 class="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">{("hotel" in category.lower() or "resort" in category.lower()) and "Packages & Rates" or "Services & Pricing"}</h3>
                <p class="text-slate-600 mt-4 text-base">Clear, upfront options tailored for this {category.lower()}.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                {pricing_html}
            </div>
        </div>
    </section>

    <!-- Services Section -->
    <section id="services" class="py-20 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center max-w-3xl mx-auto mb-16">
                <h2 class="text-xs font-bold text-amber-700 uppercase tracking-widest mb-2">{offerings_label}</h2>
                <h3 class="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">{offerings_heading}</h3>
                <p class="text-slate-600 mt-4 text-base">{offerings_subtitle}</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                {services_html}
            </div>
        </div>
    </section>

    <!-- Why Choose Us Section -->
    <section id="why-us" class="py-20 bg-slate-50 border-y border-slate-200/60">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
                <div class="space-y-6">
                    <span class="text-xs font-bold text-emerald-600 uppercase tracking-widest">Why We Stand Out</span>
                    <h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight leading-tight">
                        Built on Trust, Elegance, and Exceptional Customer Care.
                    </h2>
                    <p class="text-slate-600 leading-relaxed text-base">
                        When you choose {name}, you experience verified quality, transparent pricing, and unforgettable service.
                    </p>
                    <ul class="space-y-4 pt-2">
                        {why_html}
                    </ul>
                </div>

                <div class="bg-gradient-to-tr from-amber-700 to-amber-900 rounded-3xl p-8 sm:p-12 text-white shadow-xl relative overflow-hidden">
                    <div class="relative z-10 space-y-6">
                        <div class="inline-block p-3 rounded-2xl bg-white/20 backdrop-blur-md">
                            <i data-lucide="award" class="w-8 h-8 text-white"></i>
                        </div>
                        <h3 class="text-2xl sm:text-3xl font-bold">100% Satisfaction Guarantee</h3>
                        <p class="text-white/90 text-sm leading-relaxed">
                            Every experience at {name} is backed by our full service guarantee. If anything does not meet your expectations, we will make it right immediately.
                        </p>
                        <div class="pt-4 flex items-center space-x-4">
                            <button onclick="openBookingModal()" class="bg-white text-slate-900 font-bold px-6 py-3 rounded-xl shadow-lg hover:bg-slate-100 transition-colors text-sm">
                                {cta_primary}
                            </button>
                            <button onclick="openLiveChat()" class="text-white font-semibold flex items-center space-x-2 text-sm hover:underline">
                                <span>Direct Chat</span>
                                <i data-lucide="message-circle" class="w-4 h-4"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Testimonials Section -->
    <section id="testimonials" class="py-20 bg-white">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="text-center max-w-2xl mx-auto mb-16">
                <span class="text-xs font-bold text-amber-700 uppercase tracking-widest">Real Customer Feedback</span>
                <h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mt-2">Loved by Locals in {location}</h2>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                {testimonials_html}
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="py-20 bg-slate-50 border-t border-slate-200/80">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-12">
                <div class="space-y-6">
                    <span class="text-xs font-bold text-amber-700 uppercase tracking-widest">Visit & Connect</span>
                    <h2 class="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">We're Here in {location}</h2>
                    <p class="text-slate-600 text-base">Have questions or need assistance? Our on-duty concierge and support staff are available 24/7.</p>

                    <div class="space-y-4 pt-4">
                        <div class="flex items-center space-x-4 p-4 rounded-2xl bg-white border border-slate-100 shadow-sm">
                            <div class="w-10 h-10 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center flex-shrink-0">
                                <i data-lucide="map-pin" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <div class="text-xs text-slate-500 font-semibold uppercase">Location Address</div>
                                <div class="font-bold text-slate-900">{location} Prime District</div>
                            </div>
                        </div>

                        <div class="flex items-center space-x-4 p-4 rounded-2xl bg-white border border-slate-100 shadow-sm">
                            <div class="w-10 h-10 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center flex-shrink-0">
                                <i data-lucide="phone-call" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <div class="text-xs text-slate-500 font-semibold uppercase">Telephone Desk</div>
                                <a href="tel:{phone.replace(' ', '')}" class="font-bold text-slate-900 hover:text-amber-700">{phone}</a>
                            </div>
                        </div>

                        <div class="flex items-center space-x-4 p-4 rounded-2xl bg-emerald-50 border border-emerald-100 cursor-pointer" onclick="openLiveChat()">
                            <div class="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center flex-shrink-0">
                                <i data-lucide="message-circle" class="w-5 h-5"></i>
                            </div>
                            <div>
                                <div class="text-xs text-emerald-800 font-semibold uppercase">Official WhatsApp Desk</div>
                                <div class="font-bold text-emerald-900 hover:underline">Click to start live chat & WhatsApp</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Interactive Location / Map Card -->
                <div class="rounded-3xl bg-white p-8 border border-slate-200 shadow-sm flex flex-col justify-between relative overflow-hidden">
                    <div class="space-y-4">
                        <div class="inline-flex items-center space-x-2 bg-slate-100 px-3 py-1 rounded-full text-xs font-bold text-slate-700 shadow-sm">
                            <i data-lucide="navigation" class="w-3.5 h-3.5 text-amber-700"></i>
                            <span>Territory: {location}</span>
                        </div>
                        <h3 class="text-2xl font-bold text-slate-900">Direct Service & Reception Hub</h3>
                        <p class="text-slate-600 text-sm">Centrally situated in {location} with convenient transit and valet parking.</p>
                    </div>

                    <div class="my-8 h-48 bg-slate-100 rounded-2xl flex items-center justify-center border border-slate-200 relative">
                        <div class="text-center space-y-2">
                            <div class="w-12 h-12 rounded-full bg-amber-600 text-white flex items-center justify-center mx-auto shadow-lg animate-bounce">
                                <i data-lucide="map-pin" class="w-6 h-6"></i>
                            </div>
                            <span class="text-xs font-bold text-slate-700 block">{name} • {location}</span>
                        </div>
                    </div>

                    <button onclick="openBookingModal()" class="w-full bg-amber-600 hover:bg-amber-700 text-white font-bold py-4 rounded-xl shadow-md transition-all text-sm">
                        {cta_primary}
                    </button>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-slate-950 text-slate-400 py-12 border-t border-slate-800 text-sm">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-6">
            <div class="flex items-center space-x-3">
                {logo_markup}
                <span class="text-white font-bold text-base">{name}</span>
            </div>
            <div>
                © 2026 {name}. All rights reserved. Premium {category} in {location}.
            </div>
        </div>
    </footer>

    <!-- Floating Live Chat / WhatsApp Button -->
    <button onclick="openLiveChat()" class="fixed bottom-6 right-6 z-50 bg-emerald-500 hover:bg-emerald-600 text-white p-4 rounded-full shadow-2xl shadow-emerald-500/40 hover:scale-110 transition-all duration-300 flex items-center justify-center group" title="Instant Chat / WhatsApp">
        <i data-lucide="message-circle" class="w-7 h-7"></i>
        <span class="max-w-0 overflow-hidden whitespace-nowrap group-hover:max-w-xs transition-all duration-300 ease-in-out text-sm font-bold pl-0 group-hover:pl-2">
            Live Chat
        </span>
    </button>

    <!-- Interactive Live Chat Desk Drawer / Modal -->
    <div id="live-chat-modal" class="fixed inset-0 sm:inset-auto sm:bottom-24 sm:right-6 z-50 hidden sm:w-96 bg-white sm:rounded-3xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col h-full sm:h-[480px]">
        <!-- Chat Header -->
        <div class="bg-gradient-to-r from-emerald-600 to-teal-700 text-white p-4 flex items-center justify-between flex-shrink-0">
            <div class="flex items-center space-x-3">
                <div class="relative">
                    <div class="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center font-bold text-sm">
                        <i data-lucide="user-check" class="w-5 h-5"></i>
                    </div>
                    <span class="absolute bottom-0 right-0 w-2.5 h-2.5 bg-emerald-300 border-2 border-emerald-700 rounded-full"></span>
                </div>
                <div>
                    <h4 class="font-bold text-sm leading-tight">{name} Live Desk</h4>
                    <span class="text-[11px] text-emerald-100 flex items-center space-x-1">
                        <span>● Replies instantly</span>
                    </span>
                </div>
            </div>
            <button onclick="closeLiveChat()" class="text-white/80 hover:text-white p-1 rounded-lg">
                <i data-lucide="x" class="w-5 h-5"></i>
            </button>
        </div>

        <!-- Chat Conversation Area -->
        <div id="chat-messages" class="flex-1 p-4 overflow-y-auto space-y-3 bg-slate-50 text-xs">
            <div class="flex items-start space-x-2">
                <div class="w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center flex-shrink-0 mt-0.5">
                    <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
                </div>
                <div class="bg-white p-3 rounded-2xl rounded-tl-none border border-slate-200 shadow-sm max-w-[85%] text-slate-800 leading-relaxed">
                    Hello! Welcome to <strong>{name}</strong> in {location}. How can our team assist you today?
                </div>
            </div>

            <div class="pt-2 flex flex-wrap gap-1.5 pl-8">
                <button onclick="sendQuickMessage('I would like to {cta_primary.lower()}')" class="bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 px-2.5 py-1 rounded-full text-[11px] font-medium transition">
                    🛎️ {cta_primary}
                </button>
                <button onclick="sendQuickMessage('What are your room rates and availability?')" class="bg-emerald-50 hover:bg-emerald-100 text-emerald-800 border border-emerald-200 px-2.5 py-1 rounded-full text-[11px] font-medium transition">
                    💰 Pricing & Rates
                </button>
                <button onclick="openWhatsAppDirect()" class="bg-emerald-600 text-white px-2.5 py-1 rounded-full text-[11px] font-semibold transition flex items-center space-x-1">
                    <i data-lucide="message-circle" class="w-3 h-3"></i>
                    <span>Open in WhatsApp</span>
                </button>
            </div>
        </div>

        <!-- Chat Input Bar -->
        <div class="p-3 bg-white border-t border-slate-200 flex items-center space-x-2 flex-shrink-0">
            <input type="text" id="chat-input" onkeydown="if(event.key==='Enter') sendChatMessage()" placeholder="Type a message..." class="flex-1 px-3 py-2 text-xs border border-slate-200 rounded-xl focus:outline-none focus:ring-1 focus:ring-emerald-500">
            <button onclick="sendChatMessage()" class="w-8 h-8 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white flex items-center justify-center flex-shrink-0 transition">
                <i data-lucide="send" class="w-4 h-4"></i>
            </button>
        </div>
    </div>

    <!-- Booking Modal -->
    <div id="booking-modal" class="fixed inset-0 z-50 hidden bg-slate-950/70 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="bg-white rounded-3xl max-w-lg w-full p-8 shadow-2xl relative border border-slate-100">
            <button onclick="closeBookingModal()" class="absolute top-6 right-6 text-slate-400 hover:text-slate-700 p-1.5 rounded-lg">
                <i data-lucide="x" class="w-6 h-6"></i>
            </button>

            <div class="mb-6">
                <div class="w-10 h-10 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center mb-3">
                    <i data-lucide="calendar" class="w-5 h-5"></i>
                </div>
                <h3 class="text-2xl font-bold text-slate-900" id="modal-title">{cta_primary}</h3>
                <p class="text-slate-500 text-sm mt-1">Direct reservation with {name}. Confirmed within 15 minutes.</p>
            </div>

            <form id="modal-form" onsubmit="handleModalSubmit(event)" class="space-y-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-700 mb-1">Full Name</label>
                    <input type="text" required placeholder="Guest Name" class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-amber-500 focus:outline-none text-sm">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-semibold text-slate-700 mb-1">Phone / WhatsApp</label>
                        <input type="tel" required placeholder="{phone}" class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-amber-500 focus:outline-none text-sm">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-700 mb-1">{date_label}</label>
                        <input type="date" required class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-amber-500 focus:outline-none text-sm">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-700 mb-1">Package / Tier Selection</label>
                    <select id="modal-service-select" class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-amber-500 focus:outline-none text-sm bg-white">
                        {service_select_html}
                    </select>
                </div>
                <button type="submit" class="w-full bg-amber-600 hover:bg-amber-700 text-white font-bold py-3.5 rounded-xl shadow-lg shadow-amber-600/20 transition-all text-sm flex items-center justify-center space-x-2">
                    <i data-lucide="check" class="w-4 h-4"></i>
                    <span>Confirm {cta_primary}</span>
                </button>
            </form>
        </div>
    </div>

    <!-- Client-Side Toast Notification -->
    <div id="toast" class="fixed top-6 right-6 z-50 hidden bg-emerald-600 text-white px-6 py-4 rounded-2xl shadow-xl font-medium flex items-center space-x-3">
        <i data-lucide="check-circle" class="w-5 h-5"></i>
        <span id="toast-message">Booking received! We will text you shortly.</span>
    </div>

    <script>
        const waLink = "{wa_url}";

        lucide.createIcons();

        function toggleMobileMenu() {{
            const menu = document.getElementById('mobile-menu');
            menu.classList.toggle('hidden');
        }}

        function openBookingModal(tierName) {{
            document.getElementById('booking-modal').classList.remove('hidden');
            if (tierName) {{
                const sel = document.getElementById('modal-service-select');
                for (let i = 0; i < sel.options.length; i++) {{
                    if (sel.options[i].text.toLowerCase().includes(tierName.toLowerCase())) {{
                        sel.selectedIndex = i;
                        break;
                    }}
                }}
            }}
        }}

        function closeBookingModal() {{
            document.getElementById('booking-modal').classList.add('hidden');
        }}

        function selectTier(tierName) {{
            openBookingModal(tierName);
        }}

        function openLiveChat() {{
            document.getElementById('live-chat-modal').classList.remove('hidden');
            setTimeout(() => {{
                document.getElementById('chat-input').focus();
            }}, 100);
        }}

        function closeLiveChat() {{
            document.getElementById('live-chat-modal').classList.add('hidden');
        }}

        function openWhatsAppDirect() {{
            window.open(waLink, '_blank');
        }}

        function sendQuickMessage(text) {{
            appendUserMessage(text);
            setTimeout(() => {{
                appendAgentReply("Thank you! Our concierge has received your request: '" + text + "'. We can also continue instantly on WhatsApp.");
            }}, 600);
        }}

        function sendChatMessage() {{
            const input = document.getElementById('chat-input');
            const text = input.value.trim();
            if (!text) return;
            appendUserMessage(text);
            input.value = "";
            setTimeout(() => {{
                appendAgentReply("Got it! Our staff is ready to help with '" + text + "'. Would you like to confirm on WhatsApp now? <br><button onclick='openWhatsAppDirect()' class='mt-2 bg-emerald-600 text-white px-3 py-1 rounded-lg font-bold flex items-center space-x-1.5'><span>Chat on WhatsApp</span></button>");
            }}, 700);
        }}

        function appendUserMessage(text) {{
            const container = document.getElementById('chat-messages');
            const div = document.createElement('div');
            div.className = "flex justify-end";
            div.innerHTML = `<div class="bg-emerald-600 text-white p-3 rounded-2xl rounded-tr-none shadow-sm max-w-[85%] leading-relaxed">${{text}}</div>`;
            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }}

        function appendAgentReply(html) {{
            const container = document.getElementById('chat-messages');
            const div = document.createElement('div');
            div.className = "flex items-start space-x-2";
            div.innerHTML = `
                <div class="w-6 h-6 rounded-full bg-emerald-600 text-white flex items-center justify-center flex-shrink-0 mt-0.5">
                    <i data-lucide="sparkles" class="w-3.5 h-3.5"></i>
                </div>
                <div class="bg-white p-3 rounded-2xl rounded-tl-none border border-slate-200 shadow-sm max-w-[85%] text-slate-800 leading-relaxed">${{html}}</div>
            `;
            container.appendChild(div);
            lucide.createIcons();
            container.scrollTop = container.scrollHeight;
        }}

        function showToast(message) {{
            const toast = document.getElementById('toast');
            document.getElementById('toast-message').innerText = message;
            toast.classList.remove('hidden');
            setTimeout(() => {{
                toast.classList.add('hidden');
            }}, 4000);
        }}

        function handleModalSubmit(e) {{
            e.preventDefault();
            closeBookingModal();
            showToast("Success! Your booking request has been confirmed.");
        }}

        function handleHeroSubmit(e) {{
            e.preventDefault();
            showToast("Confirmed! Our team will contact you on WhatsApp / SMS.");
        }}
    </script>
</body>
</html>"""
        return html

code_generator_agent = CodeGeneratorAgent()
