import os
import uuid
import shutil
import httpx
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel

from backend.config import settings
from backend.services.hindsight_service import hindsight_service
from backend.orchestrator import orchestration_agent
from backend.agents.coder import code_generator_agent

app = FastAPI(
    title="Hexo Elite Website Architect API",
    description="Autonomous Website Builder with Hindsight Reflection, Asset Vault & Self-Healing Loop",
    version="1.2.0"
)

# Enable CORS for local testing & preview
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Local directories
UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DEPLOYED_DIR = Path(__file__).resolve().parent / "deployed"
DEPLOYED_DIR.mkdir(parents=True, exist_ok=True)

# Mount uploads static directory
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

class GenerateRequest(BaseModel):
    name: str = "Satya Grand Hotel"
    category: str = "Hotel"
    location: str = "Hyderabad"
    phone: str = "7337537599"
    whatsapp: Optional[str] = "917337537599"
    services: Optional[str] = "Deluxe Executive Suites, Fine Dining, Banquet Facilities"
    assets: Optional[Dict[str, Any]] = {}
    instructions: Optional[str] = None

class VoiceCommandRequest(BaseModel):
    transcript: str
    current_html: str
    business_data: Dict[str, Any]

class DeployRequest(BaseModel):
    html: str
    business_data: Dict[str, Any]

class RetainRequest(BaseModel):
    content: str
    tags: Optional[list[str]] = None
    metadata: Optional[Dict[str, str]] = None

class RecallRequest(BaseModel):
    query: str
    tags: Optional[list[str]] = None

class ReflectRequest(BaseModel):
    query: str
    context: Optional[str] = None

class DemoLearnRequest(BaseModel):
    instruction: str
    business_name: Optional[str] = "Hack Demo"

class DemoRecallRequest(BaseModel):
    query: str = "user design preferences visual style interaction animation"

class DemoGenerateRequest(BaseModel):
    project_name: str = "Aurelia AI"
    category: str = "AI Startup"
    location: str = "Hyderabad"
    instruction: str = "Build a premium AI startup website. Use the user's previously learned design preferences."


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "hindsight_connected": bool(hindsight_service.client),
        "hindsight_bank": settings.hindsight_bank_id,
        "groq_configured": settings.has_groq_credentials,
        "mode": "cloud" if hindsight_service.client else "local_resilient"
    }


@app.post("/api/upload-asset")
async def upload_asset(file: UploadFile = File(...)):
    """Upload logo, photo, video, or brochure PDF into the company asset vault"""
    try:
        ext = Path(file.filename).suffix.lower()
        unique_name = f"{uuid.uuid4().hex[:8]}_{file.filename.replace(' ', '_')}"
        dest_path = UPLOAD_DIR / unique_name
        
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_url = f"/uploads/{unique_name}"
        
        # Retain asset into Hindsight memory
        hindsight_service.retain(
            content=f"Company asset uploaded: {file.filename} (type: {ext}). Stored at {file_url}.",
            tags=["asset_upload", ext.strip(".")],
            metadata={"type": "world", "file_url": file_url, "filename": file.filename}
        )

        return {
            "success": True,
            "filename": file.filename,
            "url": file_url,
            "ext": ext
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload asset: {str(e)}")


@app.post("/api/generate")
def generate_website(req: GenerateRequest):
    """Run full pipeline: Intake -> Assets -> Copy -> Design -> Code -> Critics -> Hindsight Reflection -> Healing"""
    try:
        biz_data = req.model_dump()
        biz_data["assets"] = biz_data.get("assets") or {}
        result = orchestration_agent.run_pipeline(biz_data, initial_prompt=req.instructions)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# New endpoint: generate website from free-form user prompt using Groq
@app.post("/api/generate-from-prompt")
async def generate_from_prompt(prompt: str):
    """Accept a natural language description, obtain structured business data via Groq, and run the generation pipeline."""
    from backend.services.groq_service import GroqService
    groq = GroqService()
    # Retrieve business profile JSON from Groq LLM
    business_data = await groq.get_business_profile(prompt)
    # Run the existing orchestration pipeline
    result = orchestration_agent.run_pipeline(business_data)
    return result


@app.post("/api/voice-command")
def process_voice_command(req: VoiceCommandRequest):
    """
    Process user voice instruction:
    1. First check if it's an exact string replacement (e.g. change X to "Y" or replace X with Y).
    2. Otherwise run full agent reflection & regeneration loop.
    """
    try:
        # Recall durable preferences BEFORE applying the voice revision.
        recalled_before = hindsight_service.recall_user_preferences(
            category=req.business_data.get("category", ""),
            current_instruction=req.transcript,
            max_results=8
        )

        # Retain the user's voice instruction as an experience, then extract durable preferences.
        hindsight_service.retain(
            content=f"User voice instruction: '{req.transcript}'. Requested on business {req.business_data.get('name')}.",
            tags=["voice_command", "user_preference", "iteration"],
            metadata={"type": "experience", "learning": "voice_revision"}
        )
        learned_after = hindsight_service.learn_user_preferences(
            req.transcript,
            business_name=req.business_data.get("name", ""),
            workflow_id=f"voice-{uuid.uuid4().hex[:8]}"
        )

        # Check for fast exact voice replacement (e.g. change book a room to" book room")
        exact_match = code_generator_agent._try_exact_voice_replacement(req.current_html, req.transcript)
        if exact_match:
            # Retain successful replacement
            hindsight_service.retain(
                content=f"Applied exact voice replacement: '{req.transcript}' to {req.business_data.get('name')} layout.",
                tags=["exact_replacement", "success"],
                metadata={"type": "experience"}
            )
            return {
                "workflow_id": f"exact-{int(uuid.uuid4().hex[:6], 16)}",
                "business_data": req.business_data,
                "copy_data": {"headline": "Updated via Voice", "cta_primary": req.transcript},
                "design_system": {"theme_name": "Voice Customized"},
                "html": exact_match,
                "iterations_count": 1,
                "healed": True,
                "final_evaluation": {"average_score": 100, "passed": True},
                "logs": [{"timestamp": "Now", "stage": "Voice Engine", "message": f"Applied exact voice replacement: '{req.transcript}'"}],
                "voice_learning": {"recalled_before": recalled_before, "learned_now": learned_after}
            }

        # Otherwise run full pipeline with the voice instruction
        biz_data = req.business_data or {}
        biz_data["assets"] = biz_data.get("assets") or {}
        result = orchestration_agent.run_pipeline(biz_data, initial_prompt=req.transcript, existing_html=req.current_html)
        result["voice_learning"] = {
            "recalled_before": recalled_before,
            "learned_now": learned_after,
            "message": "Voice revision applied and durable lessons updated for future projects."
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/deploy")
async def deploy_website(req: DeployRequest):
    """
    Deploy the website instantly:
    1. Upload to public hosting via Bytebin (worldwide instant public link).
    2. Persist to local /site/{site_id} endpoint.
    3. Retain deployment metadata in Hindsight memory.
    """
    try:
        site_id = str(uuid.uuid4())[:8]
        biz_name = req.business_data.get("name", "site")
        
        # 1. Save locally
        local_file = DEPLOYED_DIR / f"{site_id}.html"
        local_file.write_text(req.html, encoding="utf-8")
        local_url = f"http://localhost:{settings.port}/site/{site_id}"

        # 2. Deploy to Bytebin for instant public URL
        public_url = None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    "https://bytebin.lucko.me/post",
                    content=req.html.encode("utf-8"),
                    headers={"Content-Type": "text/html; charset=utf-8"}
                )
                if res.status_code == 201:
                    key = res.json().get("key")
                    public_url = f"https://bytebin.lucko.me/{key}"
        except Exception as err:
            public_url = local_url

        final_public_url = public_url or local_url

        # 3. Retain in Hindsight
        hindsight_service.retain(
            content=f"Deployed production website for {biz_name} at URL: {final_public_url}. Stored site ID: {site_id}.",
            tags=["deployment", "production_url"],
            metadata={"type": "experience", "site_id": site_id, "url": final_public_url}
        )

        return {
            "success": True,
            "site_id": site_id,
            "public_url": final_public_url,
            "local_url": local_url,
            "business_name": biz_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deployment error: {str(e)}")


@app.get("/site/{site_id}", response_class=HTMLResponse)
def serve_deployed_site(site_id: str):
    """Serve any deployed site by ID"""
    file_path = DEPLOYED_DIR / f"{site_id}.html"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Site not found")
    return HTMLResponse(file_path.read_text(encoding="utf-8"))


@app.get("/api/memories")
def get_memories():
    """Retrieve all active memories in the Hindsight bank"""
    return {
        "count": len(hindsight_service.get_all_memories()),
        "memories": hindsight_service.get_all_memories()
    }


@app.post("/api/retain")
def retain_endpoint(req: RetainRequest):
    """Direct retain endpoint"""
    return hindsight_service.retain(content=req.content, tags=req.tags, metadata=req.metadata)


@app.post("/api/recall")
def recall_endpoint(req: RecallRequest):
    """Direct recall endpoint using TEMPR search"""
    return hindsight_service.recall(query=req.query, tags=req.tags)


@app.post("/api/reflect")
def reflect_endpoint(req: ReflectRequest):
    """Direct reflect endpoint"""
    return {"reflection": hindsight_service.reflect(query=req.query, context=req.context)}


@app.post("/api/demo/learn")
def demo_learn(req: DemoLearnRequest):
    """Teach the agent a durable preference for the live hackathon demonstration."""
    learned = hindsight_service.learn_user_preferences(
        req.instruction,
        business_name=req.business_name or "Hack Demo",
        workflow_id=f"demo-{uuid.uuid4().hex[:8]}"
    )
    return {
        "learned_preferences": learned,
        "memory_count": len(hindsight_service.get_all_memories())
    }


@app.post("/api/demo/recall")
def demo_recall(req: DemoRecallRequest):
    """Recall durable preferences for the live hackathon demonstration."""
    memories = hindsight_service.recall_user_preferences(
        current_instruction=req.query,
        max_results=8
    )
    return {
        "memories": memories,
        "memory_context": hindsight_service.format_memory_context(memories),
        "count": len(memories)
    }


@app.post("/api/demo/generate")
def demo_generate(req: DemoGenerateRequest):
    """Generate a real second project using Hindsight-recalled preferences."""
    memories = hindsight_service.recall_user_preferences(
        current_instruction=req.instruction,
        category=req.category,
        max_results=8
    )
    memory_context = hindsight_service.format_memory_context(memories)
    prompt = (
        f"{req.instruction}\n\n"
        "This is a fresh project. Apply the user's long-term preferences recalled from Hindsight below. "
        "Do not mention memory in the website copy.\n"
        f"{memory_context}"
    )
    business = {
        "name": req.project_name,
        "category": req.category,
        "location": req.location,
        "phone": "",
        "whatsapp": "",
        "services": "AI Strategy, Agent Engineering, Automation",
        "assets": {"photos": [], "logo_url": "", "video_url": "", "brochure_url": "", "pricing_tiers": []}
    }
    try:
        result = orchestration_agent.run_pipeline(business, initial_prompt=prompt)
        result["demo_learning"] = {
            "recalled": memories,
            "count": len(memories),
            "message": "A real website was generated using recalled Hindsight preferences."
        }
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mount static frontend directory
STATIC_DIR = Path(__file__).resolve().parent.parent / "frontend"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse("<h1>Hexo Elite AI Website Architect API is Running!</h1><p>Visit /docs for API specs.</p>")
