# arch-flow

Animated architecture diagrams as GIFs, generated from JSON descriptions. Built on [Manim](https://www.manim.community/) — the engine behind 3Blue1Brown.

## What It Does

Turn this:

```
"a RAG pipeline with PDF documents, a chunker, embedding model, vector database, and LLM"
```

Into a smooth animated GIF with nodes appearing, connections drawing, and data dots flowing through the architecture.

## Features

- **4 layout templates** — linear flow, DAG, staged pipeline, hub-and-spoke
- **8 node types** — documents, processes, databases, cloud services, APIs, users, queues
- **Dark theme** — professional tech aesthetic with customizable colors
- **Data flow animation** — colored dots travel along edges to show data movement
- **Zero API keys** — fully local rendering with Manim + ffmpeg
- **Claude Code Skill** — integrates as a skill for natural language → GIF pipeline

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

Or use the setup script (checks system deps too):

```bash
python3 scripts/env_setup.py
```

### 2. Create a JSON description

```json
{
  "title": "RAG Pipeline",
  "template": "basic_flow",
  "nodes": [
    {"id": "pdf", "label": "PDF Docs", "type": "document"},
    {"id": "chunker", "label": "Chunker", "type": "process"},
    {"id": "vectordb", "label": "Vector DB", "type": "database"},
    {"id": "llm", "label": "LLM", "type": "cloud"}
  ],
  "edges": [
    {"from": "pdf", "to": "chunker"},
    {"from": "chunker", "to": "vectordb"},
    {"from": "vectordb", "to": "llm"}
  ]
}
```

### 3. Render

```bash
python3 scripts/generate.py --input scene.json --output rag_flow.gif
```

Or inline:

```bash
python3 scripts/generate.py --json '{"title":"RAG","nodes":[{"id":"a","label":"A","type":"process"},{"id":"b","label":"B","type":"database"}],"edges":[{"from":"a","to":"b"}]}'
```

## Templates

| Template | Layout | Best For |
|----------|--------|----------|
| `basic_flow` | Linear left→right | Sequential processes, request flows |
| `dag_flow` | Topological layers | Microservice architectures, data lineage |
| `pipeline_flow` | Staged groups | ETL pipelines, ML workflows |
| `hub_spoke` | Central hub + ring | API gateways, event-driven systems |

## Node Types

| Type | Shape | Use For |
|------|-------|---------|
| `document` | Rectangle | Files, PDFs, data sources |
| `process` | Rounded rectangle | Processing steps, transformers |
| `database` | Styled rectangle | Databases, caches, stores |
| `cloud` | Ellipse | Cloud services, external APIs |
| `api` | Compact rounded rect | API endpoints, gateways |
| `user` | Circle | Users, clients |
| `queue` | Styled rectangle | Message queues, buffers |

## Customization

```json
{
  "style": {
    "bg_color": "#1a1a2e",
    "node_color": "#0f3460",
    "edge_color": "#e94560",
    "text_color": "#ffffff",
    "flow_dot_color": "#f5c518",
    "node_width": 2.0,
    "node_height": 1.2,
    "font_size": 24
  }
}
```

## As a Claude Code Skill

Install as a skill in Claude Code to generate diagrams from natural language:

```bash
# Link the skill to your project
cp -r arch-flow ~/.claude/skills/
```

Then just ask Claude: "Draw an animated RAG architecture diagram"

## Requirements

- Python 3.10+
- [Manim Community Edition](https://www.manim.community/) >= 0.18.0
- ffmpeg (for video/GIF encoding)
- Cairo (for vector rendering)

## Project Structure

```
arch-flow/
├── SKILL.md              # Claude Code skill definition
├── scripts/
│   ├── generate.py       # Main entry point
│   ├── parser.py         # JSON → scene config
│   ├── renderer.py       # Scene config → Manim → GIF
│   ├── env_setup.py      # Dependency checker/installer
│   └── templates/
│       ├── basic_flow.py
│       ├── dag_flow.py
│       ├── pipeline_flow.py
│       └── hub_spoke.py
└── references/
    ├── scene_types.md    # Template descriptions
    ├── node_styles.md    # Visual style catalog
    └── animation_presets.md
```

## License

MIT
