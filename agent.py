import sys
import warnings

# Suppress LangChain / LangGraph deprecation notices for clean CLI output
warnings.filterwarnings("ignore")

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

from tools import get_destination_info

SYSTEM_PROMPT = (
    "You are a friendly and knowledgeable travel assistant.\n"
    "When a user asks about a travel destination, use the get_destination_info "
    "tool to fetch real-time weather and conditions. Based on the data, give "
    "helpful, concise travel advice — what to pack, best activities, and anything "
    "relevant for the trip. Always be encouraging and practical."
)


def build_agent():
    """Build and return the ReAct agent using ChatOllama and get_destination_info tool."""
    llm = ChatOllama(model="llama3.2", temperature=0.3)
    tools = [get_destination_info]
    agent = create_react_agent(llm, tools=tools)
    return agent


def ask(agent, user_input: str) -> str:
    """Send user input to the agent and return the final response content."""
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_input),
    ]
    result = agent.invoke({"messages": messages})
    return result["messages"][-1].content


def main():
    print("=" * 60)
    print("       🌍 Travel Assistant Agent — LangGraph CLI")
    print("  Model : Ollama llama3.2 (temperature=0.3)")
    print("  Tool  : get_destination_info (Open-Meteo API)")
    print("=" * 60)
    print("Type 'quit', 'exit', or 'q' to leave.\n")

    print("Initializing agent...")
    try:
        agent = build_agent()
    except Exception as e:
        print(f"Failed to initialize agent: {e}")
        sys.exit(1)

    print("Agent ready! Where would you like to travel?\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSafe travels! Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Safe travels! Goodbye!")
            break

        try:
            response = ask(agent, user_input)
            print(f"\nAgent:\n{response}\n")
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()
