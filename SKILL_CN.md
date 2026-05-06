**[English](./SKILL.md)** | 中文

---
name: arch-flow
description: >
  根据自然语言描述生成架构动画 GIF。使用 Manim (Python) 渲染高质量技术动画，
  支持数据流动效果、节点动画和暗色主题。4 种模板：basic_flow（线性流程）、
  dag_flow（有向无环图）、pipeline_flow（分阶段流程）、hub_spoke（中心辐射）。
  触发词：架构图, 流程动图, 架构动画, 动画图, 系统架构图, 技术流程图。
---

# arch-flow — 架构流程动画生成器

根据自然语言或结构化 JSON 描述，自动生成精美的架构动画 GIF。

## 工作原理

**三阶段管线**：自然语言 → 结构化 JSON → Manim 脚本 → GIF

1. 用自然语言描述架构
2. Claude 将其转换为结构化 JSON（节点 + 连线）
3. 脚本在本地渲染平滑动画 GIF

## 可用模板

| 模板 | 布局 | 适用场景 |
|------|------|----------|
| `basic_flow` | 线性从左到右 | 顺序流程、简单管线 |
| `dag_flow` | 拓扑分层 | 微服务依赖、数据血缘 |
| `pipeline_flow` | 分阶段分组 | ETL、ML 工作流 |
| `hub_spoke` | 中心 + 环形 | API 网关、客户端-服务器 |

## 使用方法

### 第一步：生成 JSON

用户描述架构后，生成如下 JSON：

```json
{
  "title": "RAG 流程",
  "template": "pipeline_flow",
  "nodes": [
    {"id": "pdf", "label": "PDF 文档", "type": "document"},
    {"id": "chunker", "label": "分块器", "type": "process"},
    {"id": "embeddings", "label": "嵌入模型", "type": "process"},
    {"id": "vectordb", "label": "向量库", "type": "database"},
    {"id": "llm", "label": "大语言模型", "type": "cloud"}
  ],
  "edges": [
    {"from": "pdf", "to": "chunker"},
    {"from": "chunker", "to": "embeddings"},
    {"from": "embeddings", "to": "vectordb"},
    {"from": "vectordb", "to": "llm"}
  ]
}
```

### 第二步：渲染

```bash
python3 /path/to/arch-flow/scripts/generate.py --input scene.json --output output.gif
```

或内联方式：
```bash
python3 /path/to/arch-flow/scripts/generate.py --json '{"title":"RAG","nodes":[...],"edges":[...]}'
```

## 节点类型

| 类型 | 视觉样式 | 用途 |
|------|----------|------|
| `document` | 矩形 | 文件、PDF、数据源 |
| `process` | 圆角矩形 | 处理步骤、转换器 |
| `database` | 矩形（带样式） | 数据库、缓存、存储 |
| `cloud` | 椭圆 | 云服务、外部 API |
| `api` | 紧凑圆角矩形 | API 端点、网关 |
| `user` | 圆形 | 用户、客户端 |
| `queue` | 矩形（带样式） | 消息队列 |
| `default` | 圆角矩形 | 通用组件 |

## 样式自定义

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

## Claude 工作流

1. 阅读用户的架构描述
2. 查看 `references/scene_types.md` 选择最佳模板
3. 查看 `references/node_styles.md` 选择节点类型
4. 生成 JSON 配置
5. 将 JSON 写入临时文件
6. 通过 Bash 运行 `generate.py`
7. 将输出路径报告给用户

## 环境要求

- Python 3.10+
- Manim Community Edition (`pip install manim`)
- ffmpeg（用于渲染）
- 运行 `python3 scripts/env_setup.py` 检查/安装所有依赖

## 许可证

MIT
