"""Basic linear left-to-right flow template — high contrast, professional style."""

import json
import os

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

    w, h = 2.2, 1.3

    # Background fill — dark but tinted with node color
    body = RoundedRectangle(
        width=w, height=h, corner_radius=0.15,
        fill_color=BLACK, fill_opacity=0.6,
        stroke_color=color, stroke_width=2.5,
    )

    # Left accent stripe
    stripe = Rectangle(
        width=0.12, height=h - 0.15,
        fill_color=color, fill_opacity=1.0,
        stroke_width=0,
    ).move_to(body.get_left() + RIGHT * 0.12)

    # Icon circle
    icon_bg = Circle(
        radius=0.18,
        fill_color=color, fill_opacity=0.3,
        stroke_width=0,
    ).move_to(body.get_top() + DOWN * 0.35 + RIGHT * 0.4)

    icon_char = NODE_ICONS.get(node_type, "●")
    icon = Text(icon_char, font_size=14, color=color)
    icon.move_to(icon_bg.get_center())

    # Label text
    txt = Text(label, font_size=18, color=WHITE, weight=BOLD)
    txt.move_to(body.get_center() + DOWN * 0.1 + RIGHT * 0.1)

    return VGroup(body, stripe, icon_bg, icon, txt)


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
        edge_color = hex_to_color(style.get("edge_color", "#00BCD4"))
        dot_color = hex_to_color(style.get("flow_dot_color", "#FFD740"))

        self.camera.background_color = "#0D1117"

        # Title
        title = Text(title_text, font_size=32, color=WHITE, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        accent = Line(title.get_left(), title.get_right(), color=edge_color, stroke_width=2)
        accent.next_to(title, DOWN, buff=0.1)
        self.play(Write(title, run_time=1.0), Create(accent, run_time=0.6))
        self.wait(0.2)

        # Layout nodes horizontally
        n = len(nodes_cfg)
        spacing = min(3.0, 11.0 / max(n, 1))
        start_x = -(n - 1) * spacing / 2

        node_groups = {}
        node_positions = {}

        for i, node in enumerate(nodes_cfg):
            group = build_node(node)
            pos = RIGHT * (start_x + i * spacing) + DOWN * 0.2
            group.move_to(pos)
            node_groups[node["id"]] = group
            node_positions[node["id"]] = group.get_center()

        # Animate nodes appearing with FadeIn + slight scale
        for node in nodes_cfg:
            group = node_groups[node["id"]]
            group.set_opacity(0)
            self.add(group)
            self.play(
                group.animate.set_opacity(1),
                run_time=0.5,
                rate_func=smooth,
            )
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

            start = src_body.get_boundary_point(direction)
            end = dst_body.get_boundary_point(-direction)

            arrow = Arrow(
                start=start, end=end,
                color=edge_color, stroke_width=2.5,
                buff=0.05, max_tip_length_to_length_ratio=0.15,
                tip_shape=StealthTip,
            )
            path = Line(start=start, end=end)
            arrows.append(arrow)
            paths.append(path)

        for arrow in arrows:
            self.play(Create(arrow, run_time=0.6))
        self.wait(0.3)

        # Animate data flow dots
        for path in paths:
            dot = Dot(radius=0.12, color=dot_color, fill_opacity=1.0)
            dot.move_to(path.get_start())
            self.add(dot)
            self.play(
                MoveAlongPath(dot, path, run_time=1.0),
                rate_func=smooth,
            )
            self.remove(dot)

        self.wait(1.0)


if __name__ == "__main__":
    pass
