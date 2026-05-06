"""Pipeline flow — clean light theme with stage groups."""

import json
import os
from collections import defaultdict

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

    w, h = 2.0, 1.0
    shadow = RoundedRectangle(width=w, height=h, corner_radius=0.15,
        fill_color=BLACK, fill_opacity=0.08, stroke_width=0).shift(DOWN * 0.03 + RIGHT * 0.03)
    body = RoundedRectangle(width=w, height=h, corner_radius=0.15,
        fill_color=fill, fill_opacity=1.0,
        stroke_color=hex_to_color("#BDBDBD"), stroke_width=1.5)
    icon = Text(NODE_ICONS.get(node_type, "●"), font_size=16, color=accent)
    icon.move_to(body.get_left() + RIGHT * 0.35)
    txt = Text(label, font_size=14, color=hex_to_color("#212121"), weight=BOLD)
    txt.move_to(body.get_center() + RIGHT * 0.08)
    return VGroup(shadow, body, icon, txt)


def load_config():
    config_path = os.environ.get("ARCH_FLOW_CONFIG")
    if not config_path:
        raise RuntimeError("ARCH_FLOW_CONFIG env var not set")
    with open(config_path, "r") as f:
        return json.load(f)


def auto_detect_stages(nodes_cfg, edges_cfg):
    node_ids = [n["id"] for n in nodes_cfg]
    out_edges = defaultdict(list)
    in_edges = defaultdict(list)
    node_set = set(node_ids)
    for edge in edges_cfg:
        if edge["from"] in node_set and edge["to"] in node_set:
            out_edges[edge["from"]].append(edge["to"])
            in_edges[edge["to"]].append(edge["from"])
    visited, stages = set(), []
    sources = [nid for nid in node_ids if len(in_edges[nid]) == 0]
    if not sources:
        sources = [node_ids[0]]
    current = sources[:]
    while current and len(visited) < len(node_ids):
        stage = [nid for nid in current if nid not in visited]
        if not stage:
            remaining = [nid for nid in node_ids if nid not in visited]
            stage = remaining[:1] if remaining else []
            if not stage: break
        stages.append(stage)
        for nid in stage: visited.add(nid)
        current = []
        for nid in stage:
            for nb in out_edges[nid]:
                if nb not in visited: current.append(nb)
    for nid in node_ids:
        if nid not in visited:
            stages[-1].append(nid) if stages else stages.append([nid])
    return [{"name": f"Stage {i+1}", "nodes": s} for i, s in enumerate(stages)]


class PipelineFlow(Scene):
    def construct(self):
        data = load_config()
        nodes_cfg = data["nodes"]
        edges_cfg = data["edges"]
        style = data.get("style", {})
        title_text = data.get("title", "Architecture")

        self.camera.background_color = "#FAFAFA"

        title_bg = Rectangle(width=14, height=0.7,
            fill_color=hex_to_color("#4CAF50"), fill_opacity=1.0, stroke_width=0
        ).to_edge(UP, buff=0.1)
        title = Text(title_text, font_size=28, color=WHITE, weight=BOLD)
        title.move_to(title_bg.get_center())
        self.play(FadeIn(title_bg, run_time=0.5), Write(title, run_time=0.8))
        self.wait(0.2)

        node_map = {n["id"]: n for n in nodes_cfg}
        stages = data.get("stages") if "stages" in data else auto_detect_stages(nodes_cfg, edges_cfg)

        ns = len(stages)
        sw = min(2.8, 12.0 / max(ns, 1))
        tw = ns * sw
        sx = -tw / 2 + sw / 2

        node_groups, node_positions = {}, {}
        stage_accent = hex_to_color("#4CAF50")

        for si, stage in enumerate(stages):
            cx = sx + si * sw
            nodes = stage["nodes"]
            nl = len(nodes)
            ys = 1.2
            y0 = (nl - 1) * ys / 2
            bg_h = max(nl * ys + 0.6, 1.8)

            sbg = RoundedRectangle(width=sw - 0.2, height=bg_h, corner_radius=0.15,
                fill_color=hex_to_color("#F5F5F5"), fill_opacity=0.6,
                stroke_color=hex_to_color("#BDBDBD"), stroke_width=1.2, stroke_opacity=0.6)
            sbg.move_to(RIGHT * cx + DOWN * 0.4)

            slbl = Text(stage["name"], font_size=12, color=stage_accent, weight=BOLD)
            slbl.next_to(sbg, UP, buff=0.06)

            self.play(FadeIn(sbg, run_time=0.4), Write(slbl, run_time=0.3))
            self.wait(0.05)

            for i, nid in enumerate(nodes):
                g = build_node(node_map[nid])
                y = y0 - i * ys if nl > 1 else 0
                g.move_to(RIGHT * cx + DOWN * 0.4 + UP * y)
                node_groups[nid] = g
                node_positions[nid] = g.get_center()
                g.set_opacity(0)
                self.add(g)
                self.play(g.animate.set_opacity(1), run_time=0.3)
            self.wait(0.05)

        self.wait(0.2)

        arrow_color = hex_to_color("#757575")
        arrows, paths = [], []
        for idx, edge in enumerate(edges_cfg):
            if edge["from"] not in node_positions or edge["to"] not in node_positions: continue
            sb = node_groups[edge["from"]][1]
            db = node_groups[edge["to"]][1]
            sp, dp = node_positions[edge["from"]], node_positions[edge["to"]]
            d = dp - sp
            n = np.linalg.norm(d)
            if n > 0: d = d / n
            else: d = RIGHT
            s, e = sb.get_boundary_point(d), db.get_boundary_point(-d)
            arr = Arrow(start=s, end=e, color=arrow_color, stroke_width=2,
                        buff=0.05, max_tip_length_to_length_ratio=0.12, tip_shape=StealthTip)
            mid = (s + e) / 2
            sc = Circle(radius=0.18, fill_color=hex_to_color("#FFC107"), fill_opacity=1.0, stroke_width=0).move_to(mid)
            sn = Text(str(idx + 1), font_size=11, color=hex_to_color("#212121"), weight=BOLD).move_to(mid)
            arrows.append((arr, sc, sn))
            paths.append(Line(start=s, end=e))

        for arr, sc, sn in arrows:
            self.play(Create(arr, run_time=0.4), FadeIn(sc, run_time=0.3), FadeIn(sn, run_time=0.3))
        self.wait(0.3)

        for path in paths:
            dot = Dot(radius=0.08, color=hex_to_color("#42A5F5"), fill_opacity=1.0)
            dot.move_to(path.get_start())
            self.add(dot)
            self.play(MoveAlongPath(dot, path, run_time=0.6), rate_func=smooth)
            self.remove(dot)

        self.wait(1.0)


if __name__ == "__main__":
    pass
