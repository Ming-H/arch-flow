# Scene Types

Arch-flow provides four scene templates, each designed for a different category of architecture diagram. Choose the template that best matches the logical structure of your system.

---

## 1. basic_flow

### Description

A simple linear left-to-right flow. Nodes are arranged horizontally in a single row, connected by arrows that point from left to right. This is the most straightforward layout and works well whenever your architecture can be described as a single sequence of steps.

### Best Use Cases

- API request/response flow (Client -> Gateway -> Service -> Database)
- CI/CD pipeline (Commit -> Build -> Test -> Deploy)
- Data processing chain (Ingest -> Validate -> Transform -> Load)
- Simple request lifecycle (Request -> Auth -> Handler -> Response)

### Required JSON Structure

```json
{
  "scene_type": "basic_flow",
  "nodes": [
    { "id": "client", "label": "Client", "type": "user" },
    { "id": "server", "label": "Server", "type": "process" },
    { "id": "db", "label": "Database", "type": "database" }
  ],
  "edges": [
    { "from": "client", "to": "server" },
    { "from": "server", "to": "db" }
  ]
}
```

### Supported Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `direction` | string | `"left_to_right"` | Flow direction. Accepted values: `"left_to_right"`, `"right_to_left"`, `"top_to_bottom"`, `"bottom_to_top"` |
| `spacing` | float | `3.0` | Horizontal distance between node centers (in Manim units) |
| `edge_labels` | bool | `false` | Show labels on edges (requires `label` field on edge objects) |

### Layout Behavior

- Nodes are placed in the order they appear in the `nodes` array.
- All nodes share the same vertical center line.
- Arrows are drawn between consecutive nodes as defined by the `edges` array.
- The camera automatically frames all nodes with padding.
- If more than 7 nodes are provided, the layout wraps to a second row automatically.

---

## 2. dag_flow

### Description

A directed acyclic graph with branching and merging. Nodes are arranged in topological layers (columns), where each layer represents a generation of processing. Edges can branch from one node to many and merge from many nodes into one. This template is the best choice when your architecture has fan-out, fan-in, or complex interdependencies.

### Best Use Cases

- Microservice architecture with multiple service dependencies
- Data lineage diagram showing how datasets derive from each other
- Dependency graph for packages or build targets
- Event-driven architecture with pub/sub fan-out

### Required JSON Structure

```json
{
  "scene_type": "dag_flow",
  "nodes": [
    { "id": "api_gw", "label": "API Gateway", "type": "api" },
    { "id": "svc_a", "label": "Service A", "type": "process" },
    { "id": "svc_b", "label": "Service B", "type": "process" },
    { "id": "cache", "label": "Redis Cache", "type": "database" },
    { "id": "db", "label": "PostgreSQL", "type": "database" }
  ],
  "edges": [
    { "from": "api_gw", "to": "svc_a" },
    { "from": "api_gw", "to": "svc_b" },
    { "from": "svc_a", "to": "cache" },
    { "from": "svc_b", "to": "db" },
    { "from": "svc_a", "to": "db" }
  ]
}
```

### Supported Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `layer_spacing` | float | `3.5` | Horizontal distance between topological layers |
| `node_spacing` | float | `2.0` | Vertical distance between nodes in the same layer |
| `rank_direction` | string | `"LR"` | Layout direction: `"LR"` (left-to-right) or `"TB"` (top-to-bottom) |
| `edge_labels` | bool | `false` | Show labels on edges |
| `curved_edges` | bool | `true` | Draw curved arrows instead of straight lines to avoid overlap |

### Layout Behavior

- A topological sort determines which layer each node belongs to.
- Nodes with no incoming edges are placed in layer 0; all others are placed based on longest path from a root.
- Within each layer, nodes are distributed evenly along the vertical axis.
- Curved edges (ArcBetweenPoints) are used by default so that multiple edges between the same two layers do not overlap.
- The layout algorithm detects cycles and raises an error (use `basic_flow` or `pipeline_flow` if cyclic feedback is needed).

---

## 3. pipeline_flow

### Description

A staged pipeline with grouped nodes. Nodes are organized into named stages, and each stage is visually enclosed by a labeled background rectangle. This template is ideal when your architecture is naturally divided into sequential phases, and you want to make those phases explicit in the diagram.

### Best Use Cases

- ML training pipeline (Ingest -> Feature Engineering -> Training -> Evaluation -> Serving)
- Data ETL flow (Extract -> Transform -> Validate -> Load)
- CI/CD stages (Build -> Test -> Staging -> Production)
- Multi-tenant onboarding flow (Signup -> Verification -> Provisioning -> Activation)

### Required JSON Structure

```json
{
  "scene_type": "pipeline_flow",
  "stages": [
    {
      "name": "Extract",
      "nodes": [
        { "id": "s3", "label": "S3 Bucket", "type": "cloud" },
        { "id": "api_src", "label": "REST API", "type": "api" }
      ]
    },
    {
      "name": "Transform",
      "nodes": [
        { "id": "spark", "label": "Spark Job", "type": "process" }
      ]
    },
    {
      "name": "Load",
      "nodes": [
        { "id": "dw", "label": "Data Warehouse", "type": "database" }
      ]
    }
  ],
  "edges": [
    { "from": "s3", "to": "spark" },
    { "from": "api_src", "to": "spark" },
    { "from": "spark", "to": "dw" }
  ]
}
```

### Supported Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `stage_spacing` | float | `4.0` | Horizontal distance between stage background rectangles |
| `stage_bg_opacity` | float | `0.15` | Opacity of the stage background fill |
| `stage_bg_color` | string | `"#16213e"` | Fill color for stage background rectangles |
| `stage_border_color` | string | `"#e94560"` | Border color for stage background rectangles |
| `show_stage_labels` | bool | `true` | Display stage name above each background rectangle |
| `stage_label_font_size` | int | `28` | Font size for stage name labels |

### Layout Behavior

- Stages are laid out left to right in the order they appear in the `stages` array.
- Within each stage, nodes are stacked vertically, centered within the stage background.
- The background rectangle automatically sizes to fit all nodes in the stage with padding.
- Edges can cross stage boundaries (from a node in one stage to a node in another).
- If no edges are specified, implicit edges are created between the last node of each stage and the first node of the next stage.

---

## 4. hub_spoke

### Description

A central hub connected to surrounding satellite nodes. One node is designated as the hub and placed at the center. All other nodes are arranged in a circle around it, with edges radiating from the hub to each satellite (or optionally, bidirectional edges). This template works best for architectures with a clear central component.

### Best Use Cases

- API gateway architecture (gateway in the center, microservices around it)
- Event-driven system (message broker at center, producers/consumers around)
- Star topology network (switch/router at center, endpoints around)
- Client-server model with a single server and multiple clients

### Required JSON Structure

```json
{
  "scene_type": "hub_spoke",
  "hub": { "id": "gateway", "label": "API Gateway", "type": "api" },
  "spokes": [
    { "id": "user_svc", "label": "User Service", "type": "process" },
    { "id": "order_svc", "label": "Order Service", "type": "process" },
    { "id": "notify_svc", "label": "Notification", "type": "process" },
    { "id": "db", "label": "Database", "type": "database" },
    { "id": "cache", "label": "Cache", "type": "database" }
  ],
  "edges": [
    { "from": "gateway", "to": "user_svc" },
    { "from": "gateway", "to": "order_svc" },
    { "from": "gateway", "to": "notify_svc" },
    { "from": "gateway", "to": "db" },
    { "from": "gateway", "to": "cache" }
  ]
}
```

### Supported Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `radius` | float | `3.5` | Distance from hub center to each spoke node |
| `hub_scale` | float | `1.5` | Scale multiplier for the hub node (makes it visually larger) |
| `bidirectional` | bool | `false` | Draw double-headed arrows instead of one-directional |
| `start_angle` | float | `0.0` | Angle (in radians) for the first spoke; useful for rotating the layout |
| `edge_labels` | bool | `false` | Show labels on edges |
| `spoke_spacing` | string | `"even"` | How to distribute spokes: `"even"` (equal angles) or `"auto"` (pack based on label width) |

### Layout Behavior

- The hub node is placed at the center of the scene.
- Spoke nodes are distributed evenly around the hub at the specified radius.
- Edges are drawn from the hub to each spoke by default. If `bidirectional` is true, arrows point both ways.
- The hub node is rendered larger than spokes by the `hub_scale` factor.
- The animation emphasizes the hub first (it appears first and may use the pulse effect), then reveals spokes in sequence.
- If no `edges` array is provided, edges are automatically created from the hub to every spoke.

---

## Choosing the Right Template

| Question | Template |
|----------|----------|
| Is it a single linear sequence? | `basic_flow` |
| Do nodes branch out or merge back? | `dag_flow` |
| Are there clearly named stages or phases? | `pipeline_flow` |
| Is there one central component everything connects to? | `hub_spoke` |
| Does it have stages with branching inside? | `pipeline_flow` |
| Is it a mesh with no clear center or sequence? | `dag_flow` |
