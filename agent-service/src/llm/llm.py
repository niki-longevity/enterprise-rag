# LLM调用模块
# 调用deepseek-chat生成回答
from openai import OpenAI
from src.config.settings import settings


# 初始化OpenAI客户端（兼容DeepSeek API）
client = OpenAI(
    api_key=settings.deepseek_api_key,
    base_url=settings.deepseek_base_url
)


def generate_answer_with_context(query: str, context_docs: list) -> str:
    """
    基于检索到的政策文档生成回答

    Args:
        query: 用户问题
        context_docs: 检索到的文档列表，格式: [{"title": "...", "content": "..."}]

    Returns:
        生成的回答
    """
    # 构建上下文
    context_str = "\n\n".join([
        f"【{doc['title']}】\n{doc['content']}"
        for doc in context_docs
    ])

    # 构建提示词
    prompt = f"""你是一个专业的企业员工助手，请根据以下政策文档回答用户的问题。

政策文档内容：
{context_str}

用户问题：{query}

请根据以上政策文档，用友好、专业的语气回答用户的问题。如果政策文档中没有相关信息，请礼貌告知用户。
回答中请注明参考的政策文档标题。"""

    try:
        response = client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": "你是一个专业的企业员工助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM调用失败: {e}")
        # 降级到简单拼接
        context = "\n\n".join([f"【{doc['title']}】\n{doc['content']}" for doc in context_docs])
        return f"根据您的问题「{query}」，我为您找到以下相关政策：\n\n{context}\n\n希望以上信息对您有帮助！"


def generate_resource_answer(query: str, resources: list) -> str:
    """
    生成资源查询回答

    Args:
        query: 用户问题
        resources: 资源列表

    Returns:
        生成的回答
    """
    # 格式化资源列表
    resource_list = []
    for res in resources:
        type_name = {
            "PROJECTOR": "投影仪",
            "LAPTOP": "笔记本电脑",
            "ROOM": "会议室",
            "LICENSE": "软件许可"
        }.get(res.get("type"), res.get("type"))

        name = res.get('name', '')
        desc = res.get('description', '')
        quantity = res.get('quantity')
        available_quantity = res.get('availableQuantity') or res.get('available_quantity')

        if available_quantity is not None and quantity is not None:
            resource_list.append(f"- {type_name}: {name} (可用: {available_quantity}/{quantity}, {desc})")
        else:
            resource_list.append(f"- {type_name}: {name} ({desc})")

    resources_str = "\n".join(resource_list)

    prompt = f"""你是一个专业的企业员工助手，请根据以下资源信息回答用户的问题。

可用资源：
{resources_str}

用户问题：{query}

请用友好、专业的语气总结可用资源信息。"""

    try:
        response = client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": "你是一个专业的企业员工助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM调用失败: {e}")
        return f"根据您的问题「{query}」，以下是可用的资源：\n\n{resources_str}"


def generate_ticket_answer(ticket: dict) -> str:
    """
    生成工单创建回答

    Args:
        ticket: 工单信息

    Returns:
        生成的回答
    """
    ticket_no = ticket.get("ticketNo")
    status = ticket.get("status")
    status_text = {
        "PENDING": "待审批",
        "APPROVED": "已批准",
        "REJECTED": "已拒绝"
    }.get(status, status)

    base_info = f"工单号：{ticket_no}\n当前状态：{status_text}"

    prompt = f"""你是一个专业的企业员工助手，用户的工单已创建成功，请告知用户结果。

工单信息：
{base_info}

请用友好、专业的语气回复用户。"""

    try:
        response = client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": "你是一个专业的企业员工助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM调用失败: {e}")
        answer = f"工单已创建成功！\n\n{base_info}"
        if status == "APPROVED":
            answer += "\n\n恭喜，您的申请已自动批准！"
        elif status == "REJECTED":
            answer += "\n\n抱歉，您的申请未通过审批。"
        else:
            answer += "\n\n请等待审批结果，我们会尽快处理您的申请。"
        return answer
