# LangGraph状态定义
from typing import TypedDict, List, Optional, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
import operator


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    user_id: str
    session_id: str
