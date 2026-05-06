"""Basic linear left-to-right flow — clean light theme with polished animations."""

import json
import os

from manim import *

NODE_FILLS = {
    "document": "#FFF3E0", "process": "#E8EAF6", "database": "#E8F5E9",
    "cloud": "#E3F2FD", "api": "#FFF8E1", "user": "#FCE4EC",
    "queue": "#E0F7FA", "default": "#E8EAF6",
}
NODE_ACCENTS = {
    "document": "#E65100", "process": "#283593", "database": "#2E7D32",
    "cloud": "#1565C0", "api": "#F57F17", "user": "#C2185B",
    "queue": "#00838F", "default": "#283593",
}
NODE_ICONS = {
    "document": "📄", "process": "⚙", "database": "🗄",
    "cloud": "☁", "api": "🔌", "user": "👤", "queue": "📨", "default": "●",
}


def hex_to_color(hex_str):
    return ManimColor.from_hex(hex_str)


def build_node(node):
    node_type = node.get("type", "process")
    label = node.get("label", node["id"])
    fill = hex_to_color(NODE_FILLS.get(node_type, NODE_FILLS["default"]))
    accent = hex_to_color(NODE_ACCENTS.get(node_type, NODE_ACCENTS["default"]))

    w, h = 2.6, 1.4

    shadow = RoundedRectangle(
        width=w, height=h, corner_radius=0.2,
        fill_color=BLACK, fill_opacity=0.06, stroke_width=0,
    ).shift(DOWN * 0.05 + RIGHT * 0.05)

    body = RoundedRectangle(
        width=w, height=h, corner_radius=0.2,
        fill_color=fill, fill_opacity=1.0,
        stroke_color=hex_to_color("#E0E0E0"), stroke_width=1.5,
    )

    icon = Text(NODE_ICONS.get(node_type, "●"), font_size=22, color=accent)
    icon.move_to(body.get_left() + RIGHT * 0.45 + UP * 0.05)

    txt = Text(label, font_size=16, color=hex_to_color("#212121"), weight=BOLD)
    txt.move_to(body.get_center() + RIGHT * 0.15 + DOWN * 0.05)

    return VGroup(shadow, body, icon, txt)


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

        arrow_color = hex_to_color("#9E9E9E")
        dot_color = hex_to_color("#42A5F5")

        self.camera.background_color = "#FAFAFA"

        # Title bar
        title_bg = Rectangle(
            width=14.2, height=0.8,
            fill_color=hex_to_color("#4CAF50"), fill_opacity=1.0,
            stroke_width=0,
        ).to_edge(UP, buff=0)
        title = Text(title_text, font_size=30, color=WHITE, weight=BOLD)
        title.move_to(title_bg.get_center())

        self.play(
            LaggedStart(FadeIn(title_bg, run_time=0.6), Write(title, run_time=0.8), lag_ratio=0.3),
        )
        self.wait(0.3)

        # Layout nodes
        n = len(nodes_cfg)
        spacing = min(3.2, 11.5 / max(n, 1))
        start_x = -(n - 1) * spacing / 2

        node_groups = {}
        node_positions = {}

        for i, node in enumerate(nodes_cfg):
            group = build_node(node)
            pos = RIGHT * (start_x + i * spacing) + DOWN * 0.5
            group.move_to(pos)
            node_groups[node["id"]] = group
            node_positions[node["id"]] = group.get_center()

        # Nodes fade in with stagger
        node_anims = []
        for node in nodes_cfg:
            g = node_groups[node["id"]]
            g.set_opacity(0)
            self.add(g)
            node_anims.append(g.animate.set_opacity(1))

        self.play(LaggedStart(*node_anims, lag_ratio=0.15, run_time=1.5))
        self.wait(0.4)

        # Draw edges with step numbers
        arrows = []
        paths = []
        for idx, edge in enumerate(edges_cfg):
            src_body = node_groups[edge["from"]][1]
            dst_body = node_groups[edge["to"]][1]
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
                color=arrow_color, stroke_width=2.5,
                buff=0.08, max_tip_length_to_length_ratio=0.12,
                tip_shape=StealthTip,
            )

            mid = (start + end) / 2
            step_circle = Circle(
                radius=0.25, fill_color=hex_to_color("#FFC107"), fill_opacity=1.0,
                stroke_width=0,
            ).move_to(mid)
            step_num = Text(str(idx + 1), font_size=14, color=hex_to_color("#212121"), weight=BOLD)
            step_num.move_to(mid)

            arrows.append((arrow, step_circle, step_num))
            paths.append(Line(start=start, end=end))

        # Arrows animate in with stagger
        arrow_anims = []
        for arrow, step_circle, step_num in arrows:
            arrow_anims.extend([
                Create(arrow, run_time=0.3),
                GrowFromCenter(step_circle, run_time=0.2),
                FadeIn(step_num, run_time=0.15),
            ])
        self.play(LaggedStart(*arrow_anims, lag_ratio=0.1, run_time=2.0))
        self.wait(0.4)

        # Data flow dots — trail of 3 dots per edge for smooth flow feel
        for path in paths:
            dots = VGroup()
            for j in range(3):
                d = Dot(
                    radius=0.08,
                    color=dot_color,
                    fill_opacity=0.9 - j * 0.25,
                )
                d.move_to(path.get_start())
                dots.add(d)
            self.add(dots)
            self.play(
                MoveAlongPath(dots[0], path, run_time=0.8),
                rate_func=smooth,
            )
            self.remove(dots)

        self.wait(1.5)


if __name__ == "__main__":
    pass
