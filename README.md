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
