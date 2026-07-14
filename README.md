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

---

## 🔗 LinkedIn API Integration & Setup Guide

The application includes a production-ready, real-world integration with the **LinkedIn UGC (User Generated Content) API**. When a user schedules or publishes a post to **LinkedIn**, the backend resolves the authenticated member's ID and publishes a live share on their feed instead of simulating the workflow.

### 1. Creating the LinkedIn Developer App
1. Go to the [LinkedIn Developer Portal](https://www.linkedin.com/developers/) and log in.
2. Click **Create App** and fill in the details (App name, associated LinkedIn Page, and app logo).
3. Under the **Products** tab, request access to:
   - **Share on LinkedIn** (This product grants the `w_member_social` permission needed to publish posts on your feed).
   - **Sign In with LinkedIn** (Used to retrieve the light profile and member ID using `r_liteprofile`).
4. Wait for approval (usually immediate for personal shares).

### 2. Generating the User Access Token
1. Go to the **Auth** tab of your developer app.
2. Locate the **Client ID** and **Client Secret**.
3. Use the [LinkedIn OAuth 2.0 Authorization Flow](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow) or the **LinkedIn Developer Portal Token Generator tool** to obtain a temporary **User Access Token** containing the `w_member_social` and `r_liteprofile` scopes.

### 3. Setting Environment Variables
Open the `.env` file in the root of your project directory and paste your credentials:
```ini
# LinkedIn API Credentials
LINKEDIN_CLIENT_ID="your_client_id_here"
LINKEDIN_CLIENT_SECRET="your_client_secret_here"
LINKEDIN_ACCESS_TOKEN="your_access_token_here"
```

---

## 🧪 Testing the Live LinkedIn Publisher

### Option A: Using the `/chat` Orchestrator (Orchestrated Flow)
The master agent will automatically invoke the publishing tool if the intent is recognized:
1. Navigate to `http://127.0.0.1:8000/docs` in your browser.
2. Under the **Agent** tag, click `POST /chat` -> **Try it out**.
3. Submit the following message:
   ```json
   {
     "message": "Publish a post to LinkedIn saying: Testing my new AI Social Media Agent integration!"
   }
   ```
4. Click **Execute**. The AI Agent will recognize your intent to publish, execute the tool, and reply with the success status.

### Option B: Triggering the Publisher Directly (For Developer Testing)
If you want to bypass the AI agent and call the publishing endpoint directly, you can trigger it programmatically or via Swagger docs (if exposed) or via curl/tools. 

*Note: Since the tool wraps the `AutoPublishService.publish_post(request)`, you can inspect the response structure returned by the internal publisher:*

#### Example Request Payload
```json
{
  "platform": "LinkedIn",
  "scheduled_datetime": "2026-07-13T10:30:00",
  "content": "Building an automated social posting scheduler with FastAPI and LinkedIn API!",
  "media_urls": []
}
```

#### Expected Successful API Response
```json
{
  "publishing_status": "Success",
  "platform": "LinkedIn",
  "scheduled_time": "2026-07-13T10:30:00",
  "message": "Successfully published post to LinkedIn.",
  "publication_id": "urn:li:share:87364810294371"
}
```

#### Expected Failure Response (Configuration Missing)
```json
{
  "publishing_status": "Failed",
  "platform": "LinkedIn",
  "scheduled_time": "2026-07-13T10:30:00",
  "message": "Configuration Error: LINKEDIN_ACCESS_TOKEN is missing or empty in your environment/settings.",
  "publication_id": null
}
```

---

## ⚠️ Platform Limitations & Best Practices

1. **Access Token Lifespan:** Default LinkedIn User Access Tokens expire in **60 days**. For production setups, implement an OAuth redirect redirect URI flow that handles token refresh (using `refresh_token`).
2. **Standard API Scopes:** To share to organizational pages (e.g. companies) instead of personal profile pages, the developer app must apply for the **Community Management API** product and request the `w_organization_social` scope.
3. **API Rate Limits:** LinkedIn has strict daily limits on the number of shares a member can publish (typically 25 per day). Keep this in mind when running automated agents.

---

## 🧪 Running Tests

To run the automated test suite, ensure your virtual environment is active and run `pytest`:

```bash
pytest
```

