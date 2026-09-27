# Autonomous AI Website Builder with Hindsight Reflection & Self-Healing Loop

An autonomous, voice and text-directed AI agent that builds, tests, and iteratively self-heals production-ready websites for local businesses. Powered by **Hindsight**, the agent retains knowledge of previous mistakes, design patterns, and constraints, continuously improving its output over time.

---

## 🎯 Architecture Diagram

Based on the multi-agent reflection and self-healing system:

```
[ User Input (Voice / Text) ]
           │
           ▼
┌─────────────────────────────────┐
│       BUSINESS INTAKE           │  (Name, Category, Location, WhatsApp)
└────────────────┬────────────────┘
                 ▼
┌─────────────────────────────────┐
│      ORCHESTRATION AGENT        │ ◄────────────────────────┐
│    (Router & State Manager)     │                          │
└───────┬─────────────────────────┘                          │
        │                                                    │
        ▼                                                    │ Refinement
┌─────────────────────────────────┐                          │ Instructions
│   GENERATION PIPELINE           │                          │
│   • Copywriter Agent            │                          │
│   • Design Agent                │                          │
│   • Code Generator Agent        │                          │
└───────┬─────────────────────────┘                          │
        ▼                                                    │
┌─────────────────────────────────┐                          │
│      INTERMEDIATE CODE          │                          │
└───────┬─────────────────────────┘                          │
        ▼                                                    │
┌─────────────────────────────────┐                          │
│ HINDSIGHT REFLECTION & CRITICS  │                          │
│   • UI/UX Critic                │                          │
│   • Functionality Critic        │                          │
│   • Performance Critic          │                          │
│   • Code Quality Critic         │                          │
└───────┬─────────────────────────┘                          │
        ▼                                                    │
┌─────────────────────────────────┐                          │
│    SELF-CORRECTION ROUTER       │                          │
│  (Pass >= 85% or Re-heal?)      │                          │
└───────┬─────────────────────────┘                          │
        │ [If issues found]                                  │
        ├──────────────────────► [ Hindsight Memory Bank ] ──┘
        │                        • Retains Mistakes & Patterns
        │                        • Reflects on Rules & Directives
        ▼ [If approved]
┌─────────────────────────────────┐
│     DEPLOYMENT & LIVE SITE      │
│  • Interactive Preview Sandbox  │
│  • Working WhatsApp & Booking   │
│  • Local SEO & Schema.org       │
└─────────────────────────────────┘
```

---

## 🧠 Why Hindsight Memory is the Superpower

Standard AI code generation models suffer from **context amnesia**:
1. They repeat the same formatting and styling mistakes across revisions.
2. They break previously working components (like forms or navigation) when prompted to change another section.
3. They forget user brand guidelines, phone formats, and color palettes.

**With Hindsight:**
- **`retain()`**: Critic feedbacks and user corrections are stored as **Experience Facts** (e.g., *"WhatsApp link failed due to missing international country code"*).
- **Consolidation into Observations**: Over time, repeated facts turn into hardened **Observations** (e.g., *"Local service businesses require sticky mobile booking CTAs"*).
- **`reflect()`**: When generating or revising, the Orchestration agent queries the memory bank's observations and directives to self-correct before presenting the code to the user.

---

## ▶️ Quick Start

1. Create/activate a Python 3.11+ virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Add Hindsight/Groq credentials to `.env` if you want cloud memory/LLM features.
4. Start the app: `python run.py`.
5. Open `http://127.0.0.1:8000`.

The app also has a local-resilient mode, so the dashboard and deterministic generation pipeline can run when cloud credentials are unavailable.

## 🚀 Key Features

1. **Voice-to-Website:** Speak your requirements or revisions (powered by Web Speech API).
2. **Multi-Agent Critic Panel:** Evaluates code across 4 distinct dimensions: UI/UX, Functionality, Performance/Mobile, and Syntax Quality.
3. **Autonomous Self-Healing Loop:** If critic scores fall below threshold, the agent passes issues to Hindsight and auto-patches the code.
4. **Live Interactive Sandbox:** Instant desktop/mobile responsive preview.
5. **Real-time Memory Inspector:** Visually inspect memories recalled from Hindsight and self-correction logs during the generation process.

---

## 📋 Progress Tracking
See [CHECKLIST.md](CHECKLIST.md) for full status and phase-by-phase deliverables.


## Hindsight Learning Loop

This version makes Hindsight a first-class generation input rather than only an audit log. The agent can extract durable user preferences from natural-language or voice instructions, retain them as long-term memories, recall them for later projects, and inject the recalled preferences into the Copywriter, Design, and Code Generation stages. Generation outcomes are also retained so later runs can learn from successful patterns and critic failures.

### Demo story
1. Tell the agent: “I prefer black, white and gold, minimal layouts, subtle hover effects, and no excessive animation.”
2. The agent retains those as reusable user preferences.
3. Generate or modify the first website and show the Hindsight learning events.
4. Start a new project/session and ask for a different website without repeating the design preferences.
5. Show Hindsight Recall returning the previous preferences and the new site inheriting them.

The key product claim is: **it does not just generate another website; it learns how the user builds websites.**
