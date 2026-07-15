# AI Social Media Agent

A modular, production-ready AI Social Media Agent inspired by FeedHive. The application acts as a central orchestrator (Master Agent) powered by Gemini and LiteLLM, coordinating sub-agents and domain-specific services to automate content creation, publishing, scheduling, analytics, competitor analysis, and team collaboration.

---

## 🌟 Features

- **Content Generation & Repurposing:** Generate engaging posts tailored to platform conventions (LinkedIn, Instagram, Twitter, Facebook, etc.) and repurpose them seamlessly.
- **Smart Scheduling & Publishing:** Calculate optimal engagement times mathematically based on historical data.
- **LinkedIn OAuth 2.0 Authentication:** Seamless redirect flow to authenticate members and automatically save user tokens to secure storage.
- **Real LinkedIn API Integration:** Real-world connection to the LinkedIn API using member URNs and UGC post creation.
- **Real Instagram Graph API Integration:** Two-step container-and-publish flow via the official Instagram Graph API.
- **AI-generated Post Publishing:** Autonomously generate, approve, and publish content directly to LinkedIn or Instagram.
- **Automatic Publication Confirmation:** Retrieve unique platform IDs and update publication status in the state machine.
- **SQLite Persistence (SQLAlchemy):** Full database schema configuration to store and manage scheduled publishing jobs queue permanently.
- **API Rate Limiting (slowapi):** IP-based rate limiting on the `/chat` endpoint (20 requests/minute) with HTTP 429 responses.
- **Automated Testing with Pytest:** Complete unit testing suite with mocked requests and router exception safety verification.
- **Audience & Competitor Intelligence:** Perform deep sentiment analysis on comments/DMs, draft automated replies, and execute competitor SWOT analysis.
- **Team Collaboration:** Task assignment, review status workflows, and approval cycles.

---

## 🛠️ Technology Stack

- **Core Language:** Python 3.10+
- **API Engine:** FastAPI (ASGI Server via Uvicorn)
- **Database ORM:** SQLAlchemy
- **Database Engine:** SQLite (Persistent database stored in `publish_jobs.db`)
- **Agent Orchestration:** LiteLLM-powered tool-calling router (defaulting to Gemini 2.5 Flash Lite)
- **Configuration & Validation:** Pydantic v2 & Pydantic Settings
- **HTTP Client:** Requests
- **Rate Limiting:** slowapi (starlette-compatible `limits` integration)
- **Test Framework:** Pytest

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
├── models/             # Pydantic schemas & SQLAlchemy entities
│   ├── brand_profile.py
│   ├── calendar_post.py
│   ├── publish_job.py         # SQLAlchemy PublishJob model & statuses
│   ├── publish_request.py     # Schema for publishing payloads
│   ├── publish_response.py    # Schema for publishing outcomes
│   └── ... (additional request/response models)
│
├── prompts/            # System & agent interaction prompts
│   ├── brand_voice_prompt.py
│   ├── competitor_analysis_prompt.py
│   └── ...
│
├── services/           # Business logic & background processes
│   ├── analytics_service.py
│   ├── auto_publishing_service.py      # Multi-platform publisher (LinkedIn + Instagram)
│   ├── competitor_analysis_service.py
│   ├── instagram_service.py            # Instagram Graph API integration (NEW)
│   ├── linkedin_service.py             # Live LinkedIn API requests service
│   ├── smart_schedule_service.py       # Primary scheduler service
│   └── ...
│
├── tests/              # Test suite
│   └── test_publishing.py    # Unit tests for LinkedIn, Instagram, rate limiting & router
│
├── tools/              # Central tool definitions wrapping services
│   ├── analytics_tool.py
│   ├── calendar_tool.py
│   ├── publishing_tool.py    # Interfaces with AutoPublishingService
│   └── ...
│
├── utils/              # Helper utilities (LiteLLM provider, factory wrappers)
│   ├── litellm_helper.py
│   └── provider_factory.py
│
├── .env.example        # Environment variables template
│   .gitignore          # Git exclusion rules
├── app.py              # Main FastAPI application, OAuth callbacks & rate limiting
├── config.py           # Application configurations (Pydantic settings)
├── database.py         # SQLAlchemy & SQLite database setup script
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
Ensure you provide a valid API key (e.g., `GEMINI_API_KEY`) based on your configured provider.

---

## ⚙️ Environment Variables
Open the `.env` file in the root of your project directory and configure the following:

```ini
# Core LLM API Key
GEMINI_API_KEY="AIzaSy..."

# LLM Selection Settings
LLM_PROVIDER="gemini"
MODEL_NAME="gemini/gemini-2.5-flash"

# LinkedIn OAuth & API Credentials
LINKEDIN_CLIENT_ID="your_client_id_here"
LINKEDIN_CLIENT_SECRET="your_client_secret_here"
LINKEDIN_ACCESS_TOKEN="your_access_token_here"

# Instagram Graph API Credentials
IG_ACCESS_TOKEN="your_instagram_access_token_here"
IG_BUSINESS_ACCOUNT_ID="your_instagram_business_account_id_here"
```

---

## 🔗 LinkedIn OAuth 2.0 Integration & Setup Guide

The application includes a production-ready, real-world integration with the **LinkedIn UGC (User Generated Content) API**. 

### 1. Creating the LinkedIn Developer App
1. Go to the [LinkedIn Developer Portal](https://www.linkedin.com/developers/) and log in.
2. Click **Create App** and fill in the details.
3. Under the **Products** tab, request access to:
   - **Share on LinkedIn** (grants the `w_member_social` permission).
   - **Sign In with LinkedIn** (used to retrieve member ID).
4. Configure redirect URIs in the **Auth** tab of your app to match:
   `http://localhost:8000/linkedin/callback`

### 2. Live OAuth Code Flow
1. Navigate to `http://localhost:8000/linkedin/login` in your browser.
2. Grant permissions in the LinkedIn authorization dialog.
3. The server callback at `/linkedin/callback` will exchange the authorization code for a User Access Token, save it into your `.env` file automatically, and update the application memory state.

---

## 📸 Instagram Graph API Setup

The application supports publishing images and videos directly to Instagram Business accounts via the **Instagram Graph API**.

### Prerequisites
1. You need a **Facebook Developer Account** and a **Facebook App** with the Instagram product added.
2. Your Instagram account must be a **Professional account** (Business or Creator) linked to a Facebook Page.

### Setup Steps
1. Go to [Meta for Developers](https://developers.facebook.com/) and create or open your Facebook App.
2. Add the **Instagram** product to your app under **Add a Product**.
3. Navigate to **Instagram → Basic Display** or **Instagram → Graph API** depending on your use case.
4. Required permissions for publishing:
   - `instagram_basic`
   - `instagram_content_publish`
5. Retrieve your **Instagram Business Account ID**:
   ```
   GET https://graph.facebook.com/v17.0/me/accounts?access_token={your_token}
   ```
   Then:
   ```
   GET https://graph.facebook.com/v17.0/{page_id}?fields=instagram_business_account&access_token={your_token}
   ```
6. Add the credentials to your `.env` file:
   ```ini
   IG_ACCESS_TOKEN="EAAGm0..."
   IG_BUSINESS_ACCOUNT_ID="17841405..."
   ```

### Publishing Flow
The service implements the official two-step flow:
1. **Create Media Container** — `POST /{ig-user-id}/media`
2. **Publish Media Container** — `POST /{ig-user-id}/media_publish`

Both image and video posts are supported (video posts use `media_type=VIDEO` + `video_url`).

---

## 🚦 API Rate Limiting

The `/chat` endpoint is protected by IP-based rate limiting powered by **slowapi**.

| Endpoint | Limit | Window |
|----------|-------|--------|
| `POST /chat` | 20 requests | per minute per IP |

When the limit is exceeded, the API responds with **HTTP 429 Too Many Requests**.

```json
{
  "error": "Rate limit exceeded: 20 per 1 minute"
}
```

This does not affect the Swagger UI (`/docs`) or any other endpoint.

---

## 🖥️ Running the Application

Start the FastAPI development server with reload enabled:
```bash
python app.py
```
Alternatively, run directly with Uvicorn:
```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
The server will start running at `http://127.0.0.1:8000`.

---

## 🧪 Running Tests

Ensure your virtual environment is active and run `pytest` to execute all unit tests:

```bash
pytest
```

To run with verbose output:
```bash
pytest -v
```

### Test Coverage

| Test | Description |
|------|-------------|
| `test_successful_linkedin_publishing_publish_post` | LinkedIn publish success (immediate) |
| `test_successful_linkedin_publishing_execute_job` | LinkedIn publish success (scheduled job) |
| `test_linkedin_publishing_401_unauthorized` | LinkedIn invalid/expired token (401) |
| `test_linkedin_publishing_403_forbidden` | LinkedIn permission denied (403) |
| `test_router_behavior_when_tool_fails` | Router handles tool errors gracefully |
| `test_instagram_publish_success` | Instagram publish success (immediate) |
| `test_instagram_invalid_token` | Instagram invalid token (code 190) |
| `test_instagram_permission_denied` | Instagram permission denied (code 10) |
| `test_instagram_publish_success_via_execute_job` | Instagram publish success (scheduled job) |
| `test_unsupported_platform_returns_validation_error` | Unsupported platform returns clean error |
| `test_unsupported_platform_execute_job_returns_error` | Unsupported platform in execute_job fails cleanly |
| `test_rate_limit_returns_429` | Rate limiter returns HTTP 429 when limit exceeded |

---

## 🔗 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/chat` | Primary conversational agent endpoint (rate limited: 20/min) |
| `GET` | `/health` | Health check |
| `GET` | `/linkedin/login` | Initiate LinkedIn OAuth flow |
| `GET` | `/linkedin/callback` | LinkedIn OAuth callback & token exchange |
| `GET` | `/docs` | Swagger UI (OpenAPI) |

---

## 🧪 Testing the Live LinkedIn Publisher

### Option A: Using the `/chat` Orchestrator (Orchestrated Flow)
The master agent will automatically invoke the publishing tool if the intent is recognized:
1. Navigate to `http://127.0.0.1:8000/docs` in your browser.
2. Under the **Agent** tag, click `POST /chat` -> **Try it out**.
3. Submit the following message:
   ```json
   {
     "message": "Publish a post to LinkedIn saying: Testing my new AI Social Media Agent database-backed publisher!"
   }
   ```
4. Click **Execute**. The AI Agent will recognize your intent to publish, execute the tool, and reply with the success status.

### Option B: Direct API Execution (Job Queues)
Call the `AutoPublishingService` methods programmatically or use the tool integrations.

#### Example Request Payload for `publish_post` tool (LinkedIn):
```json
{
  "platform": "LinkedIn",
  "scheduled_datetime": "2026-07-14T12:00:00",
  "content": "Building an automated social posting scheduler with FastAPI, SQLite, and LinkedIn API!",
  "media_urls": []
}
```

#### Example Request Payload for `publish_post` tool (Instagram):
```json
{
  "platform": "Instagram",
  "scheduled_datetime": "2026-07-14T12:00:00",
  "content": "Check out our latest AI product update! #AI #SocialMedia",
  "media_urls": ["https://example.com/your-image.jpg"]
}
```

#### Expected Successful API Response:
```json
{
  "publishing_status": "Success",
  "platform": "LinkedIn",
  "scheduled_time": "2026-07-14T12:00:00",
  "message": "Successfully published post to LinkedIn.",
  "publication_id": "urn:li:share:87364810294371"
}
```
