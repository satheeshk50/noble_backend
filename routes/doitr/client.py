import contextlib

from mcp import ClientSession
from mcp.client.sse import sse_client
#importing pprint from rich
from rich.pretty import pprint
from .config import Config

def server_url():
    return f"http://{Config.Server.HOST}:{Config.Server.PORT}{Config.Server.SSE_PATH}"

@contextlib.asynccontextmanager
async def connect_to_server(url : str = server_url()):
    """Connect to the MCP server using SSE."""
    async with sse_client(url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            pprint(await session.list_tools())
            yield session
        
        
if __name__ == "__main__":
    import asyncio
    async def main():
        async with connect_to_server() as session:
            print("Connected to MCP server")
            print("Available tools:", await session.list_tools())
    
    asyncio.run(main())