# LLM 成本追踪网关 — 设计文档

## 概述

为 Agent 服务增加一个轻量级网关层，通过 LangChain callback 拦截所有 LLM 调用，记录 token 消耗、延迟、成本等指标到 MySQL，并提供独立的可视化 Dashboard。

## 架构

```
Agent Graph (nodes.py)
    │  ChatOpenAI(callbacks=[LLMTrackingCallback])
    ▼
LLMTrackingCallback (BaseCallbackHandler)
    │  提取 token / 延迟 / 成本
    ▼
MySQL: llm_call_logs ←── FastAPI /admin routes ──→ Dashboard (Vue3 + Chart.js)
                                                      ↑
DashScope SDK (embedding/rerank)                      │
    │  手动埋点（1 行/调用点）──────────────────────→ │
```

## Callback 层

### Chat 模型（ChatOpenAI）

- 新增 `src/tracking/callback.py`，实现 `BaseCallbackHandler`
- `on_llm_start`: 记开始时间、model name
- `on_llm_end`: 从 `response.llm_output` 提取 token_usage，计算延迟和成本，写入 DB
- `on_llm_error`: 记录失败调用（status=error）
- `get_llm()` 改造：创建 ChatOpenAI 时挂载 `callbacks=[tracking_callback]`

### 上下文传递

用 `contextvars.ContextVar`（异步安全，支持 LangGraph 的 async 节点）：

```python
_tracking_ctx: ContextVar = ContextVar('tracking', default=None)

def set_tracking_context(user_id: str, session_id: str, node_type: str):
    _tracking_ctx.set({"user_id": user_id, "session_id": session_id, "node_type": node_type})
```

- chat.py: 在 `agent_graph.astream_events()` 前 set
- chat.py `compress_memory_async`: 在 `llm.invoke()` 前 set（后台线程需手动传）
- 其他调用点同样处理

### Embedding/Rerank 模型（DashScope SDK）

不走 LangChain callback，在 DashScope SDK 调用点手动记录：

- `tools.py` 中 `TextReRank.call()` 2 处
- `init_vector_store.py` 中 `TextEmbedding.call()` 1 处
- `gray_updater.py` 中 embedding 调用 1 处

每处加 1 行：`track_embedding(model, usage, user_id, session_id, node_type)`

## 数据模型

### `llm_call_logs` 表

```sql
CREATE TABLE llm_call_logs (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id       VARCHAR(64)     NOT NULL,
    session_id    VARCHAR(128)    NOT NULL,
    model_name    VARCHAR(64)     NOT NULL,
    model_type    ENUM('chat','embedding','rerank') NOT NULL,
    node_type     ENUM('agent','compress','eval','index') NOT NULL,
    input_tokens  INT UNSIGNED DEFAULT 0,
    output_tokens INT UNSIGNED DEFAULT 0,
    latency_ms    INT UNSIGNED DEFAULT 0,
    cost          DECIMAL(10,6) DEFAULT 0.000000,
    status        ENUM('success','error') DEFAULT 'success',
    error_msg     VARCHAR(256) DEFAULT NULL,
    created_at    DATETIME(3) DEFAULT CURRENT_TIMESTAMP(3),

    INDEX idx_user_date  (user_id, created_at),
    INDEX idx_session    (session_id),
    INDEX idx_model_type (model_type, created_at)
);
```

### 模型定价配置

`src/tracking/pricing.json`：

```json
{
  "hy3-preview":        {"input": 0.004, "output": 0.012, "unit": "per_1k_tokens"},
  "text-embedding-v2":  {"input": 0.0005, "output": 0.0,   "unit": "per_1k_tokens"},
  "qwen3-vl-rerank":    {"input": 0.003, "output": 0.0,   "unit": "per_1k_tokens"}
}
```

`cost = (input_tokens * input_price + output_tokens * output_price) / 1000`

## Admin API

路由前缀：`/admin`，鉴权 header：`X-Admin-Token`

### 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/admin/stats/trend` | 每日趋势数据（折线图用） |
| GET | `/admin/stats/trend-hourly` | 小时趋势数据（24h） |
| GET | `/admin/stats/overview` | 时段总览（活跃用户/会话/总调用/总成本） |
| GET | `/admin/stats/aggregation` | 时段聚合（每用户平均 / 每会话平均） |
| GET | `/admin/pricing` | 模型定价配置 |

### 请求参数

```
/admin/stats/trend?from=2026-04-01&to=2026-04-28
/admin/stats/trend-hourly            （无参数，默认最近24h）
/admin/stats/overview?from=...&to=...
/admin/stats/aggregation?from=...&to=...
```

### 趋势响应结构

```json
{
  "days": [
    {
      "date": "2026-04-21",
      "models": {
        "chat":    {"calls": 120, "input_tokens": 80000, "output_tokens": 24000, "cost": 0.768},
        "embedding": {"calls": 40, "input_tokens": 20000, "output_tokens": 0, "cost": 0.01},
        "rerank":  {"calls": 30, "input_tokens": 15000, "output_tokens": 0, "cost": 0.045}
      },
      "active_users": 12,
      "active_sessions": 35
    }
  ]
}
```

小时趋势同理，`date` 变为 `hour`（如 `"2026-04-28 14:00"`）。

### 聚合响应结构

```json
{
  "per_user": {
    "avg_input_tokens": 23300.0,
    "avg_output_tokens": 7200.0,
    "avg_calls": 36.3,
    "avg_cost": 0.31
  },
  "per_session": {
    "avg_input_tokens": 6300.0,
    "avg_output_tokens": 1900.0,
    "avg_calls": 9.8,
    "avg_cost": 0.083
  }
}
```

## 前端 Dashboard

- 文件：`src/static/admin.html`
- 通过 FastAPI `StaticFiles` 挂载：`app.mount("/admin", StaticFiles(directory="src/static", html=True))`
- 技术栈：Vue 3 CDN + Chart.js CDN + 纯 CSS

### 布局

顶部 tab 切换「日维度」/「小时维度」：

**日维度（默认）：**
- 时间范围选择器（date from → date to）
- 4 个概览卡片（活跃用户、活跃会话、总调用、总成本）
- 3 个占满宽度的折线图：
  1. 每日成本趋势（按模型 model_type 堆叠/分组线）
  2. 每日 Token 趋势（输入 vs 输出两条线）
  3. 每日调用次数（按模型堆叠）
- 右侧信息面板：模型成本占比（饼图）+ 时段内每用户/每会话平均

**小时维度（过去 24h）：**
- 无日期选择，标注"最近 24 小时"
- 4 个概览卡片（同维度逻辑，但只计 24h）
- 2 个折线图（X 轴为整点小时）：
  1. 每小时 Token 趋势（输入/输出）
  2. 每小时调用次数（按模型）
- 右侧信息面板：同上

### 交互

- 自动刷新：下拉 15s / 30s / 60s / 关闭，默认 30s
- 时间范围变更 → 所有图表联动刷新

## 文件清单

| 文件 | 类型 | 说明 |
|------|------|------|
| `src/tracking/__init__.py` | 新建 | 模块入口 |
| `src/tracking/callback.py` | 新建 | BaseCallbackHandler + contextvar |
| `src/tracking/recorder.py` | 新建 | DB 写入 + manual track 函数 |
| `src/tracking/pricing.json` | 新建 | 模型定价配置 |
| `src/api/admin.py` | 新建 | Admin API 路由 |
| `src/static/admin.html` | 新建 | Dashboard 前端 |
| `src/agent/nodes.py` | 修改 | `get_llm()` 挂载 callback |
| `src/api/chat.py` | 修改 | 每次调用前 set context |
| `src/agent/tools.py` | 修改 | embedding/rerank 调用点加记录 |
| `src/rag/init_vector_store.py` | 修改 | embedding 调用点加记录 |
| `src/rag/gray_updater.py` | 修改 | embedding 调用点加记录 |
| `src/main.py` | 修改 | 挂载 admin 路由 + static files |

## 验证

1. 启动服务后访问 `/admin/` 能看到 Dashboard 页面
2. 发一条对话 → Dashboard 上出现新的调用记录
3. 日维度折线图数据随日期变化
4. 小时维度显示过去 24h 的小时曲线
5. 自动刷新正常更新数据
6. 模型占比饼图正确反映各模型成本比例
