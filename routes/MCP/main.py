from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import httpx
import json
import asyncio
from typing import List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from doitr.config import Config
from utils.logger import logger
from crawler import ContentCrawler
from crawler2 import URLScraper
load_dotenv()



# Initialize FastMCP with explicit configuration
mcp = FastMCP(
    name="content crawler",
    host=Config.Server.HOST,
    port=Config.Server.PORT,
    sse_path=Config.Server.SSE_PATH,
)

# Initialize crawlers
try:
    # Use environment variables with fallbacks
    serper_key = os.getenv("SERPER_API_KEY", "5538f5b0ddbf20f1f349364f0895f17a19581c64")
    firecrawl_key = os.getenv("FIRECRAWL_API_KEY", "fc-1290f6ebe83f4641a1a04e3e03dd45fb")
    
    crawler = ContentCrawler(serper_key)
    crawler2 = URLScraper(firecrawl_key)
    
    logger.info("Crawlers initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize crawlers: {e}")
    raise

@mcp.tool()
async def get_content(topic: str) -> str:
    """
    Tool is used for explaining a topic by searching the web and fetching content 
    along with recent blogs with urls from the top two results.
    
    This tool performs a web search using the Serper API, retrieves the first two search results,
    and fetches the full text content from their URLs. The aggregated content is returned for
    further processing by the LLM, which generates an explanation or summary for the user.
    
    Args:
        topic (str): The topic or keyword to search for online.
    
    Returns:
        str: Combined textual content from the top two relevant web pages in JSON format.
    
    Raises:
        Exception: If an error occurs during the search or while fetching web pages.
    
    Example:
        get_content("Introduction to Machine Learning")
        # Returns the full text from the first two web pages found on the topic.
    """
    try:
        logger.info(f"Getting content for topic: {topic}")
        
        # Get search results
        results = crawler.crawl_related_content(topic, max_results=1, delay=1.0)
        
        # Add instruction for next tool usage
        instruction_text = """
        You got the content from the web and internal links.
        You need to decide which internal links have useful content which is helpful to explain the topic to the user.
        After that you need to call the get_internal_content tool to get the content from the internal links 
        by passing the list of URLs to that tool.
        Remember: pass only the required URLs in list of strings format.
        Provide the blogs summary along with the URLs to the user.
        """
        
        # Structure the response better
        response = {
            "search_results": results,
            "next_step_instruction": instruction_text,
            "topic_searched": topic
        }
        
        logger.info(f"Successfully retrieved {len(results)} results for topic: {topic}")
        return response
        
    except Exception as e:
        error_msg = f"Error during get_content execution: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg})

@mcp.tool()
async def get_internal_content(urls: List[str]) -> str:
    """
    Tool is used for fetching content from a list of given internal URLs.
    
    This tool retrieves the full text content from specified web page URLs. It is designed to be
    used after the initial web search to gather more detailed information from specific pages.
    
    Args:
        urls (List[str]): List of URLs of the web pages from which to fetch content.
    
    Returns:
        str: The full text content of the specified web pages in JSON format.
    
    Raises:
        Exception: If an error occurs while fetching the web pages.
    
    Example:
        get_internal_content(["https://example.com", "https://example2.com"])
        # Returns the full text content from the specified URLs.
    """
    try:
        logger.info(f"Getting internal content for {len(urls)} URLs")
        
        # Validate URLs
        if not urls or not isinstance(urls, list):
            raise ValueError("URLs must be provided as a non-empty list")
        
        # Log the URLs being processed
        for i, url in enumerate(urls):
            logger.info(f"Processing URL {i+1}: {url}")
        
        # Get content from URLs
        results = await crawler2.scrape_multiple_urls(urls=urls)
        
        # Structure the response
        response = {
            "scraped_content": results,
            "urls_processed": urls,
            "total_urls": len(urls)
        }
        
        logger.info(f"Successfully scraped content from {len(urls)} URLs")
        return json.dumps(response, indent=2)
        
    except Exception as e:
        error_msg = f"Error during get_internal_content execution: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"error": error_msg, "urls_attempted": urls if 'urls' in locals() else []})

# Add a health check endpoint (optional but helpful for debugging)
@mcp.tool()
async def health_check() -> str:
    """
    Simple health check tool to verify the server is working.
    
    Returns:
        str: Server status information.
    """
    try:
        status = {"status": "healthy",
            "server_name": "content ",
            "tools_available": [],
            "crawlers_initialized": True
        }
        logger.info("Health check requested - server is healthy")
        return status
    except Exception as e:
        error_msg = f"Health check failed: {str(e)}"
        logger.error(error_msg)
        return json.dumps({"status": "unhealthy", "error": error_msg})


# Add startup logging

def setup_server():
    """Setup and configure the server."""
    logger.info("="*50)
    logger.info("Starting FastMCP Content Crawler Server")
    logger.info(f"Host: {Config.Server.HOST}")
    logger.info(f"Port: {Config.Server.PORT}")
    logger.info(f"SSE Path: {Config.Server.SSE_PATH}")
    logger.info(f"Transport: {Config.Server.TRANSPORT}")
    logger.info("="*50)

if __name__ == "__main__":
    try:
        setup_server()
        
        # Add some startup delay to ensure everything is ready
        logger.info("Starting server...")
        
        # Run the server
        mcp.run(transport=Config.Server.TRANSPORT)
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        raise
    