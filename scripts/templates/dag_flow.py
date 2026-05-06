"""Directed acyclic graph (DAG) flow template for arch-flow."""

import json
import os
from collections import defaultdict, deque

from manim import *


def hex_to_color(hex_str):
    return ManimColor.from_hex(hex_str)


def build_node_shape(node, node_color, text_color):
    node_type = node.get("type", "process")
    label = node.get("label", node["id"])

    if node_type == "document":
        shape = Rectangle(width=2.0, height=1.0, fill_color=node_color, fill_opacity=0.85,
                          stroke_color=WHITE, stroke_width=1.5)
    elif node_type == "database":
        shape = Rectangle(width=2.0, height=1.0, fill_color=node_color, fill_opacity=0.85,
                          stroke_color=YELLOW, stroke_width=2)
    elif node_type == "cloud":
        shape = Ellipse(width=2.4, height=1.2, fill_color=node_color, fill_opacity=0.85,
                        stroke_color=WHITE, stroke_width=1.5)
    elif node_type == "api":
        shape = RoundedRectangle(width=1.8, height=0.9, corner_radius=0.2,
                                 fill_color=node_color, fill_opacity=0.85,
                                 stroke_color=WHITE, stroke_width=1.5)
    else:
        shape = RoundedRectangle(width=2.2, height=1.0, corner_radius=0.3,
                                 fill_color=node_color, fill_opacity=0.85,
                                 stroke_color=WHITE, stroke_width=1.5)

    text = Text(label, font_size=20, color=text_color)
    text.move_to(shape.get_center())
    return VGroup(shape, text)


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
        current_layer = []
        next_queue = deque()
        for nid in list(queue):
            current_layer.append(nid)
            assigned.add(nid)
        layers.append(current_layer)

        for nid in current_layer:
            for neighbor in adjacency[nid]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    next_queue.append(neighbor)
        queue = next_queue

    for nid in node_ids:
        if nid not in assigned:
            layers[-1].append(nid)

    return layers


def load_config():
    config_path = os.environ.get("ARCH_FLOW_CONFIG")
    if not config_path:
        raise RuntimeError("ARCH_FLOW_CONFIG env var not set")
    with open(config_path, "r") as f:
        return json.load(f)


class DagFlow(Scene):
    def construct(self):
        data = load_config()

        nodes_cfg = data["nodes"]
        edges_cfg = data["edges"]
        style = data.get("style", {})
        title_text = data.get("title", "Architecture")

        bg_color = hex_to_color(style.get("bg_color", "#1a1a2e"))
        node_color = hex_to_color(style.get("node_color", "#0f3460"))
        edge_color = hex_to_color(style.get("edge_color", "#e94560"))
        text_color = hex_to_color(style.get("text_color", "#ffffff"))
        dot_color = hex_to_color(style.get("flow_dot_color", "#f5c518"))

        self.camera.background_color = bg_color

        title = Text(title_text, font_size=36, color=text_color, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title, run_time=1.5))
        self.wait(0.3)

        node_map = {n["id"]: n for n in nodes_cfg}
        layers = compute_layers(nodes_cfg, edges_cfg)

        num_layers = len(layers)
        layer_spacing = 4.5 / max(num_layers - 1, 1) if num_layers > 1 else 0
        top_y = 1.5

        node_groups = {}
        node_positions = {}

        for layer_idx, layer in enumerate(layers):
            y = top_y - layer_idx * layer_spacing if num_layers > 1 else 0
            n_in_layer = len(layer)
            x_spacing = 4.0 / max(n_in_layer, 1)
            x_start = -(n_in_layer - 1) * x_spacing / 2

            for i, nid in enumerate(layer):
                x = x_start + i * x_spacing if n_in_layer > 1 else 0
                node = node_map[nid]
                group = build_node_shape(node, node_color, text_color)
                group.move_to(RIGHT * x + UP * y)
                node_groups[nid] = group
                node_positions[nid] = group.get_center()

        for layer in layers:
            anims = []
            for nid in layer:
                anims.append(Create(node_groups[nid], run_time=1.5))
            self.play(*anims)
            self.wait(0.2)

        self.wait(0.3)

        arrows = []
        paths = []
        for edge in edges_cfg:
            src_pos = node_positions[edge["from"]]
            dst_pos = node_positions[edge["to"]]
            src_shape = node_groups[edge["from"]][0]
            dst_shape = node_groups[edge["to"]][0]

            direction = dst_pos - src_pos
            norm = np.linalg.norm(direction)
            if norm > 0:
                direction = direction / norm
            else:
                direction = DOWN

            start = src_shape.get_boundary_point(direction)
            end = dst_shape.get_boundary_point(-direction)

            arrow = Arrow(start=start, end=end, color=edge_color,
                          stroke_width=3, buff=0.05, max_tip_length_to_length_ratio=0.12)
            arrows.append(arrow)
            paths.append(Line(start=start, end=end))

        for arrow in arrows:
            self.play(Create(arrow, run_time=0.8))

        self.wait(0.3)

        for path in paths:
            dot = Dot(radius=0.1, color=dot_color, fill_opacity=1)
            dot.move_to(path.get_start())
            self.play(MoveAlongPath(dot, path, run_time=2), rate_func=smooth)
            self.play(FadeOut(dot, run_time=0.2))

        self.wait(1.0)


if __name__ == "__main__":
    pass
