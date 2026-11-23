
import os
from dotenv import load_dotenv

from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage

from chatbot.tools import banking_tools
from chatbot.prompts import SYSTEM_PROMPT

load_dotenv()

# Initialize Ollama LLM

llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "llama3.1"),
    base_url=os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    ),
    temperature=0
)

# Bind banking tools

llm_with_tools = llm.bind_tools(banking_tools)


# Chatbot node

def chatbot_node(state: MessagesState):

    messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ] + state["messages"]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }


# Create workflow

workflow = StateGraph(MessagesState)

workflow.add_node("chatbot", chatbot_node)

workflow.add_node(
    "tools",
    ToolNode(banking_tools)
)

workflow.add_edge(START, "chatbot")

workflow.add_conditional_edges(
    "chatbot",
    tools_condition
)

workflow.add_edge("tools", "chatbot")

banking_graph = workflow.compile()


# Chatbot response function

def get_chatbot_response(
    user_message,
    employee_id,
    role,
    branch_id
):

    config = {
        "configurable": {
            "employee_id": employee_id,
            "role": role,
            "branch_id": branch_id
        }
    }

    response = banking_graph.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        },
        config=config
    )

    return response["messages"][-1].content
