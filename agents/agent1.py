import logging
from datetime import datetime

from dotenv import load_dotenv
from  agentspan.agents import Agent, AgentRunTime,  ConversationMemory

load_dotenv()
logging.basicConfig(level=logging.WARNING)
logging.getLogger("agentspan").setLevel(logging.WARNING)
logging.getLogger("conductor").setLevel(logging.WARNING)


def get_current_time() -> str:
    """returns the current local time"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")



conversation_memory = ConversationMemory(max_messages=50)

assistant = Agent(
    name="personal-Assistant",
    model="openai/gpt-4",
    instructions="You are a helpful personal assistant. You will be given a task and you should ask questions to clarify the task if needed. Once you have enough information, you should provide a detailed plan to complete the task.",
    tools=[get_current_time],
    memory=converstion_memory

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
            readable_result = result.output.get("result")
            conversation_memory.add_user_message(prompt)
            conversation_memory.add_assistant_message(readable_result)

            print(f"Assistant: {readable_result}")