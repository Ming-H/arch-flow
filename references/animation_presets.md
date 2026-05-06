# Animation Presets

Arch-flow supports a set of animation effects that control how nodes appear and how data flow is visualized. These effects are implemented as Manim animations and can be combined to create polished presentation-ready GIFs.

---

## Individual Effects

### 1. fade_in

**What it looks like**: Nodes start fully transparent and smoothly increase to full opacity over the configured duration. Clean and unobtrusive.

**When to use it**: When you want a professional, subtle reveal. Works well in almost any context. Pairs naturally with `data_flow_dot`.

**Manim method**: `FadeIn(mobject)`

**Configurable parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `duration` | float | `0.5` | Time in seconds for the fade to complete |
| `shift` | vector | `None` | Optional directional shift during fade (e.g., `UP * 0.3` for a slight upward motion) |

---

### 2. draw_border

**What it looks like**: The node border is drawn first as a stroke animation (the outline traces around the shape), then the fill color fades in. Gives a "sketching" or "whiteboard" feel.

**When to use it**: Technical demos, tutorials, or any context where you want to convey the diagram being built up step-by-step.

**Manim method**: `DrawBorderThenFill(mobject)`

**Configurable parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `duration` | float | `0.8` | Total time for border draw + fill |
| `border_width` | float | `2.0` | Stroke width during the border-drawing phase |

---

### 3. grow_from_center

**What it looks like**: Nodes scale up from a single point at their center. Starts at zero size and expands to full size. Energetic and attention-grabbing.

**When to use it**: When you want each node to feel like it is materializing or popping into existence. Good for presentations where you want to keep the audience engaged.

**Manim method**: `GrowFromCenter(mobject)`

**Configurable parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `duration` | float | `0.5` | Time in seconds for the grow animation |
| `point` | vector | center of node | Origin point to grow from (defaults to node center) |

---

### 4. slide_in

**What it looks like**: Nodes glide into position from outside the visible frame. The direction is configurable (left, right, top, bottom).

**When to use it**: When you want to convey directionality or when nodes "arrive" from a specific direction. For example, slide in from the left for a left-to-right flow to reinforce the reading order.

**Manim method**: Custom implementation using `Transform` from an offscreen position to the final position.

**Configurable parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `duration` | float | `0.6` | Time in seconds for the slide |
| `direction` | string | `"left"` | Slide direction: `"left"`, `"right"`, `"top"`, `"bottom"` |
| `distance` | float | `8.0` | How far offscreen the node starts (in Manim units) |

---

### 5. data_flow_dot

**What it looks like**: After nodes are in place, a small colored dot travels along each edge from source to target. The dot follows the exact path of the edge (straight or curved). Multiple dots can animate sequentially or simultaneously.

**When to use it**: Almost always. This is the signature animation that makes arch-flow diagrams feel alive. It visually communicates data movement, requests, or events flowing through the system.

**Manim method**: `MoveAlongPath(dot, path)` with a `Dot` mobject following a `VMobject` path.

**Configurable parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `duration` | float | `0.8` | Time for one dot to travel one edge |
| `color` | string (hex) | `#f5c518` | Color of the flow dot (overridden by `flow_dot_color` in global style) |
| `radius` | float | `0.08` | Radius of the dot in Manim units |
| `sequential` | bool | `true` | If true, dots animate one edge at a time. If false, all dots move simultaneously. |
| `trail` | bool | `false` | If true, the dot leaves a fading trail along the edge path |

---

### 6. pulse

**What it looks like**: The node briefly scales up (e.g., to 120% size) and then scales back to its original size. A quick "thump" effect.

**When to use it**: To draw attention to a specific node, typically the hub in a `hub_spoke` layout, or to emphasize a critical service in a flow.

**Manim method**: `ScaleInPlace` or manual `Scale` animation in a `Succession`.

**Configurable parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `scale_factor` | float | `1.2` | Maximum scale during the pulse |
| `duration` | float | `0.3` | Total time for scale up + scale back |

---

### 7. highlight

**What it looks like**: The node briefly changes its fill color to a highlight color (default: bright yellow) and then transitions back to its original color.

**When to use it**: To call out a node at a specific point in the animation, for example when describing what happens during a failure scenario or to mark the active step in a pipeline.

**Manim method**: `AnimationGroup` of two `FillColor` animations (to highlight color and back).

**Configurable parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `color` | string (hex) | `#f5c518` | The highlight color to flash |
| `duration` | float | `0.5` | Total time for color change + revert |

---

### 8. typewriter

**What it looks like**: The text label appears one character at a time, as if being typed on a keyboard. The node shape is already visible; only the text animates.

**When to use it**: When you want to add narrative pacing to node labels, especially in presentations where you are talking through each component as it appears.

**Manim method**: Iterative `add` of single-character `Text` mobjects with short `Wait` intervals.

**Configurable parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `char_delay` | float | `0.05` | Delay in seconds between each character |
| `cursor` | bool | `false` | Show a blinking cursor at the current typing position |

---

## Specifying Animations

Animations are specified in the `animation` object at the top level of the JSON definition:

```json
{
  "animation": {
    "node_entrance": "draw_border",
    "data_flow": true,
    "effects": ["pulse:hub", "highlight:critical_node"],
    "timing": {
      "stagger": 0.3,
      "data_flow_delay": 1.0
    }
  }
}
```

### Animation Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `node_entrance` | string | `"fade_in"` | The entrance animation for all nodes. One of: `fade_in`, `draw_border`, `grow_from_center`, `slide_in` |
| `data_flow` | bool | `true` | Whether to run the `data_flow_dot` animation after all nodes have appeared |
| `effects` | array | `[]` | Additional effects to apply. Format: `"effect_name"` (apply to all nodes) or `"effect_name:node_id"` (apply to a specific node) |
| `timing.stagger` | float | `0.3` | Delay in seconds between the entrance of each successive node |
| `timing.data_flow_delay` | float | `1.0` | Pause in seconds after the last node appears before data flow dots begin |

---

## Preset Combinations

For convenience, arch-flow provides named presets that bundle common animation choices. Specify a preset with the `preset` field:

```json
{
  "animation": {
    "preset": "tech_demo"
  }
}
```

You can also use a preset and override specific fields:

```json
{
  "animation": {
    "preset": "presentation",
    "timing": {
      "stagger": 0.5
    }
  }
}
```

### Available Presets

#### tech_demo

Best for: Technical walkthroughs, blog posts, documentation.

| Setting | Value |
|---------|-------|
| Node entrance | `draw_border` |
| Data flow | enabled |
| Additional effects | none |
| Stagger | `0.4` |
| Overall feel | Precise, methodical. Each node is "sketched" into place, then dots trace the data paths. |

#### presentation

Best for: Conference talks, team meetings, slide decks.

| Setting | Value |
|---------|-------|
| Node entrance | `fade_in` |
| Data flow | enabled |
| Additional effects | `pulse` on the first node |
| Stagger | `0.3` |
| Overall feel | Smooth and polished. Nodes fade in gracefully, the first node pulses to anchor attention, then data flow dots animate. |

#### minimal

Best for: README files, quick references, inline documentation.

| Setting | Value |
|---------|-------|
| Node entrance | `fade_in` |
| Data flow | enabled |
| Additional effects | none |
| Stagger | `0.2` |
| Overall feel | Fast and unobtrusive. Gets the diagram on screen quickly with minimal motion, but still shows data flow. |

---

## Preset Comparison

| Preset | Entrance | Data Flow | Extra Effects | Stagger | Speed |
|--------|----------|-----------|---------------|---------|-------|
| `tech_demo` | draw_border | yes | none | 0.4s | Moderate |
| `presentation` | fade_in | yes | pulse (first node) | 0.3s | Moderate |
| `minimal` | fade_in | yes | none | 0.2s | Fast |

---

## Custom Animation Example

To build a fully custom animation without using a preset:

```json
{
  "animation": {
    "node_entrance": "slide_in",
    "data_flow": true,
    "effects": [
      "highlight:api_gw",
      "pulse:db",
      "typewriter:client"
    ],
    "timing": {
      "stagger": 0.5,
      "data_flow_delay": 1.5
    },
    "slide_in_direction": "left",
    "flow_dot_color": "#00ff88",
    "flow_dot_sequential": false
  }
}
```

This produces a diagram where:
1. Nodes slide in from the left, one every 0.5 seconds.
2. The `api_gw` node flashes with a highlight effect.
3. The `db` node pulses.
4. The `client` label types out character by character.
5. After a 1.5-second pause, green dots flow along all edges simultaneously.
