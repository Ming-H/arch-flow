"""DAG flow template — high contrast, professional style."""

import json
import os
from collections import defaultdict, deque

from manim import *

NODE_COLORS = {
    "document": "#2196F3",
    "process": "#9C27B0",
    "database": "#4CAF50",
    "cloud": "#FF9800",
    "api": "#FFC107",
    "user": "#E91E63",
    "queue": "#00BCD4",
    "default": "#9C27B0",
}

NODE_ICONS = {
    "document": "☰",
    "process": "⚙",
    "database": "⬢",
    "cloud": "☁",
    "api": "➤",
    "user": "●",
    "queue": "≡",
}


def hex_to_color(hex_str):
    return ManimColor.from_hex(hex_str)


def build_node(node):
    node_type = node.get("type", "process")
    label = node.get("label", node["id"])
    color = hex_to_color(NODE_COLORS.get(node_type, NODE_COLORS["default"]))

    w, h = 2.0, 1.1

    body = RoundedRectangle(
        width=w, height=h, corner_radius=0.15,
        fill_color=BLACK, fill_opacity=0.6,
        stroke_color=color, stroke_width=2.5,
    )

    stripe = Rectangle(
        width=0.1, height=h - 0.15,
        fill_color=color, fill_opacity=1.0,
        stroke_width=0,
    ).move_to(body.get_left() + RIGHT * 0.1)

    icon_bg = Circle(
        radius=0.15,
        fill_color=color, fill_opacity=0.3,
        stroke_width=0,
    ).move_to(body.get_top() + DOWN * 0.3 + RIGHT * 0.35)

    icon = Text(NODE_ICONS.get(node_type, "●"), font_size=12, color=color)
    icon.move_to(icon_bg.get_center())

    txt = Text(label, font_size=16, color=WHITE, weight=BOLD)
    txt.move_to(body.get_center() + DOWN * 0.08 + RIGHT * 0.08)

    return VGroup(body, stripe, icon_bg, icon, txt)


def load_config():
    config_path = os.environ.get("ARCH_FLOW_CONFIG")
    if not config_path:
        raise RuntimeError("ARCH_FLOW_CONFIG env var not set")
    with open(config_path, "r") as f:
        return json.load(f)


def compute_layers(nodes_cfg, edges_cfg):
    in_degree = defaultdict(int)
    adjacency = defaultdict(list)
    node_ids = [n["id"] for n in nodes_cfg]
    node_set = set(node_ids)

    for edge in edges_cfg:
        src, dst = edge["from"], edge["to"]
        if src in node_set and dst in node_set:
            adjacency[src].append(dst)
            in_degree[dst] += 1

    queue = deque([nid for nid in node_ids if in_degree[nid] == 0])
    layers = []
    assigned = set()

    while queue:
        current_layer = list(queue)
        layers.append(current_layer)
        for nid in current_layer:
            assigned.add(nid)
        next_queue = deque()
        for nid in current_layer:
            for neighbor in adjacency[nid]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0 and neighbor not in assigned:
                    next_queue.append(neighbor)
        queue = next_queue

    for nid in node_ids:
        if nid not in assigned:
            layers[-1].append(nid)

    return layers


class DagFlow(Scene):
    def construct(self):
        data = load_config()
        nodes_cfg = data["nodes"]
        edges_cfg = data["edges"]
        style = data.get("style", {})
        title_text = data.get("title", "Architecture")
        edge_color = hex_to_color(style.get("edge_color", "#00BCD4"))
        dot_color = hex_to_color(style.get("flow_dot_color", "#FFD740"))

        self.camera.background_color = "#0D1117"

        title = Text(title_text, font_size=32, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.4)
        accent = Line(title.get_left(), title.get_right(), color=edge_color, stroke_width=2)
        accent.next_to(title, DOWN, buff=0.1)
        self.play(Write(title, run_time=1.0), Create(accent, run_time=0.6))
        self.wait(0.2)

        node_map = {n["id"]: n for n in nodes_cfg}
        layers = compute_layers(nodes_cfg, edges_cfg)

        num_layers = len(layers)
        layer_spacing = min(3.5, 6.0 / max(num_layers - 1, 1))
        top_y = 1.5

        node_groups = {}
        node_positions = {}

        for layer_idx, layer in enumerate(layers):
            y = top_y - layer_idx * layer_spacing if num_layers > 1 else 0
            n_in_layer = len(layer)
            x_spacing = min(3.0, 8.0 / max(n_in_layer, 1))
            x_start = -(n_in_layer - 1) * x_spacing / 2

            for i, nid in enumerate(layer):
                x = x_start + i * x_spacing if n_in_layer > 1 else 0
                group = build_node(node_map[nid])
                group.move_to(RIGHT * x + UP * y)
                node_groups[nid] = group
                node_positions[nid] = group.get_center()

        # Animate layer by layer
        for layer in layers:
            anims = []
            for nid in layer:
                group = node_groups[nid]
                group.set_opacity(0)
                self.add(group)
                anims.append(group.animate.set_opacity(1))
            self.play(*anims, run_time=0.6, rate_func=smooth)
            self.wait(0.15)

        self.wait(0.3)

        # Draw edges
        arrows = []
        paths = []
        for edge in edges_cfg:
            src_body = node_groups[edge["from"]][0]
            dst_body = node_groups[edge["to"]][0]
            src_pos = node_positions[edge["from"]]
            dst_pos = node_positions[edge["to"]]

            direction = dst_pos - src_pos
            norm = np.linalg.norm(direction)
            if norm > 0:
                direction = direction / norm
            else:
                direction = DOWN

            start = src_body.get_boundary_point(direction)
            end = dst_body.get_boundary_point(-direction)

            arrow = Arrow(
                start=start, end=end, color=edge_color, stroke_width=2.5,
                buff=0.05, max_tip_length_to_length_ratio=0.12,
                tip_shape=StealthTip,
            )
            arrows.append(arrow)
            paths.append(Line(start=start, end=end))

        for arrow in arrows:
            self.play(Create(arrow, run_time=0.5))
        self.wait(0.3)

        # Data flow dots
        for path in paths:
            dot = Dot(radius=0.1, color=dot_color, fill_opacity=1.0)
            dot.move_to(path.get_start())
            self.add(dot)
            self.play(MoveAlongPath(dot, path, run_time=0.8), rate_func=smooth)
            self.remove(dot)

        self.wait(1.0)


if __name__ == "__main__":
    pass
