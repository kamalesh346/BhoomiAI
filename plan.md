previous commit "before multilinguality"
# BhoomiAI: Multilingual & Robust Memory Implementation Plan

## 🧭 Core Principle
The system maintains high accuracy by operating internally in **Pure English**. Multilinguality is achieved through a **Boundary Layer** translation strategy. No internal components (Specialized Agents, LangGraph Nodes, or Structured Memory) will handle translation logic.

---

## 🏗️ Refined Architecture Flow
1. **User Input (Any Indian Language)**
2. **[Boundary Layer - In]**
   - Normalize Options (A/B/C) using Regex (before translation).
   - Detect Language.
   - Translate Input → **English**.
3. **[Core System - English Only]**
   - **Intent Router (entry_node):** Detects physical changes or selections.
   - **Primary Brain (reasoning_node):** Generates expert advice/plans.
   - **Structured Memory (memory_node):** Summarizes history.
4. **[Boundary Layer - Out]**
   - Translate Final Response → **User Language**.
5. **User Output**

---

## 🛠️ Implementation Steps

### 1. Boundary Chat Handler (`api/chat_handler.py`)
Create a central wrapper to manage the lifecycle of a multilingual request:
- Intercept user messages.
- Orchestrate the translation and normalization steps.
- Invoke the English-only LangGraph.

### 2. Regex Option Parser (`api/utils/option_parser.py`)
Fix naive matching bugs by using robust regex:
- Detect: "Option A", "A", "Choose A", "Lets go with A".
- Standardize these into internal signals ("option a") *before* the message hits the translator.

### 3. Translation Module (`api/utils/translator.py`)
Implement two primary functions using the existing Llama-3.1-8b-Instant model:
- `translate_to_english(text)`
- `translate_from_english(text, target_lang)`

### 4. API & Database Synchronization
- **API:** Update `ChatMessageRequest` to accept a `language` field.
- **Database:** Add `language_preference` to the `farmers` table to remember the user's choice across sessions.

---

## 🧠 Prompt-Level Behavior Refinement
*Update internal node instructions to improve "Consultant" behavior (No code logic changes required):*

### For the Primary Brain (Reasoning Node):
- **Rule:** Greet the user **ONLY ONCE** per session.
- **Rule:** Do not repeat "Namaste" or introductions if history exists.
- **Rule:** Use strictly structured headers: ✔ Plan, 💰 Budget, 🌱 Setup, ⚠ Risks.

### For the Intent Router (Entry Node):
- **Rule:** If the user selects an option, **LOCK** that decision.
- **Rule:** Do NOT regenerate crop options (A/B/C) unless the user explicitly asks or physical constraints (water/budget) change.

---

## ⚠️ Critical Constraints
- ❌ **DO NOT** translate memory summaries (keep them in English for the Brain).
- ❌ **DO NOT** translate database JSON fields (Crop Data, Metrics).
- ❌ **DO NOT** translate structured control signals (Option IDs).
- ✅ **ONLY** translate the raw user text input and the final human-readable response.
