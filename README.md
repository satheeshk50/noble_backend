🌟 Noble Backend - LLM + MCP Tool Orchestrator

Welcome to the Noble Backend — a FastAPI-based backend system integrated with Large Language Models (LLMs) and external MCP tools (like web crawlers) to create a smart, dynamic, tool-augmented question-answering assistant.

🔍 What is this project about?

This backend project enables a conversational AI system that:

Accepts a user's natural language question.

Sends it to an LLM (like OpenAI or OpenRouter).

If needed, allows the LLM to call specialized tools (like web scrapers) hosted on an external MCP server.

Fetches results from those tools and sends them back to the LLM.

Finally, responds to the user with an accurate, context-rich answer.

All of this is handled automatically through a seamless FastAPI backend.

⚙️ Technologies Used

Component

Technology

API Framework

FastAPI

Tool Server

Custom MCP server

Orchestration

Docker & Docker Compose

Language Model

OpenAI / OpenRouter / Gemini

Tool Transport

Server-Sent Events (SSE)

Logging

Python Logging + Rich

🚀 Project Flow

User Query: A user asks a question (e.g., "Summarize the latest AI research article").

FastAPI Receives Query: The backend sends the query + available tools to the LLM.

Tool Call (if needed): If the LLM needs external data, it calls a tool (e.g., web_search).

Call MCP Server: The backend forwards this request to the MCP server.

Get Tool Result: MCP tool scrapes or processes the request and returns the result.

Final Answer: The LLM uses the tool output to generate a complete final answer.

📚 Project Structure

.
├── main.py                        # FastAPI entry point
├── Dockerfile                    # Docker build file
├── docker-compose.yml            # Compose for both servers
├── pyproject.toml                # Project dependencies
├── routes/
│   ├── doitr/
│   │   ├── client.py             # MCP Client for tool calls
│   │   └── config.py            # Centralized app settings
│   ├── MCP/
│   │   ├── main.py              # MCP server launcher
│   │   ├── crawler.py           # MCP Tool 1
│   │   └── crawler2.py          # MCP Tool 2
│   ├── utils/
│   │   ├── logger.py            # Logger with Rich
│   │   └── OpenAI.py            # OpenAI / OpenRouter API handler
│   └── web_search.py            # MCP Tool for search
├── .env                          # Environment variables
├── README.md                     # Project documentation

📆 Prerequisites

Docker & Docker Compose installed

OpenAI / OpenRouter API key (stored in .env)

Example .env:

OPENROUTER_API_KEY=your-api-key-here

🚧 How to Run the Project

Step 1: Clone the Repository

git clone https://github.com/yourusername/noble_backend.git
cd noble_backend

Step 2: Setup .env

Create a .env file at the root or in the routes/ folder with your API keys:

OPENROUTER_API_KEY=your-api-key-here

Step 3: Run with Docker Compose

docker-compose up --build

This command:

Builds and starts the FastAPI server on http://localhost:8000

Builds and starts the FastMCP server on http://localhost:3001

Step 4: Test the API

You can now send POST requests to:

http://localhost:8000/your-endpoint

Example via curl or Postman:

curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"question": "What is AI?"}'

🔧 Development Mode (Optional)

If you'd like to run it without Docker:

# Terminal 1 (FastMCP Server)
cd routes/MCP
python main.py

# Terminal 2 (FastAPI Server)
cd noble_backend root
uvicorn main:app --reload

Make sure .env is in place and ports are consistent in config.py.

💌 Contributions

Pull requests and issues are welcome. Let’s build better AI tooling together!

