from dataclasses import dataclass
from enum import Enum

class Config:
    SEED = 42
    MAX_TOKENS = 4096
    
    class Server:
        HOST = "fastmcp"
        PORT = 3001
        SSE_PATH = "/sse"
        TRANSPORT = "sse"
        
    class Agent:
        MAX_ITERATIONS = 10