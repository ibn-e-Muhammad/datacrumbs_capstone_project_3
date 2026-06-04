# ACME Corporation AI Customer Support Agent
## Comprehensive Development Report & Troubleshooting Post-Mortem

This project is a premium, AI-powered customer support application for **ACME Corporation** (an e-commerce store). The system features a modern Next.js frontend with a floating chat widget and a Python FastAPI backend acting as the agentic brain of the system. 

---

## 🏗️ Architecture Overview

The system operates on a dual-stack architecture to leverage Next.js for high-performance visual interfaces and Python for data parsing, LangChain agent executors, and local FAISS vector store indexing.

```mermaid
graph TB
    subgraph Frontend["Next.js Frontend (Tailwind CSS)"]
        LP["Landing Page<br/>(Hero, Features, Testimonials)"]
        CW["Chat Widget<br/>(Floating Glassmorphic Panel)"]
        CH["Chat History<br/>(React State / useChat Hook)"]
    end

    subgraph Backend["Python FastAPI Backend"]
        API["FastAPI Server<br/>/api/chat, /api/health"]
        RAG["RAG Service"]
        TC["LangChain ReAct Agent Executor"]
        
        subgraph Tools["Agent Tools"]
            T1["search_company_knowledge<br/>(FAISS RAG)"]
            T2["lookup_order<br/>(Google Sheets Read)"]
            T3["create_refund_ticket<br/>(Google Sheets Append)"]
        end
        
        subgraph DataLayer["Data & Models Layer"]
            VS["FAISS Vector Store<br/>(Company_sample.txt + Excel)"]
            EMB["Google Embeddings<br/>(models/gemini-embedding-2)"]
            LLM["Gemma 4 31B Agent Model<br/>(gemma-4-26b-a4b-it)"]
        end
    end

    subgraph External["External API Providers"]
        GS["Google Sheets API<br/>(Orders & Tickets tabs)"]
        GAI["Google AI Studio Developer APIs"]
    end

    LP --> CW
    CW --> |"POST /api/chat"| API
    API --> TC
    TC --> T1 --> RAG --> VS
    TC --> T2 --> GS
    TC --> T3 --> GS
    RAG --> EMB --> GAI
    TC --> LLM --> GAI
    CH --> CW
```

---

## 🛠️ System Components

### 1. Frontend (Next.js 14 on Vercel)
- **Landing Page**: Built following the PAS (Problem-Agitation-Solution) marketing copy framework with violet and indigo accents on a `bg-gray-950` background.
- **Floating Chat Widget**: Expandable chat panel styled with custom glassmorphism, responsive width controls, smooth entrance/exit animations, and auto-scrolling capabilities.
- **Client hook ([useChat.ts](file:///d:/Code/Projects/datacrumbs/capstone_project_3/frontend/src/hooks/useChat.ts))**: Manages short-term conversation states, formats role/content historical payloads, and handles error states.
- **Direct API Connection ([api.ts](file:///d:/Code/Projects/datacrumbs/capstone_project_3/frontend/src/lib/api.ts))**: The browser sends fetch requests directly to the live Railway backend to intentionally bypass Vercel Serverless Function 10-second timeouts.

### 2. Backend (Python FastAPI on Railway)
- **FastAPI Engine ([main.py](file:///d:/Code/Projects/datacrumbs/capstone_project_3/backend/main.py))**: Handles server startup routines, runs background FAISS vector store initialization on startup, and exposes API chat endpoints.
- **ReAct Agent Executor ([agent_service.py](file:///d:/Code/Projects/datacrumbs/capstone_project_3/backend/services/agent_service.py))**: Executes the main reasoning loops. Equipped with a custom agent template instructing the agent to follow a **Listen ➔ Analyze ➔ Identify ➔ Communicate ➔ Verify** workflow.
- **RAG Service ([rag_service.py](file:///d:/Code/Projects/datacrumbs/capstone_project_3/backend/services/rag_service.py))**: Loads local files (`Company_sample.txt` and `Company_products.xlsx`), splits content into semantic chunks using a `RecursiveCharacterTextSplitter`, embeds them using Google AI, and indexes them with a local `faiss-cpu` vector store.
- **Google Sheets Service ([sheets_service.py](file:///d:/Code/Projects/datacrumbs/capstone_project_3/backend/services/sheets_service.py))**: Interfaces with live Google Sheets using service account JSON credentials to retrieve orders or append tickets.
- **Tools Definition ([tools.py](file:///d:/Code/Projects/datacrumbs/capstone_project_3/backend/services/tools.py))**: Provides clean, structured bindings to bridge the LLM agent and Python service methods.

---

## 💡 The Development Journey

1. **Architecture Planning**: Designed a dual-stack system to keep LangChain dependencies isolated in Python while maintaining a premium web user experience using Next.js.
2. **Local RAG Integration**: Developed scripts to parse unstructured texts and spreadsheet catalogs to populate local semantic context buffers.
3. **External Syncing**: Created automated service-account credentials handlers to read and write records securely in Google Sheets.
4. **Agent Fine-Tuning**: Crafted the support persona instructions for the model, establishing strict guardrails around refund verification steps.

---

## 🔧 Extensive Engineering & Bug Troubleshooting (Post-Mortem)

During the development process, several critical integration, validation, compilation, and SDK bugs were identified and successfully resolved. The history, causes, and solutions are documented below:

### 1. Tailwind v4 `@apply` PostCSS Compilation Crashes
- **The Issue**: When launching the Next.js server, PostCSS crashed while compiling [globals.css](file:///d:/Code/Projects/datacrumbs/capstone_project_3/frontend/src/app/globals.css). The logs reported syntax errors such as:
  `Cannot apply unknown utility class selection:bg-violet-500` or `Cannot apply unknown utility class bg-gray-900/60` and `backdrop-blur-xl`.
- **The Cause**: Next.js Turbopack compiler coupled with Tailwind CSS v4 strictness fails to parse Tailwind alpha-modifiers or conditional modifiers (like `selection:`, opacity modifiers `/60`, or filter-based utilities) when executed under standard CSS `@apply` directives inside `@layer utilities`.
- **The Solution**: Replaced all problematic `@apply` CSS rules with vanilla CSS styling equivalent values inside the stylesheet (e.g., configuring `backdrop-filter: blur(24px)` and standard `rgba(...)` background rules for the `.glass` class directly in [globals.css](file:///d:/Code/Projects/datacrumbs/capstone_project_3/frontend/src/app/globals.css)).

### 2. Invalid Embedding Model Identifiers
- **The Issue**: Startup FAISS initialization failed, throwing errors about missing or invalid model formats.
- **The Cause**: Mismatches in Google Embedding API naming conventions (e.g. using `text-embedding-002` or `text-embedding-004` without the correct prefixes).
- **The Solution**: The embedding builder function `_get_embeddings` in [rag_service.py](file:///d:/Code/Projects/datacrumbs/capstone_project_3/backend/services/rag_service.py#L117-L124) was corrected to target Google's official `"models/gemini-embedding-2"` model format.

### 3. LangChain Tool JSON Output Stringification Failures
- **The Issue**: In multi-turn chat sessions, the agent's thought process crashed during tool calls. The logs showed tools receiving invalid inputs, such as raw JSON strings enclosed in markdown codeblocks (e.g., `{"order_id": "ORD-1001"}` or trailing markdown backticks), causing downstream lookups to fail.
- **The Cause**: ReAct agents running on Gemma or Gemini models frequently wrap structured tool inputs inside Markdown blocks or output raw JSON strings as single arguments instead of key-value bindings.
- **The Solution**: Engineered regex-based sanitizers inside the tool wrappers in [tools.py](file:///d:/Code/Projects/datacrumbs/capstone_project_3/backend/services/tools.py#L123-L132) and [tools.py](file:///d:/Code/Projects/datacrumbs/capstone_project_3/backend/services/tools.py#L187-L201). These filters strip markdown codes blocks (` ```json ` or ` ``` `) and parse nested properties from stringified inputs.

### 4. Pydantic Model Validation and Parameter Crashes
- **The Issue**: The agent threw `pydantic_core._pydantic_core.ValidationError` crashes (e.g., `CreateRefundTicketInput: reason field required`) or `TypeError: create_refund_ticket() missing 1 required positional argument: 'reason'`.
- **The Cause**: The ReAct agent executor attempts to call tools before collecting all arguments, or it passes them as one lump string, violating strict Pydantic inputs.
- **The Solution**:
  1. Updated `CreateRefundTicketInput` in [tools.py](file:///d:/Code/Projects/datacrumbs/capstone_project_3/backend/services/tools.py#L151-L153) to define `reason` with a default optional value (`default=""`).
  2. Modified the python signature in `create_refund_ticket` to support default values (`reason: str = ""`).
  3. Structured the inner tool logic to check if `reason` is empty and return a clear instruction asking the model to query the customer for the missing parameter, preventing crashes while upholding the refund validation rules.

### 5. Google Sheets Column Case-Sensitivity Mismatches
- **The Issue**: Order lookups frequently returned `Order not found` even though the user had successfully populated the Google Sheet.
- **The Cause**: gspread retrieves records as rigid dictionaries. Variations in column header casing (e.g., a user naming a column `Order Id` vs. `Order ID` or `Customer` vs. `customer`) resulted in key-misses.
- **The Solution**: Modified [sheets_service.py](file:///d:/Code/Projects/datacrumbs/capstone_project_3/backend/services/sheets_service.py#L100-L106) to normalize record dictionary keys to lowercase and strip whitespace during iteration. Casing checks for target values (like Order IDs) were also upgraded to case-insensitive evaluations.

### 6. `langchain-google-genai` finish_reason AttributeError Crash
- **The Issue**: Under certain conversational inputs (e.g., when asking about "freakish policies"), the server crashed, logging a stack trace ending with `AttributeError: 'int' object has no attribute 'name'`.
- **The Cause**: The Google Generative AI API (Gemma endpoint) occasionally returns unmapped integer values for a candidate's `finish_reason` (e.g., `19`). The `langchain-google-genai` library blindly attempts to access `.name` on this field, expecting it to be a protobuf Enum, causing the runtime crash.
- **The Solution**: Injected a runtime Python monkey-patch in [main.py](file:///d:/Code/Projects/datacrumbs/capstone_project_3/backend/main.py#L16-L34). The patch intercepts the response candidate validation method and wraps raw integers in a mock class exposing a `.name` attribute.

### 7. Vercel 502 Bad Gateway / 10-Second Timeout
- **The Issue**: Live deployments failed with a 502 Bad Gateway exactly 10 seconds into a conversation.
- **The Cause**: Vercel's free tier has a strict 10-second limit for serverless functions. ReAct agent loops taking longer than 10 seconds triggered Vercel's edge network to prematurely sever the connection.
- **The Solution**: Rewired the frontend architecture in [api.ts](file:///d:/Code/Projects/datacrumbs/capstone_project_3/frontend/src/lib/api.ts) to bypass Vercel's serverless `/api` layer and execute `fetch` requests directly from the client's browser to the live Railway domain, which enforces no such hard timeouts.

### 8. Pydantic-Settings Railway Variable Injection Failures
- **The Issue**: Initial Railway deployments crashed with `ValidationError` citing missing environment variables, even when configured via Railway dashboard.
- **The Cause**: `.env` is correctly git-ignored. Railway runtime required fully instantiated environment variables, but Pydantic's alias bindings occasionally require careful handling.
- **The Solution**: Validated `pydantic-settings` alias structures. More importantly, automated trailing-slash sanitization (`.rstrip("/")`) on `CORS_ORIGINS` parsing in [main.py](file:///d:/Code/Projects/datacrumbs/capstone_project_3/backend/main.py) to prevent preflight rejections caused by slight mismatches in user configurations.

---

## 🔍 Model Configuration & Modifications Guide

If you need to change or upgrade the AI models, you can do so directly in the following files:

### 1. The LLM Agent Model
- **Location**: [agent_service.py](file:///d:/Code/Projects/datacrumbs/capstone_project_3/backend/services/agent_service.py#L163-L170)
- **Current Model**: `gemma-4-26b-a4b-it` (Gemma 4 31B API identifier)
- **How to edit**:
  ```python
  llm = ChatGoogleGenerativeAI(
      model="gemma-4-26b-a4b-it",  # Change this string to your preferred model
      temperature=0.4,
      ...
  )
  ```

### 2. The Embedding Model (RAG)
- **Location**: [rag_service.py](file:///d:/Code/Projects/datacrumbs/capstone_project_3/backend/services/rag_service.py#L117-L124)
- **Current Model**: `models/gemini-embedding-2`
- **How to edit**:
  ```python
  def _get_embeddings() -> GoogleGenerativeAIEmbeddings:
      settings = get_settings()
      return GoogleGenerativeAIEmbeddings(
          model="models/gemini-embedding-2",  # Replace with the new embedding model
          google_api_key=settings.google_api_key,
      )
  ```

---

## 🚀 Setup & Startup Instructions

### 1. Setup Environment Configuration
Create a `.env` file at the **project root** (same directory as this README, not inside `backend/` or `frontend/`). Populate it with your credentials:

```env
# Google AI Studio API Key
GOOGLE_API_KEY="your_api_key_here"

# Google Sheets Configuration
GOOGLE_SHEET_ID="1GtmWcVJSNZmgbBkDbc6tZtmhs18GosdB7h6tmsLNlxk"
GOOGLE_CLIENT_EMAIL="your_service_account_email_here"
GOOGLE_PROJECT_ID="your_google_project_id_here"
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour\nPrivate\nKey\n-----END PRIVATE KEY-----\n"

# CORS Configurations
CORS_ORIGINS="http://localhost:3000"
```

### 2. Live Production Deployment
**Backend (Railway)**
- Connected repository directly to Railway.
- Project uses the auto-generated root `requirements.txt` and `Procfile` to build and serve FastAPI via `uvicorn main:app --host 0.0.0.0 --port $PORT`.
- Add environment variables manually in the Railway dashboard Variables tab.

**Frontend (Vercel)**
- Set Vercel "Root Directory" to `frontend`.
- Expose the Railway public URL via the `NEXT_PUBLIC_API_URL` environment variable (e.g., `https://my-railway-app.up.railway.app`).

### 3. Run Locally (Development)

### 3. Run the Next.js Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install package dependencies
npm install

# Run the development server
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser to view the application.

---
*Last updated: June 4, 2026*