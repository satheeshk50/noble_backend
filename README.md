# 🔍 Noble Backend - LLM + MCP Powered Knowledge Extraction System

This project is a modular backend framework designed to handle intelligent content extraction and question answering using **Large Language Models (LLMs)** and a two-step **MCP (Model Context Protocol)** tool-based pipeline.

---

## 🧠 Project Overview

This project enables users to ask questions on any topic. Instead of relying solely on an LLM’s static knowledge, the system dynamically scrapes relevant web content, processes it using specialized tools (MCP), and passes the results back to the LLM for a more accurate and grounded response.

### 📌 Key Features

- Tool-driven LLM architecture using OpenAI or Groq LLMs
- Web scraping through a two-step process (via Firecrawl API or equivalent)
- Modular tool system for easy extensibility
- SSE-based communication between FastAPI backend and MCP service
- Dockerized setup with Docker Compose for seamless development

---

## 🧭 Project Flow

1. **User Query:** A user sends a question to the FastAPI backend.
2. **LLM Decision:** The LLM evaluates the query and determines if a tool is needed.
3. **MCP Tool Execution:**
   - If needed, the tool is invoked via an SSE (Server-Sent Events) channel from the MCP server.
   - The tool processes the request (e.g., crawling the web or extracting in-depth internal links).
4. **LLM Response:**
   - The tool’s output is returned to the LLM.
   - The LLM integrates this result into the final response and returns it to the user.

---

## 🗂️ Folder Structure

```bash
noble_backend/
│
├── routes/
│   ├── doitr/
│   │   ├── client.py
│   │   └── config.py
│   ├── MCP/
│   │   ├── crawler.py
│   │   ├── crawler2.py
│   │   └── main.py         # FastMCP server
│   ├── utils/
│   │   ├── logger.py
│   │   └── OpenAI.py
│   ├── client.py           # SSE client for FastAPI to MCP connection
│   ├── web_search.py       # Tool handler
│
├── main.py                 # FastAPI server entry
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── .env
└── README.md

## 🚀 How to Run the Project

### 1. ✅ Prerequisites

Ensure you have the following installed:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- A `.env` file with required secrets (OpenAI/Groq keys, Firecrawl key, etc.)

#### Example `.env` file:

```env
OPENAI_API_KEY=your_openai_key
FIRECRAWL_API_KEY=your_firecrawl_key
SERVER_HOST=localhost
SERVER_PORT=3001
SSE_PATH=/sse

## 🐳 Run with Docker Compose

To start the backend and MCP servers, run:

```bash
docker-compose up --build

## 🔧 What This Will Do

- ✅ Start the **FastMCP** service on port `3001`
- ✅ Start the **FastAPI** backend service on port `8000`

---

## 🌐 Access the Services

- **FastAPI Backend**: [http://localhost:8000](http://localhost:8000)
- **MCP Server (SSE Endpoint)**: [http://localhost:3001/sse](http://localhost:3001/sse)


## ⚙️ Configuration Highlights

- 🌀 **FastAPI** uses a **lifespan hook** to initialize the `MCPClient`.
- 🔗 `MCPClient` connects to the **MCP server** at startup and fetches available tools.
- 🧩 Tools are **modular** and easy to **register** or **extend**.
- 🔄 Communication between **FastAPI** and **MCP server** happens via **SSE (Server-Sent Events)** for real-time processing.

## 🧪 Example Use Case

> **Question:** _"Explain Quantum Computing in simple terms with examples from recent articles"_

### 🔁 Step-by-Step Flow

1. 🧠 **LLM** decides a web search tool is required.
2. 🕸️ `crawler.py` performs top-level scraping of relevant links and summaries.
3. 🔍 `crawler2.py` fetches deeper in-depth data from the internal links.
4. 📤 The results are **fed back to the LLM**.
5. 🧾 LLM constructs a **well-grounded, real-time response** using fresh data.

---

## 🛠️ Tech Stack

| Tech              | Usage                                              |
|-------------------|----------------------------------------------------|
| **FastAPI**       | Main backend server                                |
| **Python Asyncio**| Concurrency for SSE + tool execution               |
| **Docker**        | Containerization for consistent deployment         |
| **SSE**           | Real-time FastAPI ↔ MCP server communication       |
| **LLMs**          | OpenAI / Groq via `langchain_groq`                 |
| **Firecrawl**     | Web crawling API for scraping and retrieval        |

