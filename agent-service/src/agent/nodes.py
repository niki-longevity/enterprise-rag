# LangGraph节点实现 - ReAct模式
from typing import Literal
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from src.config.settings import settings
from src.agent.tools import tools


def get_llm():
    return ChatOpenAI(
        model=settings.deepseek_model,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=0.7
    )


def agent_node(state):
    llm = get_llm().bind_tools(tools)
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


def should_continue(state) -> Literal["tools", "end"]:
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "end"

# 框架自带的工具执行节点
tool_node = ToolNode(tools)