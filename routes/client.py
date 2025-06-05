import asyncio
import traceback
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.sse import sse_client
from rich.pretty import pprint
from typing import Optional, List, Dict, Any
from langchain_groq import ChatGroq
from .utils.logger import logger
from .doitr.client import server_url
from openai import OpenAI
from .utils.OpenAI import OpenRouterClient
import os
load_dotenv()
print(os.getenv("OPENAI_API_KEY"))
openai = OpenRouterClient("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")
class MCPClient:
    def __init__(self,server_url:str):
        self.session: Optional[ClientSession] = None
        self.tools = []
        self.messages = []  # Initialize messages list
        self.logger = logger
        self.openai_client = openai
        self._url = server_url

    
    async def connect_to_mcp_server(self) -> bool:
        """
        Establish connection to MCP server
        Returns True if connection successful, False otherwise
        """
        try:
            self.sse_context = sse_client(self._url)
            self.read_stream, self.write_stream = await self.sse_context.__aenter__()
            
            self.session_context = ClientSession(self.read_stream, self.write_stream)
            self.session = await self.session_context.__aenter__()
            
            await self.session.initialize()
            
            self.logger.info(f" Successfully connected to MCP server at {self._url}")
            return True
            
        except Exception as e:
            self.logger.error(f" Failed to connect to MCP server: {str(e)}")
            await self.cleanup()
            return False
    
    async def get_tools(self) -> List[Dict[str, Any]]:
        """
        Get available tools from MCP server
        Returns list of tools or empty list if not connected
        """
        if not self.session:
            print(" Not connected to MCP server")
            return []
        
        try:
            tools = await self.session.list_tools()
            # print(" Available MCP tools:")
            # pprint(tools)
            return tools.tools if hasattr(tools, 'tools') else []
            
        except Exception as e:
            self.logger.error(f" Failed to get tools: {str(e)}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Call a specific tool on the MCP server
        """
        if not self.session:
            self.logger.info(" Not connected to MCP server")
            return {}
        
        try:
            if arguments is None:
                arguments = {}
            
            result = await self.session.call_tool(tool_name, arguments)
            return result
            
        except Exception as e:
            self.logger.error(f" Failed to call tool '{tool_name}': {str(e)}")
            return {}
        
    async def search(self, query: str) -> Dict[str, Any]:
        """"
        returing the web search using the OpenAI client
        Args:
            query (str): The search query to perform.
        """ 
        try:
            self.logger.info(f" Performing web search for query: {query}")
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": query}],
                tools=self.tools,
                tool_choice="auto"
            )
            return response
            
        except Exception as e:
            self.logger.error(f" Error during search: {str(e)}")
            return {"error": str(e)}
        
    async def cleanup(self):
        """Clean up resources"""
        try:
            self.logger.info("Cleaning up resources")
            if self.session:
                # Close the session if it has a close method
                if hasattr(self.session, 'close'):
                    await self.session.close()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")


# Global MCP client instance
# mcp_client = MCPClient()