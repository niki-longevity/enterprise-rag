# LangGraph节点实现 - ReAct模式
from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from src.config.settings import settings
from src.agent.tools import tools
from src.tracking.callback import tracking_callback


def get_llm():
    """获取LLM实例"""
    return ChatOpenAI(
        model=settings.tencent_model,
        api_key=settings.tencent_api_key,
        base_url=settings.tencent_base_url,
        temperature=0.7,
        callbacks=[tracking_callback],
    )


def agent_node(state):
    """Agent节点：调用LLM决定下一步"""
    llm = get_llm().bind_tools(tools)
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


def should_continue(state) -> Literal["tools", "end"]:
    """路由：判断是否需要调用工具"""
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "end"


tool_node = ToolNode(tools,handle_tool_errors= True)
