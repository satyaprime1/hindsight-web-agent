import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.agents.copywriter import copywriter_agent
from backend.agents.designer import design_agent
from backend.agents.coder import code_generator_agent
from backend.agents.critics import critic_panel
from backend.services.hindsight_service import hindsight_service

logger = logging.getLogger("orchestrator")

class OrchestrationAgent:
    """
    Coordinates the iterative generation, critic evaluation, Hindsight reflection,
    asset vault management, and self-correction loop.
    """

    def __init__(self):
        self.max_healing_iterations = 3

    def run_pipeline(
        self,
        business_data: Dict[str, Any],
        initial_prompt: Optional[str] = None,
        existing_html: Optional[str] = None
    ) -> Dict[str, Any]:
        workflow_id = f"wf-{int(datetime.now().timestamp())}"
        logs = []

        def log_event(stage: str, message: str, details: Any = None):
            entry = {
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "stage": stage,
                "message": message,
                "details": details
            }
            logs.append(entry)
            logger.info(f"[{stage}] {message}")

        instruction_summary = f" Instructions: '{initial_prompt}'" if initial_prompt else ""
        log_event("Intake", f"Processing {business_data.get('name')} in {business_data.get('location')} ({business_data.get('category')}).{instruction_summary}")

        # Learn durable user preferences BEFORE generation so memory can influence this run.
        learned_preferences = hindsight_service.learn_user_preferences(
            initial_prompt or "",
            business_name=business_data.get("name", ""),
            workflow_id=workflow_id
        )
        if learned_preferences:
            log_event("Hindsight Learning", f"Learned {len(learned_preferences)} durable user preference(s)", learned_preferences)

        # Retain company context & assets in Hindsight
        assets = business_data.get("assets", {})
        hindsight_service.retain(
            content=f"Business profile: {business_data.get('name')} in {business_data.get('location')}. Category: {business_data.get('category')}. WhatsApp: {business_data.get('whatsapp', business_data.get('phone'))}. Assets: {len(assets.get('photos', []))} photos, Logo: {bool(assets.get('logo_url'))}, Pricing Tiers: {len(assets.get('pricing_tiers', []))}.{instruction_summary}",
            tags=["business_intake", business_data.get("category", "local_biz").lower()],
            metadata={"type": "world", "workflow_id": workflow_id}
        )

        # Step 2: Hindsight Memory Recall
        recalled = hindsight_service.recall(
            query=f"design copy functionality directives for {business_data.get('category')} {initial_prompt or ''}",
            tags=["pattern", "directive"]
        )
        user_preferences = hindsight_service.recall_user_preferences(
            category=business_data.get("category", ""),
            current_instruction=initial_prompt or "",
            max_results=8
        )
        memory_context = hindsight_service.format_memory_context(user_preferences)
        log_event("Hindsight Recall", f"Retrieved {len(recalled)} architectural memories and {len(user_preferences)} reusable user preferences", {
            "architectural": recalled,
            "user_preferences": user_preferences
        })

        # Memory is now a first-class generation input.
        memory_instructions = (
            f"{initial_prompt or ''}\n\n"
            "LONG-TERM USER PREFERENCES RECALLED FROM HINDSIGHT:\n"
            f"{memory_context}\n\n"
            "Treat these as persistent preferences unless the current user instruction explicitly overrides them. "
            "Do not mention the memory system in generated website copy."
        ).strip()

        # Step 3: Run Copywriter & Designer with recalled user memory
        log_event("Copywriter Agent", "Generating copy using current request + recalled user preferences...")
        copy_data = copywriter_agent.generate_copy(business_data, instructions=memory_instructions)

        log_event("Design Agent", f"Selecting design system using category + recalled user preferences...")
        design_system = design_agent.choose_design_system(business_data.get("category", "default"), instructions=memory_instructions)

        # Step 4: Initial Code Generation
        log_event("Code Generator Agent", "Assembling tailored HTML with company assets, gallery, and pricing...")
        current_html = code_generator_agent.generate_website(
            business_data,
            copy_data,
            design_system,
            instructions=memory_instructions,
            existing_html=existing_html
        )

        # Step 5: Multi-Critic Reflection & Self-Healing Loop
        iteration = 1
        healed = False
        critic_results = None

        while iteration <= self.max_healing_iterations:
            log_event("Critic Panel", f"Running 4-Critic evaluation (Iteration {iteration})...")
            evaluation = critic_panel.evaluate_all(current_html, business_data)
            critic_results = evaluation

            log_event(
                "Critic Evaluation",
                f"Evaluation Score: {evaluation['average_score']}% (Passed: {evaluation['passed']})",
                evaluation['critic_results']
            )

            if evaluation["passed"]:
                log_event("Self-Correction Router", "All critics approved code! Passing to deployment.")
                healed = True
                
                hindsight_service.retain(
                    content=f"Successfully approved website layout for {business_data.get('name')} with score {evaluation['average_score']}%. Theme: {design_system['theme_name']}. Primary CTA: {copy_data.get('cta_primary')}.",
                    tags=["success_pattern", "approved"],
                    metadata={"type": "experience", "score": str(evaluation["average_score"])}
                )
                break
            else:
                issues_summary = "; ".join(evaluation["all_issues"])
                log_event("Hindsight Retain", f"Retaining critic flaws into memory bank: {issues_summary}")
                
                hindsight_service.retain(
                    content=f"Critic evaluation rejected code in iteration {iteration} due to: {issues_summary}",
                    tags=["critic_rejection", "mistake_guard"],
                    metadata={"type": "experience", "iteration": str(iteration)}
                )

                log_event("Hindsight Reflect", "Reflecting on flaws against architectural directives to formulate patch...")
                reflection_patch = hindsight_service.reflect(
                    query=f"How to heal these specific code flaws: {issues_summary}",
                    context=f"Business: {business_data.get('name')}, Category: {business_data.get('category')}"
                )
                log_event("Self-Correction Patch", "Hindsight generated actionable healing instructions", reflection_patch)

                iteration += 1
                if iteration <= self.max_healing_iterations:
                    log_event("Code Generator Agent", f"Applying self-healing patch for Iteration {iteration}...")
                    current_html = code_generator_agent.generate_website(
                        business_data,
                        copy_data,
                        design_system,
                        instructions=memory_instructions,
                        critique_patch_instructions=reflection_patch,
                        existing_html=current_html
                    )

        # Persist the outcome so later projects can learn from what worked or failed.
        if critic_results:
            outcome_tag = "accepted_pattern" if critic_results.get("passed") else "learning_outcome"
            hindsight_service.retain(
                content=(
                    f"Website generation outcome for {business_data.get('name')}: "
                    f"score {critic_results.get('average_score')}%. "
                    f"User-facing preferences active: {memory_context}. "
                    f"Critic issues: {'; '.join(critic_results.get('all_issues', [])) or 'none'}."
                ),
                tags=["generation_outcome", outcome_tag],
                metadata={"type": "experience", "workflow_id": workflow_id, "score": str(critic_results.get("average_score"))}
            )

        return {
            "workflow_id": workflow_id,
            "business_data": business_data,
            "copy_data": copy_data,
            "design_system": design_system,
            "html": current_html,
            "iterations_count": iteration if healed else self.max_healing_iterations,
            "healed": healed,
            "final_evaluation": critic_results,
            "recalled_memories": recalled,
            "recalled_user_preferences": user_preferences,
            "learned_preferences": learned_preferences,
            "memory_context": memory_context,
            "logs": logs
        }

orchestration_agent = OrchestrationAgent()
