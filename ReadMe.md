# ACME Corporation AI Agent
**Comprehensive Development Report**

## Overview
This project is an AI-powered customer support agent for an e-commerce store. It features a Next.js 14 frontend landing page with a chat widget and a Python FastAPI backend acting as the brain of the agent. The agent is built with a ReAct architecture utilizing `gemini-2.5-flash-lite`, FAISS for Retrieval-Augmented Generation (RAG), and Google Sheets for live order lookups and ticket creation.

## Technical Architecture
### Frontend (Next.js 14)
- **Framework**: Next.js (App Router)
- **Styling**: Tailwind CSS with a Dark SaaS aesthetic
- **Components**:
  - Landing Page: Built with a Hero, Features, How It Works, Testimonials, and Footer.
  - Chat Widget: A premium floating chat interface with glassmorphism, gradient bubbles, and typing indicators.
- **State Management**: Custom `useChat` hook to maintain conversation history and interface with the backend.
- **Proxy**: `/api/chat` route to proxy requests to the FastAPI backend and bypass CORS issues.

### Backend (Python FastAPI)
- **Framework**: FastAPI
- **Agent Architecture**: LangChain ReAct (Reason-Act-Observe) agent.
- **LLM**: `gemma-4-31b-it` with a temperature of 0.4 for deterministic yet conversational outputs.
- **Memory**: `ConversationBufferMemory` keyed by `conversation_id`.
- **RAG System**:
  - Local vector store using `faiss-cpu`.
  - Texts loaded using `TextLoader` and `UnstructuredExcelLoader`.
  - Embeddings generated via `models/gemini-embedding-2` (`GoogleGenerativeAIEmbeddings`).
  - Search tool: `search_company_knowledge`.
- **Google Sheets Integration**:
  - Tool: `lookup_order` (fetches order status).
  - Tool: `create_refund_ticket` (appends refund tickets).
  - Uses `gspread` and Service Account credentials for secure access.

## Current Status & Executions
1. **Initial Generation**: Subagents generated the base Next.js template and Python backend files but hit quota limits.
2. **Manual Completion**: The remainder of the frontend UI components and the backend `main.py` entry point were written manually.
3. **Extensive Error Fixing & Engineering**:
   - **Agent/LLM Upgrade**: Upgraded base agent model to `gemma-4-31b-it`.
   - **Vector Database**: Upgraded embedding model from an invalid format to Google's flagship `models/gemini-embedding-2` to allow FAISS to initialize securely.
   - **JSON Parsing Resiliency**: Engineered a robust regex/markdown cleaner inside the Python tools to forcibly parse and recover stringified JSON payloads (e.g., handling trailing backticks) when LangChain's native JSON output parser inevitably fails.
   - **Pydantic Validation Guardrails**: Modified the Pydantic tool schemas (e.g., `CreateRefundTicketInput`) to make secondary fields optional. This prevents `ValidationError` backend crashes when LangChain hallucinates tool-calling formats and forces all data into a single string. Added corresponding Python function signature defaults (`reason: str = ""`) to align seamlessly with the new schema.
   - **Case-Insensitive Data Sync**: Rebuilt the `get_all_records` lookup logic in the Google Sheets service to aggressively normalize dictionary headers (e.g., `Order Id` vs `Order ID`) to prevent rigid exact-match failures when interfacing with live, user-modified Google Sheets.
   - **Frontend Patch**: Fixed a Tailwind CSS compilation crash in `globals.css` caused by Next.js parsing of the `selection:bg-violet-500/30` alpha modifier.

## Setup Instructions
1. Install backend dependencies: `pip install -r backend/requirements.txt`
2. Install frontend dependencies: `npm install` inside the `/frontend` directory.
3. Configure the `.env` file based on the provided template. Ensure a valid `GOOGLE_API_KEY` is used, as well as a valid Google Service Account.
4. Run the backend: `python backend/main.py`
5. Run the frontend: `npm run dev`

---
*Last updated: June 4, 2026*