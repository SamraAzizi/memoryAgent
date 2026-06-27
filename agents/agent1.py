import logging
from datetime import datetime

from dotenv import load_dotenv
from agentspan.agents import Agent, AgentRuntime, ConversationMemory, run  # Added 'run'

import os
os.environ["AGENTSPAN_ENABLED"] = "false"  # Add this line

load_dotenv()
logging.basicConfig(level=logging.WARNING)
logging.getLogger("agentspan").setLevel(logging.ERROR)  # Changed to ERROR
logging.getLogger("conductor").setLevel(logging.ERROR)  # Changed to ERROR


def get_current_time() -> str:
    """returns the current local time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


conversation_memory = ConversationMemory(max_messages=50)

assistant = Agent(
    name="personal-Assistant",
    model="ollama/llama3",
    instructions="You are a helpful personal assistant. You will be given a task and you should ask questions to clarify the task if needed. Once you have enough information, you should provide a detailed plan to complete the task.",
    tools=[get_current_time],
    memory=conversation_memory
)

if __name__ == "__main__":
    print("Welcome to the Personal Assistant Agent!")
    
    with AgentRuntime() as runtime:
        while True:
            prompt = input("You: ").strip()
            if prompt.lower() == "q":
                break
            if not prompt:
                continue

            result = run(assistant, prompt, runtime=runtime)
            # Fix this line too - handle the output properly
            readable_result = result.output if isinstance(result.output, str) else result.output.get("result", str(result.output))
            conversation_memory.add_user_message(prompt)
            conversation_memory.add_assistant_message(readable_result)

            print(f"Assistant: {readable_result}")