---
name: arch-flow
description: >
  Generate animated architecture diagrams as GIFs from natural language descriptions.
  Uses Manim (Python) for high-quality tech animations with flowing data dots,
  node animations, and dark theme styling. Supports 4 templates: basic_flow (linear),
  dag_flow (directed acyclic graph), pipeline_flow (staged), hub_spoke (central hub).
  Triggers on: architecture diagram, flow diagram, animated diagram, arch diagram,
  架构图, 流程动图, 架构动画, animated architecture, tech diagram, system diagram.
---

# arch-flow — Architecture Flow Animator

Generate animated architecture diagrams as GIFs from natural language or structured JSON.

## How It Works

**Three-phase pipeline**: Natural Language → Structured JSON → Manim Script → GIF

1. You describe an architecture in natural language
2. Claude converts it to structured JSON (nodes + edges)
3. The scripts render a smooth animation GIF locally

## Available Templates

| Template | Layout | Best For |
|----------|--------|----------|
| `basic_flow` | Linear left→right | Sequential processes, simple pipelines |
| `dag_flow` | Topological layers | Microservice deps, data lineage |
| `pipeline_flow` | Staged groups | ETL, ML workflows, multi-stage |
| `hub_spoke` | Central + circle | API gateways, client-server |

## Usage

### Step 1: Generate JSON

When the user describes an architecture, produce a JSON like:

```json
{
  "title": "RAG Pipeline",
  "template": "pipeline_flow",
  "nodes": [
    {"id": "pdf", "label": "PDF Docs", "type": "document"},
    {"id": "chunker", "label": "Chunker", "type": "process"},
    {"id": "embeddings", "label": "Embedding Model", "type": "process"},
    {"id": "vectordb", "label": "Vector DB", "type": "database"},
    {"id": "llm", "label": "LLM", "type": "cloud"}
  ],
  "edges": [
    {"from": "pdf", "to": "chunker"},
    {"from": "chunker", "to": "embeddings"},
    {"from": "embeddings", "to": "vectordb"},
    {"from": "vectordb", "to": "llm"}
  ]
}
```

### Step 2: Render

```bash
python3 /path/to/arch-flow/scripts/generate.py --input scene.json --output output.gif
```

Or inline:
```bash
python3 /path/to/arch-flow/scripts/generate.py --json '{"title":"RAG","nodes":[...],"edges":[...]}'
```

## Node Types

| Type | Visual | Use For |
|------|--------|---------|
| `document` | Rectangle | Files, PDFs, data sources |
| `process` | Rounded rect | Processing steps |
| `database` | Rectangle (styled) | DBs, caches, stores |
| `cloud` | Ellipse | Cloud services, external APIs |
| `api` | Compact rounded rect | API endpoints |
| `user` | Circle | Users, clients |
| `queue` | Rectangle (styled) | Message queues |
| `default` | Rounded rect | Generic components |

## Style Customization

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

## Workflow for Claude

1. Read the user's architecture description
2. Check `references/scene_types.md` to pick the best template
3. Check `references/node_styles.md` for node type choices
4. Generate the JSON configuration
5. Write JSON to a temp file
6. Run `generate.py` via Bash
7. Report the output path to the user

## Requirements

- Python 3.10+
- Manim Community Edition (`pip install manim`)
- ffmpeg (for rendering)
- Run `python3 scripts/env_setup.py` to check/install all deps

## License

MIT
