import logging
from datetime import datetime

from dotenv import load_dotenv
from  agentspan.agents import Agent, AgentRunTime,  ConversationMemory

load_dotenv()
logging.basicConfig(level=logging.WARNING)
logging.getLogger("agentspan").setLevel(logging.WARNING)
logging.getLogger("conductor").setLevel(logging.WARNING)