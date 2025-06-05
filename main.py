from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routes import web_search
from routes.client import MCPClient
from routes.doitr.config import Config
from routes.utils.logger import logger
import os
import asyncio
import contextlib
from rich.pretty import pprint
from dotenv import load_dotenv

load_dotenv()


from routes.doitr.config import Config
print(f"HOST: {Config.Server.HOST}")
print(f"PORT: {Config.Server.PORT}")  
print(f"SSE_PATH: {Config.Server.SSE_PATH}")

mcp_client = None

def server_url():
    url = f"http://{Config.Server.HOST}:{Config.Server.PORT}{Config.Server.SSE_PATH}"
    logger.info(f"MCP Server URL: {url}")
    return url

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    global mcp_client
    logger.info("Starting FastAPI application...")
    
    try:
        logger.info("Initializing MCP Client...")
        mcp_client = MCPClient(server_url=server_url())
        logger.info("MCP Client created successfully")
        
        logger.info("Attempting to connect to MCP server...")
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                connected = await mcp_client.connect_to_mcp_server()
                if connected:
                    logger.info(" MCP server connected successfully")
                    mcp_client.tools = await mcp_client.get_tools()
                    yield
                else:
                    logger.error(f" Failed to connect to MCP server - attempt {attempt + 1}/{max_retries}")
                    
            except Exception as e:
                logger.error(f" Connection attempt {attempt + 1} failed: {str(e)}")
        
    except Exception as e:
        logger.error(f" Failed to initialize MCP client: {str(e)}")
        logger.exception("Full error traceback:")
        mcp_client = None
        
    logger.info("FastAPI startup complete")
    
app = FastAPI(
    title="Noble Backend API",
    description="API with MCP integration",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Include router
app.include_router(web_search.router, prefix="/web_search", tags=["web_search"])

def get_mcp_client():
    return mcp_client


@app.get("/")
async def root():
    return {"message": "Hello, World!", "mcp_status": "connected" if mcp_client else "disconnected"}

@app.get("/call-llm")
async def calling_llm(query : str):
    try:
        response = await mcp_client.search(query=query)
        return {"message": "LLM called successfully", "response": response}
    except Exception as e:
            logger.info(f"Failed to fetch tools: {str(e)}")

  


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify FastAPI and MCP tool status.
    """
    status = {
        "status": "healthy",
        "message": "FastAPI server is running",
    }

    if mcp_client:
        try:
            response = await mcp_client.session.call_tool("health_check")
            status["mcp_status"] = "connected"
            status["mcp_tool_response"] = response
        except Exception as e:
            status["mcp_status"] = "error"
            status["mcp_error"] = str(e)
    else:
        status["mcp_status"] = "disconnected"

    return {"response":response, "status": status}
