# arch-flow

从 JSON 描述生成架构动画 GIF。基于 [Manim](https://www.manim.community/) —— 3Blue1Brown 使用的动画引擎。

## 功能

把这样的描述：

```
"一个 RAG 流程，包含 PDF 文档、分块器、嵌入模型、向量数据库和大语言模型"
```

变成一个平滑的动画 GIF：节点依次出现、连线绘制、数据流点沿着架构流动。

## 特性

- **4 种布局模板** — 线性流程、有向无环图、分阶段管线、中心辐射
- **8 种节点类型** — 文档、处理、数据库、云服务、API、用户、队列
- **暗色主题** — 专业技术美学，颜色可自定义
- **数据流动画** — 彩色圆点沿连线流动，展示数据传输
- **无需 API 密钥** — 完全本地渲染（Manim + ffmpeg）
- **Claude Code 技能** — 作为 Skill 集成，支持自然语言 → GIF

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

或使用安装脚本（同时检查系统依赖）：

```bash
python3 scripts/env_setup.py
```

### 2. 创建 JSON 描述

```json
{
  "title": "RAG 流程",
  "template": "basic_flow",
  "nodes": [
    {"id": "pdf", "label": "PDF 文档", "type": "document"},
    {"id": "chunker", "label": "分块器", "type": "process"},
    {"id": "vectordb", "label": "向量库", "type": "database"},
    {"id": "llm", "label": "大语言模型", "type": "cloud"}
  ],
  "edges": [
    {"from": "pdf", "to": "chunker"},
    {"from": "chunker", "to": "vectordb"},
    {"from": "vectordb", "to": "llm"}
  ]
}
```

### 3. 渲染

```bash
python3 scripts/generate.py --input scene.json --output rag_flow.gif
```

## 模板

| 模板 | 布局 | 适用场景 |
|------|------|----------|
| `basic_flow` | 线性从左到右 | 顺序流程、请求流 |
| `dag_flow` | 拓扑分层 | 微服务架构、数据血缘 |
| `pipeline_flow` | 分阶段分组 | ETL 管线、ML 工作流 |
| `hub_spoke` | 中心 + 环形 | API 网关、事件驱动系统 |

## 节点类型

| 类型 | 形状 | 用途 |
|------|------|------|
| `document` | 矩形 | 文件、PDF、数据源 |
| `process` | 圆角矩形 | 处理步骤、转换器 |
| `database` | 带样式矩形 | 数据库、缓存、存储 |
| `cloud` | 椭圆 | 云服务、外部 API |
| `api` | 紧凑圆角矩形 | API 端点、网关 |
| `user` | 圆形 | 用户、客户端 |
| `queue` | 带样式矩形 | 消息队列、缓冲区 |

## 自定义样式

```json
{
  "style": {
    "bg_color": "#1a1a2e",
    "node_color": "#0f3460",
    "edge_color": "#e94560",
    "text_color": "#ffffff",
    "flow_dot_color": "#f5c518"
  }
}
```

## 作为 Claude Code 技能使用

```bash
# 将技能链接到项目
cp -r arch-flow ~/.claude/skills/
```

然后直接对 Claude 说："画一个 RAG 架构动画图"

## 环境要求

- Python 3.10+
- [Manim Community Edition](https://www.manim.community/) >= 0.18.0
- ffmpeg（用于视频/GIF 编码）
- Cairo（用于矢量渲染）

## 许可证

MIT
