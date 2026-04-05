add multilingual property - do it after completing all 4 phases down
# Digital Sarathi: 8-Agent Architecture Implementation Plan

## Objective
Upgrade the current 5-node LangGraph conversational flow into a robust, production-ready **8-Agent Expert System** as defined in `agri_plan.pdf`. This plan adopts a phased approach, starting with a simplified scoring mechanism for the Top 3 crops, and eventually scaling to a "Pre-compute and Cache" strategy to optimize performance and cost.

---

## Phase 1: Foundation (Generate Top 3 Candidates)
*The immediate goal is to replace the generic LLM recommendation with a structured, multi-agent scoring system.*

1. **Agent Definitions:** Create individual modules/functions for the 8 specialized agents:
   - **Soil Agent:** Evaluates NPK, pH, and soil type suitability.
   - **Crop Knowledge Agent:** Filters viable crops from an Indian crop dataset.
   - **Water & Climate Agent:** Assesses feasibility based on water source and weather.
   - **Market Intelligence Agent:** Checks price signals and trends.
   - **Policy & Subsidy Agent:** Identifies applicable government schemes.
   - **Farmer Profile Agent:** Enforces land size and budget constraints.
   - **Sustainability Agent:** Considers crop rotation and soil preservation.
   - **Pest Advisory Agent:** Adds non-blocking risk alerts.
2. **State Update:** Update `AgentState` to include `candidate_crops` and `current_options`.
3. **Orchestrator Node (`recommendation_node`):**
   - Refactor this node to act as the Orchestrator.
   - Pass the farmer's profile through the agents to score a predefined list of crops.
   - Apply a Conflict Resolution Engine to finalize scores (e.g., reject high-water crops for rain-fed farms unless drip irrigation is planned).
   - Select the **Top 3** crops and format them as Options A, B, and C.

---

## Phase 2: Pre-compute & Cache (15-20 Candidates)
*Optimize the system to prevent redundant processing.*

1. **Expanded Scoring:** Modify the Orchestrator to generate a ranked list of the top 15-20 viable crops instead of just 3.
2. **State Caching:** Store this expanded list in the `AgentState` under a new key: `viable_candidates`.
3. **Initial Presentation:** The system still only presents the Top 3 (Options A, B, C) to the user initially, keeping the UI clean.

---

## Phase 3: Fallback Logic ("Show me more")
*Handle user requests for alternative options instantly.*

1. **State-Aware Reasoning:** Update the `reasoning_node` to recognize when a user rejects the initial options or asks for alternatives.
2. **Zero-Latency Retrieval:** Instead of re-running the 8 agents, the `reasoning_node` fetches the next 3 crops (e.g., ranks 4, 5, 6) from the `viable_candidates` list stored in the state.
3. **Seamless Presentation:** Present these new options to the user dynamically.

---

## Phase 4: Constraint-Triggered Re-runs
*Ensure the system adapts to fundamental changes in the farmer's situation.*

1. **Intent Router:** Implement a lightweight "Intent Router" (either as a LangGraph conditional edge or an initial LLM classification step) when receiving a new message.
2. **Routing Logic:**
   - **General Query:** Route to `reasoning_node` (answers using RAG/Knowledge).
   - **Request Alternatives:** Route to `reasoning_node` (fetches from `viable_candidates` cache).
   - **Constraint Change (e.g., "I got a loan for ₹2 Lakhs" or "I installed a borewell"):** Route back to the `recommendation_node`. The Orchestrator re-runs the 8 agents with the updated profile to generate a brand new master list of `viable_candidates`.

---

## Next Immediate Steps (Executing Phase 1)
1. Create a dummy/mock dataset of Indian crops (JSON) to serve as the knowledge base.
2. Build the basic scoring logic for the 8 agents (can be heuristic/rule-based initially, powered by LLM for complex reasoning).
3. Integrate the Orchestrator into the existing `recommendation_node`.
4. Test the generation of the Top 3 options based on different farmer profiles.