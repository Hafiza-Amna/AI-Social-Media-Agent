# AI Social Media Agent

A modular, production-ready AI Social Media Agent inspired by FeedHive. The application acts as a central orchestrator (Master Agent) powered by Gemini and LiteLLM, coordinating sub-agents and domain-specific services to automate content creation, publishing, scheduling, analytics, competitor analysis, and team collaboration.

---

## 🌟 Features

- **Content Generation & Repurposing:** Generate engaging posts tailored to platform conventions (LinkedIn, Twitter, Facebook, etc.) and repurpose them seamlessly.
- **Smart Scheduling & Publishing:** Calculate optimal engagement times mathematically based on historical data and automate publication.
- **Audience & Competitor Intelligence:** Perform deep sentiment analysis on comments/DMs, draft automated replies, and execute competitor SWOT analysis.
- **Team Collaboration:** Seamless task assignment, content review workflows, and approval cycles.
- **Flexible Backend Architecture:** Unified FastAPI endpoints supporting asynchronous agent execution and provider-agnostic LLM integration.

---

## 🛠️ Technology Stack

- **Core Framework:** Python 3.10+
- **API Engine:** FastAPI (ASGI Server via Uvicorn)
- **Agent Orchestration:** Custom LiteLLM-powered tool-calling router (compatible with Groq, Gemini, OpenAI, etc.)
- **Configuration & Validation:** Pydantic v2 & Pydantic Settings
- **State Management:** SQLite database layer (SQLAlchemy ORM)

---

## 📂 Project Architecture

```text
AI-Social-Media-Agent/
│
├── agents/             # Agent definitions & system instructions
│   └── social_media_agent.py
│
├── api/                # FastAPI routing & API controller handlers
│
├── models/             # Pydantic schemas & database entities
│   ├── brand_profile.py
│   ├── calendar_post.py
│   ├── publish_job.py
│   └── ... (additional request/response models)
│
├── prompts/            # System & agent interaction prompts
│   ├── brand_voice_prompt.py
│   ├── competitor_analysis_prompt.py
│   └── ...
│
├── services/           # Business logic & background processes
│   ├── analytics_service.py
│   ├── auto_publishing_service.py
│   ├── competitor_analysis_service.py
│   └── ...
│
├── tools/              # Central tool definitions wrapping services
│   ├── analytics_tool.py
│   ├── calendar_tool.py
│   └── ...
│
├── utils/              # Helper utilities (LiteLLM provider, factory wrappers)
│   ├── litellm_helper.py
│   └── provider_factory.py
│
├── .env.example        # Environment variables template
├── .gitignore          # Git exclusion rules
├── app.py              # Main FastAPI application entry point
├── config.py           # Application configurations (Pydantic settings)
├── requirements.txt    # Application package dependencies
└── router.py           # Master AI Intent Router & Orchestrator
```

---

## 🚀 Setup Instructions

### 1. Clone & Set Up Directory
Clone this repository to your local system and navigate to the directory:
```bash
git clone <your-repository-url>
cd AI-Social-Media-Agent
```

### 2. Configure Virtual Environment
Create and activate a virtual environment to manage dependencies cleanly:
* **Windows:**
  ```powershell
  python -m venv .venv
  .venv\Scripts\activate
  ```
* **macOS/Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Install Dependencies
Install all required packages:
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your API credentials:
```bash
copy .env.example .env
```
Ensure you provide a valid API key (e.g., `GROQ_API_KEY`, `GEMINI_API_KEY`) based on your configured `LLM_PROVIDER` in `.env`.

---

## 🖥️ Running the Application

Start the FastAPI development server with reload enabled:
```bash
python app.py
```
Alternatively, run directly with Uvicorn:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```
The server will start running at `http://127.0.0.1:8000`.

---

## 🧪 Testing via Swagger UI

FastAPI provides an interactive OpenAPI (Swagger) interface out of the box.

1. Open your browser and navigate to: `http://127.0.0.1:8000/docs`
2. **Health Check:** Locate the `GET /health` endpoint under the **System** tag, click "Try it out", and click "Execute" to verify the API and AI model configuration are healthy.
3. **Chat/Agent Query:**
   - Locate the `POST /chat` endpoint under the **Agent** tag.
   - Click "Try it out".
   - Submit a prompt to test agent orchestration, e.g.:
     ```json
     {
       "message": "Generate a LinkedIn post about FastAPI and Python."
     }
     ```
   - Click "Execute" to observe the AI Agent executing tasks, calling the necessary tools, and returning a synthesized response.
