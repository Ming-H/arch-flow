"""Basic linear left-to-right flow template for arch-flow."""

import json
import os

from manim import *


def hex_to_color(hex_str):
    return ManimColor.from_hex(hex_str)


def build_node_shape(node, node_color, text_color):
    node_type = node.get("type", "process")
    label = node.get("label", node["id"])

    if node_type == "document":
        shape = Rectangle(width=2.0, height=1.2, fill_color=node_color, fill_opacity=0.85,
                          stroke_color=WHITE, stroke_width=1.5)
    elif node_type == "database":
        shape = Rectangle(width=2.0, height=1.2, fill_color=node_color, fill_opacity=0.85,
                          stroke_color=YELLOW, stroke_width=2)
    elif node_type == "cloud":
        shape = Ellipse(width=2.4, height=1.4, fill_color=node_color, fill_opacity=0.85,
                        stroke_color=WHITE, stroke_width=1.5)
    elif node_type == "api":
        shape = RoundedRectangle(width=1.8, height=1.0, corner_radius=0.2,
                                 fill_color=node_color, fill_opacity=0.85,
                                 stroke_color=WHITE, stroke_width=1.5)
    else:
        shape = RoundedRectangle(width=2.2, height=1.2, corner_radius=0.3,
                                 fill_color=node_color, fill_opacity=0.85,
                                 stroke_color=WHITE, stroke_width=1.5)

    text = Text(label, font_size=22, color=text_color)
    text.move_to(shape.get_center())

    group = VGroup(shape, text)
    return group


def load_config():
    config_path = os.environ.get("ARCH_FLOW_CONFIG")
    if not config_path:
        raise RuntimeError("ARCH_FLOW_CONFIG env var not set")
    with open(config_path, "r") as f:
        return json.load(f)


class BasicFlow(Scene):
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

        n = len(nodes_cfg)
        spacing = 10.0 / max(n - 1, 1) if n > 1 else 0
        start_x = -5.0

        node_groups = {}
        node_positions = {}

        for i, node in enumerate(nodes_cfg):
            pos_x = start_x + i * spacing if n > 1 else 0
            pos_y = 0
            group = build_node_shape(node, node_color, text_color)
            group.move_to(UP * 0.3 + RIGHT * pos_x)
            node_groups[node["id"]] = group
            node_positions[node["id"]] = group.get_center()

        for node in nodes_cfg:
            group = node_groups[node["id"]]
            self.play(Create(group, run_time=1.5))
            self.wait(0.2)

        self.wait(0.3)

        arrows = []
        paths = []
        for edge in edges_cfg:
            src_pos = node_positions[edge["from"]]
            dst_pos = node_positions[edge["to"]]

            src_shape = node_groups[edge["from"]][0]
            dst_shape = node_groups[edge["to"]][0]

            direction = (dst_pos - src_pos)
            direction = direction / np.linalg.norm(direction)

            start = src_shape.get_boundary_point(direction)
            end = dst_shape.get_boundary_point(-direction)

            arrow = Arrow(start=start, end=end, color=edge_color,
                          stroke_width=3, buff=0.05, max_tip_length_to_length_ratio=0.15)
            arrows.append(arrow)

            path = Line(start=start, end=end)
            paths.append(path)

        for arrow in arrows:
            self.play(Create(arrow, run_time=1.0))

        self.wait(0.3)

        for path in paths:
            dot = Dot(radius=0.12, color=dot_color, fill_opacity=1)
            dot.move_to(path.get_start())
            self.play(MoveAlongPath(dot, path, run_time=2), rate_func=smooth)
            self.play(FadeOut(dot, run_time=0.3))

        self.wait(1.0)


if __name__ == "__main__":
    pass
