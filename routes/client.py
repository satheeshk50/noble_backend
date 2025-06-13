import asyncio
import traceback
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.sse import sse_client
from rich.pretty import pprint
from typing import Optional, List, Dict, Any
from .utils.logger import logger
from .doitr.client import server_url
from openai import OpenAI
from .utils.OpenAI import OpenRouterClient
import os
load_dotenv(dotenv_path='routes\\.env')
openai = OpenRouterClient(os.getenv("OPENAI_API_KEY"))
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
        
    async def process_query(self, query: str):
        """Process a query using OpenAI and available tools, returning all messages at the end"""
        try:
            self.logger.info(f"Processing new query: {query[:100]}...")
            
            # Initialize conversation with user query
            messages = [{"role": "user", "content": query}]
            self.messages.extend(messages)

            while True:
                self.logger.debug("Calling OpenAI API via OpenRouter")
                
                # Call LLM
                response = self.openai_client.call_llm(messages,tools=self.tools)
                self.logger.info(f"Received response from OpenAI: {response}...")
                # Add assistant response to messages
                assistant_message = {
                    "role": "assistant",
                    "content": response.content if hasattr(response, 'content') else ""
                }
                self.logger.info(f"Assistant response: {response}...")
                # Handle tool calls
                if hasattr(response, 'tool_calls') and response.tool_calls is not None:
                    # Add tool calls to the assistant message
                    assistant_message["tool_calls"] = []
                    
                    for tool_call in response.tool_calls:
                        assistant_message["tool_calls"].append({
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        })
                    
                    messages.append(assistant_message)
                    self.messages.append(assistant_message)
                    
                    # Execute each tool call
                    for tool_call in response.tool_calls:
                        tool_name = tool_call.function.name
                        try:
                            # Parse arguments (they come as JSON string)
                            import json
                            tool_args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            tool_args = {}
                        
                        self.logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                        
                        try:
                            # Call the MCP tool
                            result = await self.call_tool(tool_name, tool_args)
                            print(("next_step_instruction" in result))
                            if 'next_step_instruction' in result:
                                tool_result_message = {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "next_tool_call_instruction": result.next_step_instruction,
                                "content": str(result["search_results"]),
                                "topic": result["topic"]
                            }
                            # Add tool result to messages
                            else:
                                tool_result_message = {
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": str(result.content) if hasattr(result, 'content') else str(result)
                                }
                            
                            messages.append(tool_result_message)
                            self.messages.append(tool_result_message)
                            # await self.log_conversation(messages)
                            # final_response = self.call_llm_with_messages(messages)
                            
                            
                        except Exception as e:
                            error_msg = f"Tool execution failed: {str(e)}"
                            self.logger.error(error_msg)
                            
                            # Add error result to messages
                            tool_error_message = {
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": f"Error: {error_msg}"
                            }
                            
                            messages.append(tool_error_message)
                            self.messages.append(tool_error_message)
                            # await self.log_conversation(messages)
                    
                    # Continue the loop to get the final response
                    continue
                
                else:
                    # No tool calls, this is the final response
                    messages.append(assistant_message)
                    self.messages.append(assistant_message)
                    break
            return messages
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")

        
        
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