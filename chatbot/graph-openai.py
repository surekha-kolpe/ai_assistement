
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import ToolNode, tools_condition

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from chatbot.tools import banking_tools
from chatbot.prompts import SYSTEM_PROMPT


# Initialize language model

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)


# Connect tools to LLM

llm_with_tools = llm.bind_tools(banking_tools)


# LLM node

def chatbot_node(state: MessagesState):

    messages = [
        SystemMessage(content=SYSTEM_PROMPT)
    ] + state["messages"]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": [response]
    }


# Create LangGraph workflow

workflow = StateGraph(MessagesState)


# Add nodes

workflow.add_node(
    "chatbot",
    chatbot_node
)

workflow.add_node(
    "tools",
    ToolNode(banking_tools)
)


# Add edges

workflow.add_edge(
    START,
    "chatbot"
)

workflow.add_conditional_edges(
    "chatbot",
    tools_condition
)

workflow.add_edge(
    "tools",
    "chatbot"
)


# Compile graph

banking_graph = workflow.compile()


# Function to interact with chatbot

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
