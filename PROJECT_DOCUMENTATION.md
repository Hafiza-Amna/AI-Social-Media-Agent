# AI Social Media Agent — Technical Documentation & System Architecture

## 1. Project Overview

The **AI Social Media Agent** is an enterprise-grade, production-ready AI-powered social media management platform inspired by FeedHive and powered by an advanced LLM orchestration architecture. The application operates as a centralized Master Agent that coordinates modular sub-agents and specialized domain services to automate social media marketing workflows.

The system handles end-to-end social media operations, including platform-tailored content generation, A/B caption variation generation, mathematical smart scheduling, real-time analytics scoring, competitor SWOT analysis, direct message (DM) and public comment auto-reply assistants, content repurposing across platforms, team role management, and human-in-the-loop content review and approval prior to live social media publishing.

---

## 2. Problem Statement

Modern social media managers, marketing agencies, and brands face several core operational challenges:
1. **Manual Overhead and Fragmented Tools:** Managing multiple social accounts (LinkedIn, Instagram, etc.) requires juggling disparate tools for drafting, scheduling, analyzing, and reviewing posts.
2. **Lack of Human Oversight in Automated Posting:** Fully autonomous AI publishing without human verification can result in off-brand messages, typos, or compliance errors being posted publicly.
3. **Sub-optimal Posting Schedule:** Content is often published at arbitrary times rather than when targeted audiences are statistically most active.
4. **Platform Nuances:** Adapting core campaign messaging across different networks (LinkedIn vs. Instagram vs. Twitter) is tedious and time-consuming.
5. **Slow Response Times:** Community management (comments and direct messages) suffers from delayed responses, leading to missed leads and reduced engagement.

The AI Social Media Agent addresses these challenges by offering a single conversational AI interface with strict human approval controls, mathematical scheduling models, multi-platform integrations, and unified API endpoints.

---

## 3. Project Objectives

- **Unified LLM Architecture:** Provide a vendor-agnostic LLM orchestration layer (via LiteLLM) capable of switching between models (Groq Llama 3.3 70B, Google Gemini 2.5 Flash, OpenAI GPT-4o) via environment configuration.
- **Human-in-the-Loop Governance:** Implement a persistent approval queue where all AI-generated content enters `pending_review` status and cannot be published to live social networks until explicitly reviewed, edited, or approved by a human.
- **Real Platform Integrations:** Deliver direct, functional integrations with the LinkedIn UGC (User-Generated Content) API and Instagram Graph API (two-step container and publishing flow) with real-world OAuth 2.0 authentication.
- **Modular Tool & Service Design:** Decouple AI intent routing, FastAPI endpoint handlers, SQLAlchemy database models, and service layer implementations to ensure high testability, maintainability, and scalability.
- **Production Readiness:** Enforce IP-based rate limiting (20 req/min), structured Pydantic input/output schemas, SQLite persistence (`publish_jobs.db`), and automated Pytest test coverage.

---

## 4. Key Features

- **Conversational Master Agent:** Single natural-language entry point (`POST /chat`) that analyzes user requests, selects tools autonomously, and executes complex multi-step workflows.
- **Platform-Specific Content Generation:** Crafts posts optimized for target platforms (LinkedIn, Instagram, Twitter, Facebook, etc.) incorporating tone of voice, target audience, brand goals, hashtags, and CTAs.
- **A/B Caption Variant Generation:** Simultaneously generates Variant A (storytelling/emotional hook) and Variant B (concise/conversion-driven) for A/B testing marketing campaigns.
- **Human Content Approval Workflow:** Autonomously queues posts in SQLite under `pending_review`. Supports human review actions (`approve`, `reject`, `edit`) via `POST /review/{job_id}`. Approving auto-publishes the post immediately.
- **Real LinkedIn OAuth 2.0 & UGC API Integration:** Full OAuth authorization flow (`/linkedin/login` and `/linkedin/callback`), member profile URN retrieval, token persistence in `.env`, and live UGC post creation.
- **Real Instagram Graph API Integration:** Container creation (`/media`) and media publishing (`/media_publish`) using Instagram Business Account credentials and media URLs.
- **Smart Scheduling Engine:** Calculates mathematically optimal engagement time slots based on day-of-week audience activity algorithms.
- **Community Management Assistants:** Dedicated services and tools for public comment response generation and direct message (DM) classification/response.
- **Competitor Analysis & Analytics Scoring:** SWOT analysis generator for competitor strategies and engagement scoring algorithms for performance analytics.
- **API Rate Limiting & Swagger UI:** Integrated IP-based rate limiting via `slowapi` and interactive OpenAPI documentation at `/docs`.

---

## 5. System Architecture

The AI Social Media Agent follows a layered, decoupled service-oriented architecture:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             Client Application / UI                         │
│                    (Swagger UI / Frontend / Curl / REST)                    │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ HTTP Requests (JSON)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FastAPI Web Application                           │
│     • CORS Middleware           • IP Rate Limiter (20 req/min via slowapi)  │
│     • Global Error Handling     • OpenAPI / Swagger Documentation           │
└───────┬─────────────────────────────┬─────────────────────────────┬─────────┘
        │                             │                             │
        ▼                             ▼                             ▼
┌──────────────┐              ┌──────────────┐              ┌──────────────┐
│  POST /chat  │              │ POST /review │              │ GET /jobs    │
└───────┬──────┘              └───────┬──────┘              └───────┬──────┘
        │                             │                             │
        ▼                             │                             │
┌─────────────────────────────┐       │                             │
│       AI Intent Router      │       │                             │
│  (LiteLLM + Master Agent)   │       │                             │
└───────┬─────────────────────┘       │                             │
        │ Function Call               │                             │
        ▼                             ▼                             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               Service Layer                                 │
│  • AutoPublishingService         • LinkedInService      • InstagramService  │
│  • ContentGeneratorService       • SmartScheduleService • TeamService       │
└───────┬─────────────────────────────┬─────────────────────────────┬─────────┘
        │                             │                             │
        ▼                             ▼                             ▼
┌──────────────────────┐    ┌──────────────────┐    ┌─────────────────────────┐
│ SQLite Database      │    │  LinkedIn API    │    │  Instagram Graph API    │
│ (publish_jobs.db)    │    │  (UGC Post API)  │    │  (Media Container API)  │
└──────────────────────┘    └──────────────────┘    └─────────────────────────┘
```

---

## 6. Frontend and Backend Technologies

### Backend Technologies
- **Python 3.12 / 3.10+:** Primary runtime language.
- **FastAPI:** Modern, asynchronous high-performance Web framework for API endpoints.
- **Uvicorn:** Lightning-fast ASGI server implementation for running FastAPI.
- **SQLAlchemy:** ORM engine for relational database mapping and operations.
- **SQLite:** Lightweight file-based persistent relational database stored at `publish_jobs.db`.
- **Pydantic v2 & Pydantic Settings:** Data validation, strict request/response schema modeling, and type-safe environment configuration.
- **Requests:** Synchronous HTTP library for external API integrations (LinkedIn UGC API, Instagram Graph API).
- **slowapi:** Rate limiting library for FastAPI endpoints built on Starlette and `limits`.
- **Pytest:** Automated testing framework.

### Frontend Technologies
- **Single-Page Application (SPA):** Lightweight Vanilla HTML5, CSS3, and JavaScript ES6+ architecture for maximum maintainability and zero build overhead.
- **SaaS Dark Theme Design System:** Professional slate-dark visual theme (`#0b0f17` background, glassmorphism surface cards, Inter/Outfit Google Fonts, status indicators, and modal dialogs).
- **Remixicon CDN:** Iconography framework for social media platform badges and dashboard control elements.
- **FastAPI StaticFiles Mounting:** Served directly at `http://127.0.0.1:8001/` or `http://127.0.0.1:8001/dashboard` via FastAPI `StaticFiles` and `FileResponse`.

### Frontend Architecture & UI Sections
The frontend is organized into 8 core functional modules:
1. **Dashboard Overview (`dashboard.js`):** Real-time counters (Total, Pending, Scheduled, Published, Failed), platform health status, recent activity timeline, and quick action shortcuts.
2. **AI Content Generator (`content.js`):** Form interface for selecting platform (LinkedIn/Instagram), content prompts, tone of voice, content types (Standard/AB Variants), and media URLs. Connects to `POST /chat`.
3. **Content Approval Center (`approval.js`):** Human-in-the-Loop review hub displaying pending jobs, content text, created timestamps, and action buttons (`Approve & Publish`, `Reject`, `Edit`). Connects to `POST /review/{job_id}`.
4. **Content Calendar (`calendar.js`):** Timeline view of scheduled posts grouped by date/time, platform badge, and status.
5. **Social Media Connections (`connections.js`):** Status cards for LinkedIn OAuth 2.0 (`/linkedin/login`) and Instagram Graph API integrations.
6. **Publishing Center (`publishing.js`):** Complete job queue management table with status filtering (All, Pending, Approved, Published, Failed) and manual execution triggers (`POST /execute_job/{job_id}`).
7. **Analytics Dashboard (`analytics.js`):** Real database performance metrics (total jobs, published vs failed rates, platform distribution). Unmeasured metrics display "Data not available yet".
8. **Settings & Health (`settings.js`):** Live API health monitoring (`GET /health`), active LLM model identification, rate limiter policies, and masked credential security indicators.

---

## 7. Tools, Frameworks, and Libraries

| Category | Library / Framework | Version / Details | Purpose |
|---|---|---|---|
| **API Framework** | FastAPI | `0.115+` | Core REST API web framework |
| **ASGI Server** | Uvicorn | `0.34+` | ASGI web server for asynchronous handling |
| **ORM / Database** | SQLAlchemy | `2.0+` | Database object-relational mapping |
| **Data Validation** | Pydantic / Pydantic Settings | `2.10+` | Data schema validation and config management |
| **AI Gateway** | LiteLLM | `1.61+` | Vendor-agnostic LLM interface and tool calling |
| **HTTP Client** | Requests | `2.32+` | Executing REST requests to social platform APIs |
| **Rate Limiting** | slowapi | `0.1.9+` | IP-based rate limiting on sensitive API endpoints |
| **Env Management** | python-dotenv | `1.0+` | Loading environment variables from `.env` |
| **Testing** | Pytest / Pytest-AsyncIO | `8.0+` | Test execution, async testing, and assertions |

---

## 8. AI/LLM Architecture

The AI architecture is structured around a central **Master Agent** concept with vendor-agnostic execution powered by **LiteLLM**.

```
                           ┌──────────────────────────┐
                           │      User Request        │
                           └────────────┬─────────────┘
                                        │
                                        ▼
                           ┌──────────────────────────┐
                           │     AIIntentRouter       │
                           └────────────┬─────────────┘
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
              ┌─────────────────────┐       ┌────────────────────┐
              │ System Prompt &     │       │ LiteLLM Provider   │
              │ Tool Definitions    │       │ (Groq / Gemini /   │
              └──────────┬──────────┘       │  OpenAI / etc.)    │
                         │                  └──────────┬─────────┘
                         └──────────────┬──────────────┘
                                        │
                                        ▼
                           ┌──────────────────────────┐
                           │   Tool Selection &       │
                           │   Execution Engine       │
                           └────────────┬─────────────┘
                                        │
                     ┌──────────────────┼──────────────────┐
                     ▼                  ▼                  ▼
             ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
             │ Content Tool │   │ Publish Tool │   │ Analytics    │
             └──────────────┘   └──────────────┘   └──────────────┘
```

---

## 9. Google ADK Agent Workflow

The system adopts design principles from the **Google Agent Development Kit (ADK)**:
1. **Declarative Agent Configuration:** The Master Agent system prompt explicitly defines agent responsibilities, tool call expectations, argument constraints, and multi-step execution logic.
2. **Tool Registries:** Domain capabilities are encapsulated into `FunctionTool` objects (`tool_wrapper.py`) that declare Pydantic request classes or keyword arguments.
3. **Structured Intent Routing:** The agent evaluates user prompts against tool schema signatures, selects appropriate tools, executes the Python logic, and synthesizes the results.

---

## 10. LiteLLM and Groq Integration

- **LiteLLM Integration:** All model completion calls pass through `litellm.completion()`. This provides model fallback capabilities, automatic retries for transient network issues (`num_retries=2`), and uniform tool-calling JSON schema representations across LLM backends.
- **Groq Integration:** The default configuration uses `groq/llama-3.3-70b-versatile` via Groq's high-speed inference engine. Switching to another provider (e.g., `gemini/gemini-2.5-flash` or `openai/gpt-4o`) requires changing `LLM_PROVIDER` and `MODEL_NAME` in `.env`.

---

## 11. AI Intent Router

The `AIIntentRouter` class (`router.py`) acts as the central execution engine:
- **Initialization:** Reads registered tools from `create_master_agent()`, builds LiteLLM function schemas once at startup, and loads system prompts.
- **Three-Step Processing Pipeline:**
  1. **Initial LLM Call:** Sends system prompt, user prompt, and tool schemas to the model.
  2. **Tool Execution:** If the LLM returns `tool_calls`, the router executes the matching Python functions, captures their outputs, and appends the result to message history. Special handling is included for Instagram media URL extraction.
  3. **Response Synthesis:** Re-invokes the LLM with the tool outputs to generate a natural language summary. When a publish tool runs, the router returns a structured payload containing `job_id`, `status: "pending_review"`, and natural language confirmation text.

---

## 12. LinkedIn Integration

The LinkedIn integration (`services/linkedin_service.py`) provides real-world connectivity to LinkedIn's API:
- **OAuth 2.0 Flow:**
  - `GET /linkedin/login`: Generates LinkedIn authorization URL with requested scopes (`openid profile email w_member_social`).
  - `GET /linkedin/callback`: Exchanges authorization code for a User Access Token and updates `.env` dynamically via `update_env_token()`.
- **Member Profile URN Retrieval:** Queries `https://api.linkedin.com/v2/userinfo` to automatically obtain the authenticated user's profile ID and format it as `urn:li:person:{member_id}`.
- **UGC Post Creation:** Submits POST requests to `https://api.linkedin.com/v2/ugcPosts` with `author`, `lifecycleState: "PUBLISHED"`, and `specificContent` payloads.
- **Public URL Construction:** Formats public post links (`https://www.linkedin.com/feed/update/{urn}`) upon successful publication.

---

## 13. Instagram Integration

The Instagram integration (`services/instagram_service.py`) implements the official Meta Graph API two-step publishing flow:
- **Prerequisites:** Requires an Instagram Business Account ID (`IG_BUSINESS_ACCOUNT_ID`) and Access Token (`IG_ACCESS_TOKEN`).
- **Step 1 — Create Media Container:**
  - POST to `https://graph.facebook.com/v21.0/{IG_BUSINESS_ACCOUNT_ID}/media`
  - Body: `image_url` (or `video_url`), `caption`, `access_token`. Returns container `id`.
- **Step 2 — Publish Container:**
  - POST to `https://graph.facebook.com/v21.0/{IG_BUSINESS_ACCOUNT_ID}/media_publish`
  - Body: `creation_id` (container ID), `access_token`. Returns published media `id`.

---

## 14. Human Content Approval Workflow

To prevent unintended or unverified automated posts, all AI publishing tools route through a strict human approval queue:

```
[User Request via /chat]
           │
           ▼
[AI Generates Post Content]
           │
           ▼
[Queued in SQLite Database with status='pending_review']
           │
           ├───────────────────────────────┐
           ▼                               ▼
[Human Calls /review/{job_id}]   [Human Attempts Direct Execution]
           │                               │
  ┌────────┼────────┐                      ▼
  ▼        ▼        ▼            [BLOCKED: Error 400]
Approve  Reject   Edit
  │        │        │
  │        ▼        ▼
  │     Status:   Status: Approved +
  │    Rejected   Content Updated
  │        │        │
  └────────┼────────┘
           │
           ▼
[Auto-Publishing Triggered to LinkedIn / Instagram API]
           │
           ▼
[Status updated to 'published' + Returns Public URL & URN]
```

- **Safety Guarantee:** Posts in `pending_review` status CANNOT be executed directly via `/execute_job` until approved.
- **Review Actions:**
  - `approve`: Updates status to `approved` and triggers immediate live auto-publishing.
  - `reject`: Updates status to `rejected` and permanently blocks publishing.
  - `edit`: Updates post text content with human-supplied edits, sets status to `approved`, and triggers immediate live auto-publishing.
- **Immutability:** Once a job reaches `published` status, subsequent review requests are rejected with a validation error (`HTTP 400`).

---

## 15. Smart Scheduling Workflow

The smart scheduling service (`services/smart_schedule_service.py` & `tools/scheduling_tool.py`) provides data-driven posting recommendations:
- **Algorithm:** Maps weekday request parameters to peak historical engagement hours (e.g., Wednesday at 09:00 AM, Thursday at 01:00 PM, Tuesday at 10:00 AM).
- **Time Slot Selection:** Evaluates target audience timezones and platform-specific usage patterns to output an ISO 8601 formatted datetime string (`YYYY-MM-DDTHH:MM:SS`).

---

## 16. Auto-Publishing Workflow

Managed by `AutoPublishingService` (`services/auto_publishing_service.py`):
1. **Schedule / Queue:** Receives post content and platform details, creates a `PublishJob` record in SQLite with status `pending_review`, and returns the `job_id`.
2. **Review Validation:** Verifies job existence and checks if status is `approved`.
3. **API Execution:** Dispatches publishing to `LinkedInService.publish_text_post()` or `InstagramService.publish_photo_post()`.
4. **State Transition:** Upon API success, updates job status to `published`, records `published_at` timestamp and publication URN/ID. On API error, updates status to `failed` and records error details.

---

## 17. Database and Persistence Layer

- **Database Engine:** SQLite stored locally at `publish_jobs.db`.
- **ORM Framework:** SQLAlchemy with `declarative_base()`.
- **Database Initialization:** `init_db()` is called during application startup within the FastAPI lifespan context manager (`app.py`).
- **Table Schema (`publish_jobs` table):**

| Column Name | Data Type | Constraints / Details |
|---|---|---|
| `job_id` | String | Primary Key (UUID string) |
| `platform` | String | Platform name (LinkedIn, Instagram) |
| `scheduled_datetime` | DateTime / String | Scheduled posting time |
| `content` | Text | Post body text / caption |
| `media_urls` | JSON / Text | Serialized JSON list of media URLs |
| `status` | String | `pending_review`, `approved`, `rejected`, `published`, `failed` |
| `created_at` | DateTime | Timestamp when job was created |
| `reviewed_at` | DateTime | Timestamp when human review occurred |
| `reviewer` | String | Identity of human reviewer (default: "Human Reviewer") |
| `review_action` | String | Action taken: `approve`, `reject`, `edit` |
| `publication_id` | String | External platform post URN / ID returned after publishing |

---

## 18. API Endpoints

| Method | Path | Tags | Description | Rate Limit |
|---|---|---|---|---|
| `POST` | `/chat` | Agent | Main natural-language conversational AI endpoint | 20 / min per IP |
| `GET` | `/jobs` | Publishing | List publishing jobs in queue (filterable via `?status=`) | None |
| `POST` | `/review/{job_id}` | Review | Review pending post (`approve`, `reject`, `edit`) | None |
| `POST` | `/execute_job/{job_id}` | Publishing | Manually trigger execution of an approved job | None |
| `GET` | `/linkedin/login` | LinkedIn OAuth | Redirect user to LinkedIn OAuth page | None |
| `GET` | `/linkedin/callback` | LinkedIn OAuth | Handle OAuth callback, exchange code for token | None |
| `GET` | `/health` | System | Health check endpoint returning agent & model status | None |
| `GET` | `/docs` | Documentation | Interactive Swagger UI OpenAPI documentation | None |

---

## 19. Project Structure

```
AI SOCIAL MEDIA AGENT/
├── .env                       # Local environment variables (DO NOT COMMIT)
├── .env.example               # Template environment configuration file
├── .gitignore                 # Git ignore rules
├── README.md                  # Main repository README
├── PROJECT_DOCUMENTATION.md   # Project Architecture & System Documentation
├── TESTING_REPORT.md          # Comprehensive Test & Verification Report
├── agent.py                   # Master Agent definition & system prompt
├── app.py                     # FastAPI application entry point & API endpoints
├── audit_schemas.py           # Tool JSON Schema auditing utility
├── config.py                  # Pydantic Settings environment loader
├── database.py                # SQLAlchemy engine & SQLite setup
├── publish_jobs.db            # Persistent SQLite database file
├── requirements.txt           # Python package dependencies
├── router.py                  # AIIntentRouter (LiteLLM execution engine)
├── agents/                    # Multi-agent modules
│   └── social_media_agent.py  # Agent helper configuration
├── models/                    # Pydantic schemas and SQLAlchemy models
│   ├── account_connection.py
│   ├── analytics_request.py
│   ├── analytics_response.py
│   ├── brand_profile.py
│   ├── calendar_post.py
│   ├── calendar_request.py
│   ├── calendar_response.py
│   ├── comment_request.py
│   ├── comment_response.py
│   ├── competitor_request.py
│   ├── competitor_response.py
│   ├── content_request.py
│   ├── content_response.py
│   ├── dm_request.py
│   ├── dm_response.py
│   ├── platform_type.py
│   ├── publish_job.py         # SQLAlchemy PublishJob ORM model
│   ├── publish_request.py
│   ├── publish_response.py
│   ├── repurpose_request.py
│   ├── repurpose_response.py
│   ├── schedule_request.py
│   ├── schedule_response.py
│   ├── social_account.py
│   ├── team_request.py
│   ├── team_request_internal.py
│   └── team_response.py
├── prompts/                   # System prompts for domain sub-agents
├── services/                  # Business logic services
│   ├── analytics_service.py
│   ├── auto_publishing_service.py
│   ├── brand_voice_service.py
│   ├── comment_assistant_service.py
│   ├── competitor_analysis_service.py
│   ├── content_calendar_service.py
│   ├── content_generator.py
│   ├── content_repurposing_service.py
│   ├── dm_assistant_service.py
│   ├── instagram_service.py
│   ├── linkedin_service.py
│   ├── smart_schedule_service.py
│   ├── social_account_service.py
│   └── team_collaboration_service.py
├── tools/                     # FunctionTools exposed to the Master Agent
│   ├── __init__.py            # Tool exports
│   ├── analytics_tool.py
│   ├── calendar_tool.py
│   ├── comment_tool.py
│   ├── competitor_tool.py
│   ├── content_generator_tool.py
│   ├── dm_tool.py
│   ├── publishing_tool.py
│   ├── repurpose_tool.py
│   ├── scheduling_tool.py
│   └── team_tool.py
├── utils/                     # Utility modules
│   ├── litellm_helper.py      # LiteLLMProvider implementation
│   ├── llm_provider.py        # Abstract LLMProvider base class
│   ├── provider_factory.py    # LLM provider factory
│   └── tool_wrapper.py        # FunctionTool wrapper class
└── tests/                    # Pytest test suite
    └── test_publishing.py     # 21 integration & unit tests
```

---

## 20. Installation and Setup Instructions

### Prerequisites
- Python 3.10, 3.11, or 3.12 installed on your system.
- Git installed.

### Step 1: Clone Repository
```bash
git clone https://github.com/Career-institute-ai/ai-social-media-.git
cd ai-social-media-
```

### Step 2: Create and Activate Virtual Environment
- **Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\activate
  ```
- **macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 21. Environment Variables

Create a `.env` file in the project root based on `.env.example`. The table below describes required environment variable names (values must remain private):

| Variable Name | Description | Required / Optional |
|---|---|---|
| `APP_NAME` | Name of the application (default: "AI Social Media Agent") | Optional |
| `APP_ENV` | Application environment (`development` / `production`) | Optional |
| `DEBUG` | Debug mode flag (`True` / `False`) | Optional |
| `LLM_PROVIDER` | LLM provider identifier (`groq`, `gemini`, `openai`) | Required |
| `MODEL_NAME` | LiteLLM model identifier string (e.g. `groq/llama-3.3-70b-versatile`) | Required |
| `GROQ_API_KEY` | API Key for Groq inference service | Required if using Groq |
| `GEMINI_API_KEY` | API Key for Google Gemini API | Required if using Gemini |
| `OPENAI_API_KEY` | API Key for OpenAI API | Required if using OpenAI |
| `OPENROUTER_API_KEY` | API Key for OpenRouter service | Optional |
| `LINKEDIN_CLIENT_ID` | OAuth Client ID for LinkedIn App | Required for LinkedIn |
| `LINKEDIN_CLIENT_SECRET` | OAuth Client Secret for LinkedIn App | Required for LinkedIn |
| `LINKEDIN_ACCESS_TOKEN` | User Access Token for LinkedIn UGC API | Required for LinkedIn publishing |
| `IG_ACCESS_TOKEN` | Access Token for Meta / Instagram Graph API | Required for Instagram publishing |
| `IG_BUSINESS_ACCOUNT_ID` | Instagram Business Account ID | Required for Instagram publishing |
| `FACEBOOK_PAGE_ID` | Facebook Page ID linked to Instagram Account | Optional |

---

## 22. How to Run the Application

Start the FastAPI application server using Python:

```bash
.\.venv\Scripts\python.exe -m uvicorn app:app --reload --port 8001
```

The application will start at `http://127.0.0.1:8001`.

---

## 23. How to Run Tests

Run the complete test suite using Pytest via the virtual environment's Python executable:

```bash
.\.venv\Scripts\python.exe -m pytest -v
```

All 21 test scenarios will execute and validate publishing queues, rate limiting, human approval workflows, and router functionality.

---

## 24. Swagger/API Documentation

Interactive OpenAPI / Swagger documentation is automatically generated by FastAPI and available in your browser at:
- **Swagger UI:** `http://127.0.0.1:8001/docs`
- **ReDoc:** `http://127.0.0.1:8001/redoc`

You can test endpoints directly from Swagger UI, including creating chat prompts, reviewing jobs, and checking health status.

---

## 25. Security Considerations

- **Secrets Isolation:** `.env` is explicitly ignored via `.gitignore`. API keys and client secrets are never exposed in log outputs or API responses.
- **Human Approval Gate:** AI agents cannot autonomously publish posts to social media without human review, preventing unauthorized broadcasts.
- **Rate Limiting:** `/chat` is protected by `slowapi` (20 req/min per IP) against denial-of-service or token exhaustion attacks.
- **OAuth Token Security:** OAuth tokens are managed on the server side and exchanged over HTTPS.

---

## 26. Important Implementation Details

- **Single Lifetime Router Initialization:** `AIIntentRouter` is instantiated once during FastAPI application startup inside the `lifespan` manager and stored in `app.state.router` for maximum efficiency.
- **Automatic Image URL Extraction for Instagram:** The router inspects user messages for image URLs (`.jpg`, `.jpeg`, `.png`, `.webp`) and injects them into Instagram tool arguments automatically if omitted by the LLM.
- **SQLAlchemy Thread Safety:** Engine configured with `connect_args={"check_same_thread": False}` to support multithreaded FastAPI request handling cleanly.

---

## 27. Limitations

- **Image URL Dependency for Instagram:** Instagram Graph API mandates a publicly accessible image/video URL for container creation; text-only posts are not supported by Meta's Graph API.
- **Rate Limiting Storage:** `slowapi` currently uses in-memory IP tracking; multi-node deployment would require an external Redis backend.
- **Local SQLite File:** SQLite is suited for single-instance applications; enterprise multi-instance deployments should use PostgreSQL.

---

## 28. Future Improvements

- **PostgreSQL Database Migration:** Upgrade from SQLite to PostgreSQL for multi-region database replication.
- **Redis Rate Limiter Storage:** Integrate Redis with `slowapi` for distributed rate limiting.
- **Webhooks Integration:** Support Meta and LinkedIn incoming webhooks for real-time engagement monitoring.
- **Rich Media Upload Manager:** Build an inline S3/GCS media uploader for direct image asset management before posting to Instagram.
