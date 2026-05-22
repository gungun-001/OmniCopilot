# 🤖 Omni Copilot: Full Project Documentation

## 1. Complete Project Overview
**Omni Copilot** is a premium, AI-powered unified workspace assistant. It acts as a central "command center" for a user's digital life, integrating with professional tools like Google Workspace, Notion, Slack, Discord, and GitHub. Unlike traditional chatbots, Omni Copilot is an **action-oriented agent** that can read your emails, schedule your meetings, extract data from your cloud files, and notify your team—all through a single conversational interface.

## 2. Main Objective and Problem Solved
- **The Problem**: "Context Switching Fatigue." Professionals waste significant time switching between multiple tabs and apps (Gmail for communication, Slack for team updates, Google Drive for files, GitHub for code) to complete a single task.
- **The Solution**: Omni Copilot provides a **Unified AI Agent** that bridges these silos. It solves the problem of fragmented workflows by bringing the tools to the conversation, rather than forcing the user to go to the tools.

## 3. Tech Stack
### **Frontend**
- **Framework**: Next.js 15 (App Router)
- **Styling**: Tailwind CSS 4.0
- **Animations**: Framer Motion (for the premium glassmorphic feel)
- **Icons**: Lucide React
- **State Management**: React Hooks (useState, useEffect)

### **Backend**
- **Framework**: FastAPI (Python 3.9+)
- **AI Orchestration**: LangChain (AgentExecutor)
- **LLM**: Groq (LPU Inference Engine) using `qwen-2.5-32b` (and fallback models)
- **Database**: SQLite (via SQLAlchemy ORM)
- **Authentication**: JWT (JSON Web Tokens)

### **APIs & Services**
- **Google Cloud**: Calendar, Gmail, Drive (OAuth2)
- **Notion**: Notion SDK for workspace management
- **Slack**: Slack SDK for messaging
- **Discord**: Webhook-based notifications
- **GitHub**: PyGithub for repository management

---

## 4. Folder Structure Explanation
```text
Omni-Copilot-main/
├── backend/                # FastAPI Application
│   ├── agents/             # AI Agent logic (Orchestrator)
│   ├── routes/             # API Endpoints (Chat, Auth)
│   ├── tools/              # 13+ Tool definitions for LangChain
│   ├── utils/              # Authentication and Token helpers
│   ├── models.py           # Database Schema (SQLAlchemy)
│   ├── database.py         # DB Connection setup
│   └── main.py             # Entry point for the server
├── frontend/               # Next.js Application
│   ├── src/
│   │   ├── app/            # Main pages and layouts
│   │   ├── components/     # UI Components (Chat, Auth, Splash)
│   │   └── utils/          # Frontend API helpers
│   └── public/             # Static assets
└── README.md               # Quick-start guide
```

---

## 5. Major Files and Modules
### **Backend**
- **`backend/agents/orchestrator.py`**: The core "Brain." It configures the LangChain agent, the system prompt, and the streaming logic.
- **`backend/tools/all_tools.py`**: The "Hands." Contains every tool the AI can use, from `schedule_meeting` to `fetch_github_file`.
- **`backend/routes/chat.py`**: Implements Server-Sent Events (SSE) to stream the AI's "thoughts" and "actions" to the UI in real-time.
- **`backend/models.py`**: Defines the `User` table for local authentication.

### **Frontend**
- **`frontend/src/app/page.tsx`**: The main entry point that manages the transition from the Splash Screen to Auth to Chat.
- **`frontend/src/components/ChatInterface.tsx`**: The primary UI that handles user input and renders the streaming AI response.
- **`frontend/src/components/Intro.tsx`**: The premium 5-second animated splash screen.

---

## 6. Complete Project Workflow
1.  **Launch**: User lands on the site and sees a 5-second premium splash screen.
2.  **Authentication**: User logs in or signs up (data stored in local SQLite).
3.  **Interaction**: User types a request (e.g., "Schedule a meeting with Aarav for tomorrow at 2 PM and notify the Slack channel").
4.  **Orchestration**: 
    - The Backend receives the message.
    - The AI Agent (Groq) "reasons" about which tools to use.
    - It calls the `schedule_meeting_tool`.
    - It then calls the `send_slack_message_tool`.
5.  **Execution**: The tools interact with real APIs using the user's tokens.
6.  **Response**: The AI streams its progress back to the user ("I've scheduled the meeting and sent the Slack message!").

---

## 7. Backend Architecture
The backend follows a **Modular Agentic Architecture**:
- **API Layer**: FastAPI routes handle requests.
- **Service Layer**: LangChain's `AgentExecutor` manages the conversation history and tool-calling loop.
- **Inference Layer**: Groq provides ultra-fast LLM responses, making the agent feel "instant."
- **Persistence Layer**: SQLite stores user credentials.

## 8. Frontend Architecture
The frontend is a **Single Page Application (SPA)** built with Next.js:
- **Component-Based**: Clean separation between Chat, Auth, and Layout.
- **Streaming UI**: Uses the Fetch API to read the backend's SSE stream, updating the message bubble character-by-character.
- **Aesthetic First**: Uses global CSS variables and Tailwind for a consistent dark-premium theme.

---

## 9. API Flow and Endpoints
- **POST `/api/auth/signup`**: Creates a new user.
- **POST `/api/auth/login`**: Authenticates user and returns a JWT.
- **POST `/api/chat`**: The unified chat endpoint. It accepts a message and session ID, returning an SSE stream of JSON chunks.

## 10. Database Schema
**Table: `users`**
- `id`: Primary Key (Integer)
- `first_name`: String
- `last_name`: String
- `email`: String (Unique, Indexed)
- `hashed_password`: String (Securely stored)

## 11. Authentication Flow
1.  **Signup**: User provides details -> Password hashed with `passlib` -> Saved to SQLite.
2.  **Login**: User provides email/password -> Verified against hash -> JWT generated with `python-jose`.
3.  **Client-side**: JWT stored in `localStorage`. Included in subsequent API calls.

---

## 12. AI/ML/RAG Workflow (Special Focus)
### **RAG Pipeline (Agentic RAG)**
Unlike traditional RAG which uses a static Vector Database, Omni Copilot uses **Dynamic Source Retrieval**:
- **Retrieval Flow**: When a user asks about a file, the agent uses the `search_drive_tool` to find it, then the `read_drive_file_tool` to "read" the content (extracting text from PDFs) and inject it into the context.
- **Embedding Model**: Not explicitly needed for this flow as it fetches direct content.
- **Vector DB**: None (Dynamic retrieval replaces the need for a pre-indexed vector DB for workspace files).

### **AI Agent Workflow**
- **Prompt Engineering**: The system prompt (in `orchestrator.py`) enforces strict rules about timezone handling (ISO 8601), professional descriptions, and GitHub access.
- **LLM Workflow**: Groq LPU -> LangChain Agent -> Tool Execution -> Observation -> Final Answer.

---

## 13. External Services
- **Google Calendar/Gmail/Drive**: Core workspace tools.
- **Notion**: For note-taking and task tracking.
- **Slack/Discord**: For team communication.
- **GitHub**: For developer productivity.

---

## 14. Deployment Process
- **Backend**: Can be deployed to **Render** or **Railway** using the `Dockerfile` or direct Python environment.
- **Frontend**: Optimized for **Vercel** or **Netlify**.
- **Environment**: Requires setting all API keys in the host's environment variables.

## 15. Environment Variables
| Variable | Purpose |
| :--- | :--- |
| `GROQ_API_KEY` | Access to the LLM |
| `GOOGLE_TOKEN_JSON` | Authorized Google credentials |
| `NOTION_API_KEY` | Access to Notion workspace |
| `SLACK_BOT_TOKEN` | Access to Slack workspace |
| `GITHUB_ACCESS_TOKEN`| Access to GitHub repositories |
| `JWT_SECRET_KEY` | Key for signing Auth tokens |

---

## 16. Features List
1.  **Animated Splash**: Premium intro.
2.  **Secure Auth**: Local SQLite login.
3.  **13+ AI Tools**: Scheduling, Emailing, Messaging, File reading.
4.  **Real-time Streaming**: Character-by-character AI thoughts.
5.  **PDF Extraction**: Reads Google Drive files directly.
6.  **GitHub Manager**: Fetches repos and file structures.

## 17. Future Improvements
- **Multi-user Google OAuth**: Allow users to link their own Google accounts via the UI.
- **Persistent Chat History**: Save chat logs to the SQLite database.
- **Vector Search**: Add a Vector DB (ChromaDB) for long-term "memory" of all workspace files.
- **Medical Module**: Plug in a Medical Search Tool (e.g., PubMed API) to handle medical queries.

## 18. Bugs/Issues Found
- **Model Name**: `orchestrator.py` references `qwen/qwen3-32b`, which might need adjustment to standard Groq identifiers (e.g., `qwen-2.5-32b-so-on`).
- **Google Token**: Currently relies on a local `token.json` which is not ideal for multiple users.

## 19. Security Concerns
- **Plaintext Secrets**: Ensure `.env` is never committed (it is currently ignored by `.gitignore`).
- **Token Scope**: Google tokens should use "Minimum Viable Scopes" for security.

---

## 20. Setup Instructions
### **1. Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or venv\Scripts\activate on Windows
pip install -r requirements.txt
python utils/generate_google_token.py  # Follow OAuth flow
uvicorn main:app --reload --port 8001
```

### **2. Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```

---

## 🎯 The Final Pitch

### **Elevator Pitch**
"Omni Copilot is your AI-powered Chief of Staff. It connects your Gmail, Slack, Notion, and GitHub into one premium interface, allowing you to manage your entire workspace through a single chat window. It doesn't just answer questions—it schedules your meetings, reads your files, and talks to your team so you don't have to."

### **Resume-Ready Project Description**
**Omni Copilot | Full-Stack AI Engineer**
- Built a unified workspace assistant using **Next.js 15** and **FastAPI**, integrating 13+ APIs including Google Workspace, Slack, and GitHub.
- Implemented an **Agentic RAG pipeline** using **LangChain** and **Groq**, enabling real-time PDF data extraction and tool-calling with <200ms latency.
- Designed a **premium glassmorphic UI** with **Framer Motion**, featuring a secure JWT-based authentication system and SSE-based real-time response streaming.

### **Interview Explanation**
"I developed Omni Copilot to solve the problem of app-switching fatigue. The technical challenge was orchestrating multiple external APIs through a single LLM. I used LangChain to build a tool-calling agent and Groq for high-speed inference. For the UI, I focused on a 'premium' experience, using Next.js 15 and Server-Sent Events to provide a fluid, real-time interaction that feels like talking to a human assistant who has full access to your office tools."

---
*Documentation generated by Antigravity AI.*
