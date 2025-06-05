# import asyncio
# import traceback
# from dotenv import load_dotenv
# from mcp import ClientSession
# from mcp.client.sse import sse_client
# from rich.pretty import pprint
# from typing import Optional, List, Dict, Any
# from langchain_groq import ChatGroq
# from .routes.utils.logger import logger
# from .routes.doitr.client import server_url
# from openai import OpenAI
# from .routes.utils.OpenAI import OpenRouterClient
# import os
# load_dotenv()
# print(os.getenv("OPENAI_API_KEY"))
# openai = OpenRouterClient("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")
# print(openai)
# class MCPClient:
#     def __init__(self):
#         self.session: Optional[ClientSession] = None
#         self.tools = []
#         self.messages = []  # Initialize messages list
#         self.logger = logger
#         self.openai_client = openai
        

#     # async def connect_to_server(self, server_url):
#     #     """Connect to the MCP server using SSE."""
#     #     try:
#     #         self.logger.info(f"Connecting to MCP server at {server_url}...")
            
#     #         # Use asyncio.wait_for to add timeout to the entire connection process
#     #         await asyncio.wait_for(
#     #             self._connect_with_timeout(server_url), 
#     #             timeout=30.0
#     #         )
            
#     #         self.logger.info("Connected to MCP server successfully")
#     #         return True
            
#     #     except asyncio.TimeoutError:
#     #         self.logger.error("Connection timed out after 15 seconds")
#     #         return False
#     #     except Exception as e:
#     #         self.logger.error(f"Failed to connect to server: {str(e)}")
#     #         return False
#     # async def _connect_with_timeout(self, server_url):
#     #     """Helper method to handle the actual connection."""
#     #     try:
#     #         async with sse_client(server_url) as (read_stream, write_stream):
#     #             self.session = ClientSession(read_stream, write_stream)
#     #             self.logger.info("Session created successfully. Initializing...")
                
#     #             # Add timeout specifically for initialization with longer duration
#     #             await asyncio.wait_for(self.session.initialize(), timeout=20.0)
#     #             self.logger.info("Session initialized successfully")
                
#     #             # Keep the connection alive for a moment to ensure it's stable
#     #             await asyncio.sleep(0.1)
                
#     #     except Exception as e:
#     #         self.logger.error(f"Error in _connect_with_timeout: {str(e)}")
#     #         raise
#     # SOLUTION 2: Connection with health check
#     async def connect_with_different_protocol(self, server_url):
#         """Try connection with different MCP protocol settings."""
#         try:
#             self.logger.info(f"Attempting connection with different protocol settings to {server_url}")
            
#             # Try with modified SSE client settings
#             import aiohttp
            
#             # Create custom HTTP session with specific settings
#             connector = aiohttp.TCPConnector(
#                 keepalive_timeout=30,
#                 enable_cleanup_closed=True,
#                 limit=10
#             )
            
#             timeout = aiohttp.ClientTimeout(total=30, connect=10)
            
#             async with aiohttp.ClientSession(
#                 connector=connector,
#                 timeout=timeout,
#                 headers={
#                     'Accept': 'text/event-stream',
#                     'Cache-Control': 'no-cache',
#                     'Connection': 'keep-alive',
#                     'User-Agent': 'MCPClient/1.0'
#                 }
#             ) as http_session:
                
#                 self.logger.info("Attempting SSE connection with custom settings...")
                
#                 async with http_session.get(server_url) as response:
#                     if response.status != 200:
#                         raise Exception(f"Server returned status {response.status}")
#                     else:
#                         self.logger.info(f'Server returnes status {response.status}, proceeding with SSE client')
                    
#                     self.logger.info("SSE connection established with custom settings")
                    
#                     # Now try the MCP connection
#                     async with sse_client(server_url) as (read_stream, write_stream):
#                         self.session = ClientSession(read_stream, write_stream)
#                         self.logger.info("Session created with custom protocol settings")
                        
#                         # Try initialization with very short timeout
#                         try:
#                             await asyncio.wait_for(self.session.initialize(), timeout=3.0)
#                             self.logger.info("Quick initialization succeeded")
#                             return True
#                         except asyncio.TimeoutError:
#                             self.logger.info("Quick init timed out, but session might still work")
#                             # Test if session works anyway
#                             if await self._test_session_functionality():
#                                 return True
#                             raise
                            
#         except Exception as e:
#             self.logger.error(f"Different protocol connection failed: {str(e)}")
#             return False
        
        
#     async def get_tools(self):
#         """Retrieve the list of tools available on the MCP server."""
#         self.logger.info("Retrieving available tools from MCP server...")
#         if not self.session:
#             raise Exception("Session not initialized. Call connect_to_server() first.")
#         try:
#             result = await self.session.list_tools()
#             self.tools = result.tools
#             return self.tools
#         except Exception as e:
#             raise Exception(f"Failed to retrieve tools: {str(e)}")
    
#     async def call_tool(self, tool_name: str, tool_args: dict):
#         """Call a tool with the given name and arguments"""
#         try:
#             result = await self.session.call_tool(tool_name, tool_args)
#             return result
#         except Exception as e:
#             self.logger.error(f"Failed to call tool: {str(e)}")
#             raise Exception(f"Failed to call tool: {str(e)}")
    
#     def format_tools_for_openai(self):
#         """Format MCP tools for OpenAI function calling format"""
#         if not self.tools:
#             return []
        
#         formatted_tools = []
#         for tool in self.tools:
#             formatted_tool = {
#                 "type": "function",
#                 "function": {
#                     "name": tool.name,
#                     "description": tool.description,
#                     "parameters": tool.inputSchema if hasattr(tool, 'inputSchema') else {}
#                 }
#             }
#             formatted_tools.append(formatted_tool)
#         return formatted_tools
    
#     def call_llm_with_messages(self, messages: List[Dict[str, Any]], model: str = "openai/gpt-4o-mini"):
#         """Call OpenAI LLM with the current messages using OpenRouterClient"""
#         try:
#             # Format tools for OpenAI
#             tools = self.format_tools_for_openai()
            
#             # Use the OpenRouterClient's internal method
#             params = {
#                 "model": model,
#                 "messages": messages,
#                 "extra_headers": self.openai_client.headers
#             }
            
#             # Add tools if available
#             if tools:
#                 params["tools"] = tools
#                 params["tool_choice"] = "auto"
            
#             # Make the API call using the internal client
#             response = self.openai_client.client.chat.completions.create(**params)
#             message = response.choices[0].message
            
#             # Log tool calls if present
#             if hasattr(message, "tool_calls") and message.tool_calls:
#                 self.logger.info(" Tool call detected!")
#                 for call in message.tool_calls:
#                     self.logger.info(f"Tool name: {call.function.name}")
#                     self.logger.info(f"Arguments: {call.function.arguments}")
#             else:
#                 self.logger.info("No tool call. Assistant replied with text.")
            
#             return message
            
#         except Exception as e:
#             self.logger.error(f"Failed to call LLM: {str(e)}")
#             raise Exception(f"Failed to call LLM: {str(e)}")
    
#     async def log_conversation(self, messages: List[Dict[str, Any]]):
#         """Log the conversation for debugging"""
#         self.logger.debug(f"Current conversation state: {len(messages)} messages")
#         for i, msg in enumerate(messages[-3:]):  # Log last 3 messages
#             self.logger.debug(f"Message {i}: {msg.get('role', 'unknown')} - {str(msg.get('content', ''))[:100]}...")

#     async def process_query(self, query: str):
#         """Process a query using OpenAI and available tools, returning all messages at the end"""
#         try:
#             self.logger.info(f"Processing new query: {query[:100]}...")
            
#             # Initialize conversation with user query
#             messages = [{"role": "user", "content": query}]
#             self.messages.extend(messages)
#             await self.log_conversation(messages)

#             while True:
#                 self.logger.debug("Calling OpenAI API via OpenRouter")
                
#                 # Call LLM
#                 response = self.call_llm_with_messages(messages)
                
#                 # Add assistant response to messages
#                 assistant_message = {
#                     "role": "assistant",
#                     "content": response.content if hasattr(response, 'content') else ""
#                 }
                
#                 # Handle tool calls
#                 if hasattr(response, 'tool_calls') and response.tool_calls:
#                     # Add tool calls to the assistant message
#                     assistant_message["tool_calls"] = []
                    
#                     for tool_call in response.tool_calls:
#                         assistant_message["tool_calls"].append({
#                             "id": tool_call.id,
#                             "type": tool_call.type,
#                             "function": {
#                                 "name": tool_call.function.name,
#                                 "arguments": tool_call.function.arguments
#                             }
#                         })
                    
#                     messages.append(assistant_message)
#                     self.messages.append(assistant_message)
#                     await self.log_conversation(messages)
                    
#                     # Execute each tool call
#                     for tool_call in response.tool_calls:
#                         tool_name = tool_call.function.name
#                         try:
#                             # Parse arguments (they come as JSON string)
#                             import json
#                             tool_args = json.loads(tool_call.function.arguments)
#                         except json.JSONDecodeError:
#                             tool_args = {}
                        
#                         self.logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                        
#                         try:
#                             # Call the MCP tool
#                             result = await self.call_tool(tool_name, tool_args)
#                             self.logger.info(f"Tool result: {result}")
                            
#                             # Add tool result to messages
#                             tool_result_message = {
#                                 "role": "tool",
#                                 "tool_call_id": tool_call.id,
#                                 "content": str(result.content) if hasattr(result, 'content') else str(result)
#                             }
                            
#                             messages.append(tool_result_message)
#                             self.messages.append(tool_result_message)
#                             await self.log_conversation(messages)
#                             # final_response = self.call_llm_with_messages(messages)
                            
                            
#                         except Exception as e:
#                             error_msg = f"Tool execution failed: {str(e)}"
#                             self.logger.error(error_msg)
                            
#                             # Add error result to messages
#                             tool_error_message = {
#                                 "role": "tool",
#                                 "tool_call_id": tool_call.id,
#                                 "content": f"Error: {error_msg}"
#                             }
                            
#                             messages.append(tool_error_message)
#                             self.messages.append(tool_error_message)
#                             await self.log_conversation(messages)
                    
#                     # Continue the loop to get the final response
#                     continue
                
#                 else:
#                     # No tool calls, this is the final response
#                     messages.append(assistant_message)
#                     self.messages.append(assistant_message)
#                     await self.log_conversation(messages)
#                     break

#             return messages

#         except Exception as e:
#             self.logger.error(f"Error processing query: {str(e)}")
#             self.logger.debug(f"Query processing error details: {traceback.format_exc()}")
#             raise
        
#     async def cleanup(self):
#         """Clean up resources"""
#         try:
#             self.logger.info("Cleaning up resources")
#             if self.session:
#                 # Close the session if it has a close method
#                 if hasattr(self.session, 'close'):
#                     await self.session.close()
#         except Exception as e:
#             self.logger.error(f"Error during cleanup: {str(e)}")


# # Usage example
# async def main():
#     client = MCPClient()
    
#     try:
#         # Connect to MCP server
#         await client.connect_to_server(server_url())
        
#         # Get available tools
#         tools = await client.get_tools()
#         print("Available tools:")
#         pprint(tools)
        
#         # Process a query
#         query = "What tools are available and how can I use them?"
#         messages = await client.process_query(query)
        
#         print("\nFinal conversation:")
#         for msg in messages:
#             print(f"{msg['role']}: {msg.get('content', 'N/A')}")
            
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         await client.cleanup()

# if __name__ == "__main__":
#     asyncio.run(main())