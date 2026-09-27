import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.config import settings, ROOT_DIR

logger = logging.getLogger("hindsight_service")

class HindsightService:
    def __init__(self):
        self.bank_id = settings.hindsight_bank_id
        self.client = None
        self.local_memories: List[Dict[str, Any]] = []
        self.memory_file = ROOT_DIR / "hindsight_memory.json"
        self._load_local_memories()
        self._init_client()

    def _load_local_memories(self):
        """Load resilient local memory so learning survives backend restarts."""
        if not self.memory_file:
            return
        try:
            if self.memory_file.exists():
                data = json.loads(self.memory_file.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    self.local_memories = data
                    logger.info("Loaded %s persistent local Hindsight memories", len(data))
        except Exception as e:
            logger.warning("Could not load persistent Hindsight memory: %s", e)

    def _persist_local_memories(self):
        """Persist the local fallback memory after every learning event."""
        if not self.memory_file:
            return
        try:
            self.memory_file.write_text(
                json.dumps(self.local_memories, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as e:
            logger.warning("Could not persist local Hindsight memory: %s", e)

    def _init_client(self):
        if settings.has_hindsight_credentials:
            try:
                from hindsight_client import Hindsight
                self.client = Hindsight(
                    base_url=settings.hindsight_base_url,
                    api_key=settings.hindsight_api_key,
                )
                logger.info(f"Connected to Hindsight Cloud at {settings.hindsight_base_url}")
                self._configure_bank()
            except Exception as e:
                logger.error(f"Failed to initialize live Hindsight client: {e}. Falling back to internal memory engine.")
                self.client = None
        else:
            logger.info("No live Hindsight API key detected. Operating in simulated Hindsight mode (records all retains, recalls, and reflections locally).")
            # Seed default architectural knowledge
            if not self.local_memories:
                self._seed_default_memories()
                self._persist_local_memories()

    def _configure_bank(self):
        """Configure mission and directives on the Hindsight bank"""
        if not self.client:
            return
        try:
            mission = (
                "You are an elite, conversion-focused autonomous web architect. "
                "You specialize in building rock-solid, responsive local business websites "
                "with verified booking forms, valid WhatsApp integration, and impeccable local SEO."
            )
            # Try setting mission if available
            try:
                self.client.set_mission(bank_id=self.bank_id, mission=mission)
            except Exception:
                pass

            # Core Directives
            directives = [
                "Always format WhatsApp links as 'https://wa.me/<country_code><number>' without '+' symbols, spaces, or dashes.",
                "Always include responsive meta viewport tags and mobile touch-friendly buttons.",
                "Always provide interactive feedback on form submission (toast notification or modal); never leave forms inert.",
                "Maintain WCAG AA color contrast across all hero banners and call-to-action buttons."
            ]
            for d in directives:
                try:
                    self.client.create_directive(bank_id=self.bank_id, directive=d)
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Note on configuring memory bank: {e}")

    def _seed_default_memories(self):
        """Seed architectural observations for local/offline run"""
        seeds = [
            {
                "id": "obs-1",
                "type": "observation",
                "content": "Local business websites convert 3x higher when they feature a floating WhatsApp CTA and a prominent click-to-call button.",
                "tags": ["pattern", "conversion", "local_biz"],
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "obs-2",
                "type": "directive",
                "content": "CRITICAL RULE: WhatsApp links must strictly follow https://wa.me/<country_code><number>. E.g., 'https://wa.me/15125550198'. Never use tel: or raw unformatted strings for WhatsApp.",
                "tags": ["mistake_guard", "functionality", "whatsapp"],
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "obs-3",
                "type": "observation",
                "content": "Hero banners must use high contrast text (e.g., white text on slate-900 background with minimum 4.5:1 ratio) to ensure readability.",
                "tags": ["ui_ux", "accessibility"],
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "obs-4",
                "type": "observation",
                "content": "Appointment booking forms must include Name, Phone/Email, Preferred Date/Time, and a simulated confirmation modal to prevent user abandonment.",
                "tags": ["functionality", "forms"],
                "created_at": datetime.now().isoformat()
            }
        ]
        self.local_memories.extend(seeds)

    def learn_user_preferences(self, instruction: str, business_name: str = "", workflow_id: str = "") -> List[str]:
        """Extract durable, reusable preferences from a user's instruction and retain them.

        This intentionally stores stable design/development preferences rather than every
        transient command, so future projects can benefit from what the user repeatedly
        teaches the agent.
        """
        text = (instruction or "").strip()
        if not text:
            return []

        lower = text.lower()
        preferences = []
        rules = [
            (("no gradient", "no gradients", "without gradient", "avoid gradients"),
             "User prefers interfaces without gradients."),
            (("black, white and gold", "black white gold", "black and white and gold", "black/white/gold"),
             "User prefers a black, white, and gold visual palette."),
            (("black and gold", "black & gold"),
             "User prefers a black-and-gold visual palette."),
            (("minimal", "minimalist", "clean and minimal", "minimal design"),
             "User prefers a clean, minimal interface with restrained visual clutter."),
            (("luxurious", "luxury", "premium", "rich look", "high-end"),
             "User prefers a premium, luxurious, high-end visual direction."),
            (("no excessive animation", "avoid excessive animation", "not too much animation", "subtle animation"),
             "User prefers subtle, purposeful animation rather than excessive motion."),
            (("hover effects", "interactive hover", "interactive elements"),
             "User prefers interactive UI states and meaningful hover feedback."),
            (("no emojis", "without emojis", "avoid emojis"),
             "User prefers professional interfaces without decorative emojis."),
            (("professional", "corporate", "professional look"),
             "User prefers a professional, polished visual language."),
            (("dark mode", "dark theme", "dark interface"),
             "User prefers a dark interface/theme."),
            (("light mode", "light theme", "white background"),
             "User prefers a light interface/theme with a clean background."),
        ]
        for triggers, memory in rules:
            if any(t in lower for t in triggers):
                preferences.append(memory)

        # Capture explicit preference sentences even when they do not match a preset.
        explicit_markers = ("i prefer ", "i like ", "i want ", "keep it ", "always use ", "don't use ", "do not use ", "avoid ")
        if any(marker in lower for marker in explicit_markers):
            compact = " ".join(text.split())
            if len(compact) <= 240:
                preferences.append(f"User instruction/preference: {compact}")

        # De-duplicate while preserving order.
        preferences = list(dict.fromkeys(preferences))
        for pref in preferences:
            self.retain(
                content=pref,
                tags=["user_preference", "design_preference", "long_term_memory"],
                metadata={"type": "user_preference", "workflow_id": workflow_id, "business": business_name, "learning": "explicit_user_instruction"}
            )
        return preferences

    def recall_user_preferences(self, category: str = "", current_instruction: str = "", max_results: int = 8) -> List[Dict[str, Any]]:
        """Recall durable user preferences for the current generation task."""
        query = (
            f"user preferences design style visual language interaction animation typography "
            f"{category} {current_instruction}"
        ).strip()
        return self.recall(
            query=query,
            tags=["user_preference", "design_preference", "long_term_memory"],
            max_results=max_results
        )

    def format_memory_context(self, memories: List[Dict[str, Any]], max_chars: int = 3500) -> str:
        """Format recalled memories into a compact context block for downstream agents."""
        lines = []
        seen = set()
        for memory in memories:
            content = str(memory.get("content", "")).strip()
            if not content or content in seen:
                continue
            seen.add(content)
            lines.append(f"- {content}")
            if sum(len(x) + 1 for x in lines) >= max_chars:
                break
        return "\n".join(lines) if lines else "- No durable user preferences recalled yet."

    def retain(self, content: str, tags: Optional[List[str]] = None, metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Retain memory: Stores facts, critic evaluations, or self-correction lessons.
        """
        tags = tags or []
        metadata = metadata or {}
        
        # Always save to local log for real-time frontend visualization
        memory_entry = {
            "id": f"mem-{len(self.local_memories) + 1}",
            "type": metadata.get("type", "experience"),
            "content": content,
            "tags": tags,
            "metadata": metadata,
            "created_at": datetime.now().isoformat(),
            "source": "hindsight_cloud" if self.client else "hindsight_local"
        }
        self.local_memories.append(memory_entry)
        self._persist_local_memories()

        if self.client:
            try:
                resp = self.client.retain(
                    bank_id=self.bank_id,
                    content=content,
                    tags=tags,
                    metadata=metadata
                )
                logger.info(f"Retained in Hindsight Cloud: {content[:80]}...")
                return {"status": "success", "mode": "cloud", "entry": memory_entry}
            except Exception as e:
                logger.error(f"Error calling live Hindsight retain: {e}")
                return {"status": "fallback", "mode": "local", "entry": memory_entry, "error": str(e)}

        return {"status": "success", "mode": "local", "entry": memory_entry}

    def recall(self, query: str, tags: Optional[List[str]] = None, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Recall memories: Uses TEMPR multi-strategy search (Semantic, Keyword, Graph, Temporal)
        """
        if self.client:
            try:
                resp = self.client.recall(
                    bank_id=self.bank_id,
                    query=query,
                    tags=tags,
                    max_tokens=2048
                )
                recalled = []
                # Map client recall results
                if hasattr(resp, "results") and resp.results:
                    for r in resp.results:
                        recalled.append({
                            "content": getattr(r, "content", str(r)),
                            "score": getattr(r, "score", 0.95),
                            "type": getattr(r, "type", "observation"),
                            "source": "hindsight_cloud"
                        })
                elif hasattr(resp, "memories") and resp.memories:
                    for m in resp.memories:
                        recalled.append({
                            "content": getattr(m, "content", str(m)),
                            "score": getattr(m, "score", 0.9),
                            "type": getattr(m, "type", "observation"),
                            "source": "hindsight_cloud"
                        })
                if recalled:
                    return recalled
            except Exception as e:
                logger.warning(f"Cloud recall error: {e}. Falling back to local TEMPR search.")

        # Local fallback search: Keyword + Tag matching
        query_words = set(query.lower().split())
        matched = []
        for mem in self.local_memories:
            content_lower = mem["content"].lower()
            score = sum(1 for word in query_words if word in content_lower) / max(len(query_words), 1)
            
            # Tag boost
            if tags and any(t in mem.get("tags", []) for t in tags):
                score += 0.4

            if score > 0.1 or not query_words:
                matched.append({
                    "content": mem["content"],
                    "score": round(min(score, 1.0), 2),
                    "type": mem.get("type", "observation"),
                    "tags": mem.get("tags", []),
                    "created_at": mem.get("created_at"),
                    "source": "hindsight_local"
                })

        # Sort by score descending
        matched.sort(key=lambda x: x["score"], reverse=True)
        return matched[:max_results]

    def reflect(self, query: str, context: Optional[str] = None) -> str:
        """
        Reflect: Agentic reasoning over stored observations, directives, and facts.
        """
        if self.client:
            try:
                resp = self.client.reflect(
                    bank_id=self.bank_id,
                    query=query,
                    context=context,
                    budget="mid"
                )
                if hasattr(resp, "text") and resp.text:
                    return resp.text
                if hasattr(resp, "content") and resp.content:
                    return resp.content
                if hasattr(resp, "response") and resp.response:
                    return resp.response
                return str(resp)
            except Exception as e:
                logger.warning(f"Cloud reflect error: {e}. Using local reflection engine.")

        # Local reflection logic: Synthesizes stored memories against query
        recalled = self.recall(query=query, max_results=4)
        insights = "\n".join([f"- [Recalled Rule]: {r['content']}" for r in recalled])
        
        reflection_summary = (
            f"Based on historical observations and architectural directives:\n"
            f"{insights}\n\n"
            f"Prescription for current evaluation: Address identified gaps while adhering strictly "
            f"to accessibility, responsive layout guidelines, and valid external contact protocols."
        )
        return reflection_summary

    def get_all_memories(self) -> List[Dict[str, Any]]:
        """Return all memories currently registered in the bank"""
        return self.local_memories

hindsight_service = HindsightService()
