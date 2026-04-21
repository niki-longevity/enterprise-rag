# LLM调用模块
from openai import OpenAI
from langchain_openai import ChatOpenAI
from src.config.settings import settings


client = OpenAI(
    api_key=settings.deepseek_api_key,
    base_url=settings.deepseek_base_url
)


def get_llm_with_tools(tools):
    """获取绑定工具的LLM"""
    llm = ChatOpenAI(
        model=settings.deepseek_model,
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
        temperature=0.7
    )
    return llm.bind_tools(tools)
