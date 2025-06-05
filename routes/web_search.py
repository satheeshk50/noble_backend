from fastapi import APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from contextlib import asynccontextmanager
from .client import MCPClient
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from .doitr.config import Config
import os
from .utils.logger import logger
load_dotenv()

# class Settings(BaseSettings):
#     server_script_path: str = "C:\\Users\\sathe\\OneDrive\\Documents\\Nobel Thoughts\\MCP\\serper3\\main.py"

# settings = Settings()
# def server_url():
#     return f"http://{Config.Server.HOST}:{Config.Server.PORT}{Config.Server.SSE_PATH}"


# @asynccontextmanager
# async def lifespan(router: APIRouter):
#     # Startup
#     client = MCPClient()
#     try:
#         connected = await client.connect_to_server(server_url=server_url())
#         if connected:
#             logger.info("MCP server connceted sucessfully")
#         router.state.client = client
#         yield
#     except Exception as e:
#         raise Exception(f"Failed to connect to server: {str(e)}")
#     finally:
#         await client.cleanup()

router = APIRouter()


@router.get("/search")
async def search(query: str):
    """
    Perform a web search using the MCP client.
    """
    return {"message": "This endpoint is currently disabled for testing purposes."}
    # if not query:
    #     raise HTTPException(status_code=400, detail="Query parameter is required")

    # try:
    #     client: MCPClient = router.app.state.client
    #     response = await client.search(query)
    #     return response
    # except Exception as e:
    #     logger.error(f"Error during search: {str(e)}")
    #     raise HTTPException(status_code=500, detail="Internal Server Error")