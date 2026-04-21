# Standalone Deep Agents Service

一个可独立运行的 `FastAPI + LangChain + Deep Agents` Agent 服务原型，目标是把“大模型调用、工具编排、文档 ETL、向量入库、流式接口”整合成一套本地可部署、可继续演进的后端项目。

这个项目当前定位不是通用脚手架，也不是完整生产系统，而是一个偏工程化的 Agent 实验底座：

- 用来验证 `Deep Agents` 作为 Agent 编排核心的可行性
- 保留传统企业应用需要的数据库、缓存、向量库、中间件接入能力
- 为后续接入 RAG、记忆、复杂工具调用和多模型治理留出清晰扩展点

---

## Features

当前已经具备的功能：

- `FastAPI` HTTP 服务入口
- 普通聊天接口 `/api/v1/chat`
- 流式聊天接口 `/api/v1/chat/stream`
- 文档上传接口 `/api/v1/documents/upload`
- 文档列表接口 `/api/v1/documents`
- 内置调试 UI 页面 `/`
- 基于 `Deep Agents` 的 Agent 编排
- 多工具注册与适配为 LangChain `StructuredTool`
- 多模型路由封装，支持 OpenAI-compatible API 接入
- 文档 ETL：原始文件解析、文本分块
- embedding 生成与 Milvus 向量入库
- PostgreSQL 元数据持久化
- 为 memory / store / RAG 闭环预留扩展接口

---

## Tech Stack

### Backend

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic v2
- Loguru

### LLM / Agent

- LangChain
- LangGraph
- Deep Agents
- LangChain OpenAI
- OpenAI-compatible API

### Data / Middleware

- PostgreSQL
- Redis
- Milvus
- MinIO
- etcd
- Attu

### Persistence / ORM

- SQLAlchemy 2.x
- asyncpg

### Infrastructure / Deployment

- Docker
- Docker Compose

---

## What This Project Solves

这个项目主要解决的是“如何把一个 Agent 原型做成带业务边界的后端服务”，而不是只写一个 notebook 或几段 demo 代码。

它覆盖了几个关键工程问题：

- 如何把大模型调用封装成标准 HTTP 服务
- 如何把 Agent 编排和 API 层解耦
- 如何把文档上传、解析、分块、向量入库串成后端流程
- 如何让模型服务、数据库、缓存、向量库一起工作
- 如何为后续的 RAG、记忆、工具扩展、多模型治理留扩展点

---

## Project Structure

```text
agents/
├─ api/                  # HTTP contracts / routes / UI assets
├─ core/                 # Agent orchestration, tools, memory runtime
├─ services/             # Use-case orchestration for chat and documents
├─ infrastructure/       # DB, LLM router, cache, vector DB, tracing
├─ etl/                  # Document parsing and chunking pipeline
├─ rag/                  # Embeddings / retriever / reranker / generator
├─ models/               # Shared domain schemas and enums
├─ memories/             # Seed memory files for Deep Agents
├─ application.py        # FastAPI app factory and lifecycle wiring
├─ main.py               # Uvicorn entrypoint
├─ factory.py            # Dependency wiring for orchestrator
├─ config.py             # Settings
├─ docker-compose.dev-deps.yml
├─ Dockerfile
└─ PROJECT_FLOW.md       # Detailed architecture walkthrough
```

---

## Core Architecture

项目当前采用的是“单体服务 + 分层架构”，不是微服务拆分。

### 1. Application Layer

- [application.py](D:\a_annotation\project-python\agents\application.py)
- [main.py](D:\a_annotation\project-python\agents\main.py)

职责：

- 创建 FastAPI 应用
- 注册所有路由
- 初始化数据库引擎与 session factory
- 应用启动时自动建表

### 2. API Layer

- [api/contracts.py](D:\a_annotation\project-python\agents\api\contracts.py)
- [api/routes/chat.py](D:\a_annotation\project-python\agents\api\routes\chat.py)
- [api/routes/document.py](D:\a_annotation\project-python\agents\api\routes\document.py)
- [api/routes/health.py](D:\a_annotation\project-python\agents\api\routes\health.py)
- [api/routes/ui.py](D:\a_annotation\project-python\agents\api\routes\ui.py)

职责：

- 只处理 HTTP 请求与响应
- 不直接承载复杂业务逻辑
- 把实际工作交给 service 层

### 3. Service Layer

- [services/chat.py](D:\a_annotation\project-python\agents\services\chat.py)
- [services/documents.py](D:\a_annotation\project-python\agents\services\documents.py)

职责：

- 组织一条完整用例流程
- 比如聊天一次、文档上传一次
- 把 API 层和底层 core/infrastructure 解耦

### 4. Core Layer

- [core/agent/orchestrator.py](D:\a_annotation\project-python\agents\core\agent\orchestrator.py)
- [core/tools](D:\a_annotation\project-python\agents\core\tools)
- [core/memory/runtime.py](D:\a_annotation\project-python\agents\core\memory\runtime.py)

职责：

- Deep Agents 编排
- 工具注册与中断策略
- memory 文件和 backend 装配

### 5. Infrastructure / ETL / RAG Layer

- [infrastructure/database](D:\a_annotation\project-python\agents\infrastructure\database)
- [infrastructure/llm](D:\a_annotation\project-python\agents\infrastructure\llm)
- [infrastructure/vectordb](D:\a_annotation\project-python\agents\infrastructure\vectordb)
- [etl](D:\a_annotation\project-python\agents\etl)
- [rag](D:\a_annotation\project-python\agents\rag)

职责：

- 底层数据库访问
- 模型路由
- Milvus 向量写入
- 文档解析与分块
- embedding / retrieval / generation 能力

---

## Current Request Flows

### Chat

`POST /api/v1/chat`

调用链：

1. `api/routes/chat.py`
2. `services/chat.py`
3. `factory.py`
4. `core/agent/orchestrator.py`
5. `Deep Agents + tools + model router`

### Streaming Chat

`POST /api/v1/chat/stream`

调用链：

1. `api/routes/chat.py`
2. `services/chat.py`
3. `orchestrator.stream(...)`
4. Deep Agents streaming events
5. SSE 输出

### Document Upload

`POST /api/v1/documents/upload`

调用链：

1. `api/routes/document.py`
2. `services/documents.py`
3. `etl/pipeline.py`
4. PostgreSQL 文档元数据写入
5. `rag/embeddings.py`
6. `infrastructure/vectordb/milvus_client.py`

---

## API Endpoints

### Health

- `GET /api/v1/health`

### Chat

- `POST /api/v1/chat`
- `POST /api/v1/chat/stream`

示例请求：

```json
{
  "messages": [
    {
      "role": "user",
      "content": "请拆解一个企业知识库问答系统的开发任务"
    }
  ],
  "conversation_id": "demo-thread-1",
  "model": "qwen3-32b"
}
```

### Documents

- `POST /api/v1/documents/upload`
- `GET /api/v1/documents`

---

## Local Development

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Start infrastructure dependencies

```bash
docker compose -f docker-compose.dev-deps.yml up -d
```

默认会启动：

- PostgreSQL
- Redis
- etcd
- MinIO
- Milvus
- Attu

### 3. Configure environment

项目使用 `.env` 配置，至少需要确认这些字段：

- `OPENAI_API_KEY`
- `OPENAI_API_BASE`
- `OPENAI_MODEL`
- `DATABASE_URL`
- `REDIS_URL`
- `MILVUS_HOST`
- `MILVUS_PORT`

### 4. Run the backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### 5. Visit

- Home UI: [http://127.0.0.1:8001/](http://127.0.0.1:8001/)
- Swagger: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)
- Health: [http://127.0.0.1:8001/api/v1/health](http://127.0.0.1:8001/api/v1/health)

---

## Docker Deployment

当前项目已经提供业务服务镜像构建文件：

```bash
docker build -t standalone-deep-agents .
docker run --rm -p 8001:8001 --env-file .env standalone-deep-agents
```

如果你希望完全容器化运行，需要注意：

- 当前 `docker-compose.dev-deps.yml` 主要负责中间件依赖
- 业务服务默认仍按“本机 Python + Docker 中间件”的模式运行
- 若要全容器部署，可继续补一层 app service 到 compose 中

---

## Built-in Tools

当前默认内置工具包括：

- `calculator`
- `web_search`
- `database_query`

这些工具会被注册到 `ToolRegistry`，再适配成 LangChain `StructuredTool` 提供给 Deep Agents。

---

## Current Status

### Implemented

- 独立可运行的 FastAPI 服务
- Deep Agents 主编排
- 普通聊天与流式聊天
- 文档上传与文档列表
- ETL：解析与分块
- 文档 chunk 的 PostgreSQL 存储
- embedding 生成
- Milvus 向量写入
- 基础模型路由能力
- 基础工具系统
- 调试 UI

### Partially Implemented

- Redis 缓存模块代码已存在，但未正式接入主链路
- Memory backend 接口已留好，但持久化 store 还未真正接入
- RAG 模块代码已存在，但尚未接入 `/api/v1/chat` 主流程
- 多模型治理具备基础封装，但当前默认配置仍偏单模型使用

### Not Fully Landed Yet

- 聊天主链路中的正式 RAG 闭环
- 检索 + 重排 + 生成一体化回答链路
- 记忆系统的真实持久化
- 异步任务队列 / 后台任务
- 更完整的 tracing / metrics / monitoring
- 更正式的鉴权与多用户会话隔离

---

## TODO

1. 把 RAG 正式接入 `/api/v1/chat`
   当前文档已经能完成 ETL 和向量入库，但聊天侧还没有消费知识库。

2. 把 Redis 接入缓存链路
   包括普通缓存、语义缓存、工具结果缓存或会话态缓存。

3. 优化 orchestrator/provider 生命周期
   当前每次请求动态创建 orchestrator，后续可以演进为更清晰的 provider / DI 模式。

4. 强化文档链路的事务与失败恢复
   包括批量上传、补跑 embedding、失败重试等能力。

5. 增加真正的生产化能力
   比如鉴权、日志聚合、监控指标、容器化 app service、配置分层等。
