clear chat in ui, override the system recommendations,

# Digital Sarathi - Project Flow & Technical Walkthrough

Digital Sarathi is an AI-powered agricultural consultant designed to assist Indian farmers with crop recommendations, government schemes, and pest management using a multi-agent system and RAG (Retrieval-Augmented Generation).

## 1. System Architecture & Flow

### User Interaction Flow
1.  **Authentication**: Farmer logs in or creates a profile (Location, Soil Type, Land Size, Water Source, Budget).
2.  **Consultant Chat (The Entry Point)**: 
    *   Powered by **LangGraph** and **Groq (Mixtral-8x7b)**.
    *   Uses a **ReAct Agent** pattern.
    *   **RAG Integration**: If the user asks about subsidies, pests, or specific practices, the agent calls the `query_knowledge_base` tool.
    *   The tool searches a **FAISS** vector index containing government PDF/text data.
3.  **Recommendation Pipeline**:
    *   Triggered from the Dashboard or Chat.
    *   A sequential multi-agent workflow:
        *   **Soil Agent**: Scores crops based on NPK/pH suitability.
        *   **Water/Climate Agent**: Fetches live weather (OpenWeather API) and scores based on irrigation needs.
        *   **Market Agent**: Analyzes simulated market demand and investment vs. return.
        *   **Sustainability Agent**: Checks crop rotation history to prevent soil depletion.
        *   **Conflict Engine**: Uses LLM reasoning to resolve mismatches (e.g., high-water crop in a drought-prone area).
4.  **Results**: Three distinct options are presented: *Safe/Stable*, *High Reward*, and *Soil Health*.

---

## 2. Implementation Journey

### Phase 1: Knowledge Base (RAG)
*   **Action**: Processed agricultural documents (MSP, PM-KISAN, Pest Advisory) into chunks.
*   **Tech**: `langchain-huggingface` (embeddings) + `FAISS` (vector store).
*   **Outcome**: Created a searchable "brain" for the consultant.

### Phase 2: Multi-Agent Orchestration
*   **Action**: Built the logic in `agents/orchestrator.py` to move beyond simple LLM prompting.
*   **Tech**: Custom scoring algorithms + LangGraph for state management.

### Phase 3: Frontend & UX
*   **Action**: Built a "Farmer-First" UI using Streamlit with custom CSS for a modern, accessible feel.

---

## 3. Issues Faced & Resolved

| Issue | Description | Resolution |
| :--- | :--- | :--- |
| **ModuleNotFoundError** | `torchvision` was missing, causing `transformers` to fail during RAG initialization. | Installed `torchvision` and updated `requirements.txt`. |
| **Deprecation Warnings** | `HuggingFaceEmbeddings` moved to `langchain-huggingface`. | Refactored `rag/retriever.py` to use the updated package. |
| **Transformers v5 Logs** | Extensive legacy alias/deprecation warnings in `transformers 5.x`. | Implemented global warning filters and logging suppression in `app.py` and `retriever.py`. |
| **LangGraph API Change**| `create_react_agent` deprecated `state_modifier` in favor of `prompt`. | Updated `agents/agent_graph.py` to use the `prompt` parameter. |
| **Groq Model Removal** | `mixtral-8x7b-32768` decommissioned by Groq. | Updated `config.py` to use `llama-3.1-8b-instant` (stable for tool calls). |
| **Tool Call Failures** | Intermittent 400 errors during tool validation with larger models. | Renamed tool to `query_rag` and implemented empathetic error handling in `views/chat.py`. |
| **API Rate Limits** | Frequent calls to LLM during agent loops. | Implemented message history trimming and optimized the state graph. |
| **Weather Data Fallback** | Pipeline failed when OpenWeather API keys were missing. | Added a robust fallback mechanism to "Neutral" weather states. |

---

## 4. Current Flow (Status: Functional)

*   **Login/Profile**: Fully functional with SQLite backend.
*   **Consultant Chat**: Integrated with LangGraph and RAG. Successfully retrieves scheme info.
*   **Recommendations**: Multi-agent scoring is active and produces weighted results.
*   **History**: Chat and recommendation history are persisted to the database.

---

## 5. Known Bugs & Pending Improvements

### Current Bugs 🐛
1.  **HF Hub Authentication Warning**: "You are sending unauthenticated requests to the HF Hub." 
    *   *Status*: Non-breaking, but slows down the first initialization.
2.  **BertModel UNEXPECTED Key**: A warning regarding `embeddings.position_ids` during model load.
    *   *Status*: Harmless (internal to `sentence-transformers`), but clutters logs.
3.  **Chat Rerun**: Occasionally, the `st.chat_input` requires a double-enter or triggers a full page refresh before displaying the latest message.

### Future Roadmap 🚀
*   **Voice Interface**: Allow farmers to speak their queries in local languages.
*   **Image Diagnosis**: Integrate a tool for farmers to upload photos of sick crops for pest identification.
*   **Real Market Data**: Replace simulated market scores with live eNAM API data.
