# Agentic AI Chat Application

A full-stack chat application powered by an agentic AI that can use tools (web search, calculator, time, notes) to answer questions. Built with **Python (FastAPI)** backend and **Next.js (React)** frontend, using **Google Gemini** as the LLM.

## Architecture

```
┌─────────────────────┐       WebSocket        ┌──────────────────────┐
│   Next.js Frontend  │ ◄───────────────────► │   FastAPI Backend    │
│   (React 19 + TS)   │   real-time steps      │   (Python 3.11+)    │
│   Tailwind CSS      │                        │                      │
│   Port: 3000        │                        │   Port: 8000         │
└─────────────────────┘                        └──────────┬───────────┘
                                                          │
                                                          ▼
                                               ┌──────────────────────┐
                                               │   Gemini API         │
                                               │   (Agentic Loop)     │
                                               │                      │
                                               │   Tools:             │
                                               │   - Web Search       │
                                               │   - Calculator       │
                                               │   - Current Time     │
                                               │   - Create Note      │
                                               └──────────────────────┘
```

## Project Structure

```
ChatApp/
├── backend/
│   ├── main.py              # FastAPI server (REST + WebSocket endpoints)
│   ├── agent.py             # Agentic AI loop (Gemini + function calling)
│   ├── tools.py             # Tool definitions and execution logic
│   ├── config.py            # Environment configuration
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment variable template
│   └── .gitignore
├── frontend/
│   ├── app/
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Main chat page
│   │   └── globals.css      # Tailwind + dark theme styles
│   ├── components/
│   │   ├── Header.tsx       # Connection status and clear button
│   │   ├── ChatMessage.tsx  # User/assistant message bubbles (markdown)
│   │   ├── ChatInput.tsx    # Auto-resizing textarea input
│   │   └── ToolStep.tsx     # Expandable tool call/result visualization
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts       # API proxy configuration
│   ├── postcss.config.mjs
│   └── .gitignore
└── README.md
```

## Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **pnpm** (or npm)
- **Google Gemini API Key** — get one at https://aistudio.google.com/apikey

### Install Node.js (if not installed)

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
source ~/.bashrc
nvm install 22
nvm use 22
```

### Install pnpm (if not installed)

```bash
npm install -g pnpm
```

## Setup

### 1. Backend

```bash
cd ChatApp/backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```
GEMINI_API_KEY=AIzaSy...
```

Optional environment variables (in `.env`):

| Variable               | Default              | Description                  |
|------------------------|----------------------|------------------------------|
| `GEMINI_API_KEY`       | (required)           | Your Google Gemini API key   |
| `MODEL_NAME`           | `gemini-2.0-flash`   | Gemini model to use          |
| `MAX_TOKENS`           | `4096`               | Max tokens per response      |
| `MAX_AGENT_ITERATIONS` | `10`                 | Max tool-use loops per query |

Available models: `gemini-2.0-flash`, `gemini-2.0-flash-lite`, `gemini-2.5-pro-preview-05-06`, etc.

Start the backend:

```bash
python main.py
```

The API runs at **http://localhost:8000**.

### 2. Frontend

```bash
cd ChatApp/frontend

# Install dependencies
pnpm install

# Start development server
pnpm dev
```

The app runs at **http://localhost:3000**.

> **Using npm instead of pnpm?** Replace `pnpm install` with `npm install` and `pnpm dev` with `npm run dev`.

## Usage

1. Start the backend (Terminal 1)
2. Start the frontend (Terminal 2)
3. Open **http://localhost:3000** in your browser
4. Start chatting!

### Example Prompts

- "What time is it?"
- "Calculate the square root of 144 + 2^10"
- "Search the web for the latest news about AI"
- "Save a note about our meeting tomorrow at 3pm"
- "What is 15% tip on a $85 bill?"

## How the Agentic Loop Works

1. User sends a message via WebSocket
2. Backend sends the message to Gemini along with function declarations
3. If Gemini decides to call a function, the backend:
   - Streams the function call to the frontend (shown as an expandable step)
   - Executes the function
   - Streams the result back to the frontend
   - Sends the result back to Gemini
4. Step 3 repeats until Gemini produces a final text response (up to `MAX_AGENT_ITERATIONS`)
5. The final response is streamed to the frontend and rendered as markdown

## Available Tools

| Tool               | Description                                          |
|--------------------|------------------------------------------------------|
| `web_search`       | Search the web via DuckDuckGo instant answers API    |
| `calculator`       | Evaluate math expressions (supports sqrt, sin, log)  |
| `get_current_time` | Returns the current date and time                    |
| `create_note`      | Saves a titled note for the current session          |

## API Endpoints

| Endpoint       | Method    | Description                              |
|----------------|-----------|------------------------------------------|
| `/api/health`  | GET       | Health check                             |
| `/api/tools`   | GET       | List available tools                     |
| `/api/chat`    | POST      | Synchronous chat (send messages, get reply) |
| `/ws/chat`     | WebSocket | Real-time chat with tool step streaming  |

## Tech Stack

**Backend:**
- FastAPI — async web framework
- Google Generative AI SDK — Gemini API client with function calling
- httpx — async HTTP client (for web search tool)

**Frontend:**
- Next.js 15 — React framework with App Router
- React 19 — UI library
- TypeScript — type safety
- Tailwind CSS 4 — styling
- react-markdown — message rendering
