#!/usr/bin/env python3
"""Parse JSON input and build scene configuration for Manim rendering."""

import json
import sys
from typing import Any


TEMPLATE_MAP = {
    "basic_flow": "basic_flow",
    "dag_flow": "dag_flow",
    "dag": "dag_flow",
    "pipeline_flow": "pipeline_flow",
    "pipeline": "pipeline_flow",
    "hub_spoke": "hub_spoke",
    "hub": "hub_spoke",
}

VALID_NODE_TYPES = {"document", "process", "database", "cloud", "api", "user", "queue", "default"}

DEFAULT_STYLE = {
    "bg_color": "#1a1a2e",
    "node_color": "#0f3460",
    "edge_color": "#e94560",
    "text_color": "#ffffff",
    "flow_dot_color": "#f5c518",
    "node_width": 2.0,
    "node_height": 1.2,
    "font_size": 24,
}


def validate_nodes(nodes: list[dict]) -> list[dict]:
    validated = []
    for node in nodes:
        if "id" not in node:
            raise ValueError(f"Node missing 'id' field: {node}")
        validated.append({
            "id": node["id"],
            "label": node.get("label", node["id"]),
            "type": node.get("type", "default"),
        })
        if validated[-1]["type"] not in VALID_NODE_TYPES:
            validated[-1]["type"] = "default"
    return validated


def validate_edges(edges: list[dict], node_ids: set[str]) -> list[dict]:
    validated = []
    for edge in edges:
        src = edge.get("from") or edge.get("source") or edge.get("src")
        dst = edge.get("to") or edge.get("target") or edge.get("dst")
        if not src or not dst:
            raise ValueError(f"Edge missing 'from'/'to' fields: {edge}")
        if src not in node_ids:
            raise ValueError(f"Edge source '{src}' not found in nodes")
        if dst not in node_ids:
            raise ValueError(f"Edge target '{dst}' not found in nodes")
        validated.append({
            "from": src,
            "to": dst,
            "label": edge.get("label", ""),
        })
    return validated


def detect_template(nodes: list[dict], edges: list[dict], data: dict) -> str:
    if data.get("template"):
        return TEMPLATE_MAP.get(data["template"], "basic_flow")
    if data.get("stages") or data.get("hub"):
        if data.get("stages"):
            return "pipeline_flow"
        return "hub_spoke"

    edge_count = {}
    for e in edges:
        edge_count[e["from"]] = edge_count.get(e["from"], 0) + 1
        edge_count[e["to"]] = edge_count.get(e["to"], 0) + 1

    has_branch = any(v > 2 for v in edge_count.values())
    has_multi_source = len({e["to"] for e in edges}) < len(edges)

    if has_branch or has_multi_source:
        return "dag_flow"

    return "basic_flow"


def parse(data: dict) -> dict[str, Any]:
    nodes = validate_nodes(data.get("nodes", []))
    node_ids = {n["id"] for n in nodes}
    edges = validate_edges(data.get("edges", []), node_ids)

    style = {**DEFAULT_STYLE, **data.get("style", {})}

    template = detect_template(nodes, edges, data)

    config = {
        "template": template,
        "title": data.get("title", "Architecture"),
        "nodes": nodes,
        "edges": edges,
        "style": style,
        "animation": data.get("animation", {}),
    }

    if template == "pipeline_flow" and "stages" in data:
        config["stages"] = data["stages"]

    if template == "hub_spoke" and "hub" in data:
        config["hub"] = data["hub"]

    return config


def main():
    if len(sys.argv) < 2:
        print("Usage: python parser.py <input.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    config = parse(data)
    print(json.dumps(config, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
