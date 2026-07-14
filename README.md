# AI Social Media Agent

A modular, production-ready AI Social Media Agent inspired by FeedHive. The application acts as a central orchestrator (Master Agent) powered by Gemini and LiteLLM, coordinating sub-agents and domain-specific services to automate content creation, publishing, scheduling, analytics, competitor analysis, and team collaboration.

---

## 🌟 Features

- **Content Generation & Repurposing:** Generate engaging posts tailored to platform conventions (LinkedIn, Twitter, Facebook, etc.) and repurpose them seamlessly.
- **Smart Scheduling & Publishing:** Calculate optimal engagement times mathematically based on historical data.
- **LinkedIn OAuth 2.0 Authentication:** Seamless redirect flow to authenticate members and automatically save user tokens to secure storage.
- **Real LinkedIn API Integration:** Real-world connection to the LinkedIn API using member URNs and UGC post creation.
- **AI-generated LinkedIn Post Publishing:** Autonomously generate, approve, and publish content directly to a member feed.
- **Automatic Publication Confirmation:** Retrieve unique platform IDs and update publication status in the state machine.
- **SQLite Persistence (SQLAlchemy):** Full database schema configuration to store and manage scheduled publishing jobs queue permanently.
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
│   ├── auto_publishing_service.py      # Consolidated SQLite-backed publisher
│   ├── competitor_analysis_service.py
│   ├── linkedin_service.py             # Live LinkedIn API requests service
│   ├── smart_schedule_service.py       # Primary scheduler service
│   └── ...
│
├── tests/              # Test suite
│   └── test_publishing.py    # Unit tests validating LinkedIn APIs & Router errors
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
├── app.py              # Main FastAPI application & OAuth callback endpoints
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
```

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

#### Example Request Payload for `publish_post` tool:
```json
{
  "platform": "LinkedIn",
  "scheduled_datetime": "2026-07-14T12:00:00",
  "content": "Building an automated social posting scheduler with FastAPI, SQLite, and LinkedIn API!",
  "media_urls": []
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

---

## 🧪 Running Tests

Ensure your virtual environment is active and run `pytest` to execute all unit tests:

```bash
pytest
```
