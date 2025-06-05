from dataclasses import dataclass
from enum import Enum

class ModelProvider(str,Enum):
    GROQ = "groq"

@dataclass
class ModelConfig:
    name: str
    temperature: float
    provider: ModelProvider

GROQ = ModelConfig(
    name="llama-3.3-70b-versatile",
    temperature=0.1,
    provider=ModelProvider.GROQ
)

class Config:
    SEED = 42
    MODEL = GROQ
    MAX_TOKENS = 4096
    
    class Server:
        HOST = "localhost"
        PORT = 3001
        SSE_PATH = "/sse"
        TRANSPORT = "sse"
        
    class Agent:
        MAX_ITERATIONS = 10