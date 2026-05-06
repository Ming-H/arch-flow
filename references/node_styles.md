# Node Styles

Arch-flow provides several node types, each rendered as a distinct shape and color to visually communicate the role of each component in the architecture.

---

## Built-in Node Types

| Type | Shape | Color Hint | Best For |
|------|-------|-----------|----------|
| `document` | Rectangle | Amber / Paper | Files, PDFs, data sources, configuration files |
| `process` | RoundedRectangle | Blue | Processing steps, transformers, compute services |
| `database` | Rectangle with cylinder lines | Teal / Green | Databases, caches, key-value stores |
| `cloud` | Ellipse | Purple | Cloud services, external APIs, third-party integrations |
| `api` | RoundedRectangle (compact) | Orange | API endpoints, gateways, routers |
| `user` | Circle | Pink | User/client representations, external actors |
| `queue` | Rectangle with zigzag border | Yellow | Message queues, buffers, event buses |
| `default` | RoundedRectangle | Blue | Generic components, fallback for unknown types |

---

## Type Details

### document

- **Shape**: Standard rectangle with sharp corners.
- **Color**: Amber fill (`#f5c518` tint) with darker amber border.
- **Rendering**: A small folded-corner decoration is drawn in the top-right to evoke a document icon.
- **Use when**: The node represents a file, a report, a log, or any static data source.

```json
{ "id": "invoice", "label": "Invoice PDF", "type": "document" }
```

### process

- **Shape**: RoundedRectangle with moderate corner radius.
- **Color**: Blue fill (`#0f3460` tint) with lighter blue border.
- **Rendering**: Clean rounded rectangle, the most common node type.
- **Use when**: The node is a processing step, a service, a transformer, or any compute component.

```json
{ "id": "etl", "label": "ETL Pipeline", "type": "process" }
```

### database

- **Shape**: Rectangle with two horizontal cylinder lines near the top to suggest a cylinder/drum.
- **Color**: Teal fill (`#16697a` tint) with green border.
- **Rendering**: The cylinder lines are drawn as elliptical arcs to create a 3D database icon feel.
- **Use when**: The node is a relational database, NoSQL store, cache (Redis, Memcached), or data warehouse.

```json
{ "id": "postgres", "label": "PostgreSQL", "type": "database" }
```

### cloud

- **Shape**: Ellipse (wide oval).
- **Color**: Purple fill (`#533483` tint) with lighter purple border.
- **Rendering**: A soft oval shape that visually suggests an external or cloud-hosted service.
- **Use when**: The node is an AWS/GCP/Azure service, an external SaaS API, or any off-premise resource.

```json
{ "id": "s3", "label": "AWS S3", "type": "cloud" }
```

### api

- **Shape**: RoundedRectangle with compact dimensions (smaller than `process`).
- **Color**: Orange fill (`#e94560` tint) with darker orange border.
- **Rendering**: A smaller, punchier rounded rectangle designed to look like an endpoint or gateway.
- **Use when**: The node is an API endpoint, a gateway, a proxy, or a router.

```json
{ "id": "gateway", "label": "API Gateway", "type": "api" }
```

### user

- **Shape**: Circle.
- **Color**: Pink fill (`#e8a0bf` tint) with darker pink border.
- **Rendering**: A simple circle that represents an external actor or human user.
- **Use when**: The node represents a user, a client application, or an external system that initiates requests.

```json
{ "id": "client", "label": "End User", "type": "user" }
```

### queue

- **Shape**: Rectangle with a zigzag (sawtooth) pattern on the top and bottom borders.
- **Color**: Yellow fill (`#f5c518` tint) with darker yellow border.
- **Rendering**: The zigzag border visually suggests a buffer or holding area, similar to a queue icon.
- **Use when**: The node is a message queue (RabbitMQ, Kafka), a task queue, or a buffer.

```json
{ "id": "kafka", "label": "Kafka Topic", "type": "queue" }
```

### default

- **Shape**: RoundedRectangle (same as `process`).
- **Color**: Blue fill (same as `process`).
- **Rendering**: Identical to `process`. Used as a fallback when no `type` field is specified or the type is not recognized.
- **Use when**: The component does not fit any other category, or you want to keep the diagram generic.

```json
{ "id": "component", "label": "Service", "type": "default" }
```

---

## Style Configuration

Global style settings control the visual appearance of all nodes, edges, and the scene background. Override these values in the `style` object at the top level of your JSON definition.

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

### Field Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `bg_color` | string (hex) | `#1a1a2e` | Scene background color. Applied to the full canvas. Use a dark color for high contrast. |
| `node_color` | string (hex) | `#0f3460` | Default fill color for nodes. Individual node types may override this with their own color hint, but this serves as the base. |
| `edge_color` | string (hex) | `#e94560` | Color of the arrows/lines connecting nodes. |
| `text_color` | string (hex) | `#ffffff` | Color of all text labels on nodes and edges. |
| `flow_dot_color` | string (hex) | `#f5c518` | Color of the animated dot that travels along edges during the `data_flow_dot` animation. |
| `node_width` | float | `2.0` | Default width of each node in Manim units. Some node types (e.g., `api`) render smaller by applying a scale factor. |
| `node_height` | float | `1.2` | Default height of each node in Manim units. |
| `font_size` | int | `24` | Font size for node labels. Edge labels use a slightly smaller size (font_size - 4). |

### Per-Node Style Overrides

Individual nodes can override the global style by including a `style` field:

```json
{
  "id": "highlight_node",
  "label": "Important Service",
  "type": "process",
  "style": {
    "node_color": "#e94560",
    "text_color": "#ffffff"
  }
}
```

Per-node style fields follow the same naming convention as the global style. Only the fields you specify are overridden; all others fall back to the global defaults.

---

## Color Palette Reference

The default palette is designed for dark backgrounds with high contrast. Below are the hex values used across node types:

| Role | Hex |
|------|-----|
| Background | `#1a1a2e` |
| Node base (process, default) | `#0f3460` |
| Edge / accent | `#e94560` |
| Flow dot | `#f5c518` |
| Text | `#ffffff` |
| Document amber | `#d4a030` |
| Database teal | `#16697a` |
| Cloud purple | `#533483` |
| API orange | `#e94560` |
| User pink | `#e8a0bf` |
| Queue yellow | `#c9a818` |
