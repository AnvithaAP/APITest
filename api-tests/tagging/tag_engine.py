from __future__ import annotations

from dataclasses import dataclass

from orchestrator.query_engine import ParsedQuery, QueryClause, parse_query, parse_ui_selections


@dataclass(frozen=True)
class TagGroup:
    operator: str
    clauses: list[QueryClause]


class TagEngine:
    """Centralized tag intelligence engine ready for UI query builders."""

    def parse(self, query: str) -> ParsedQuery:
        return parse_query(query)

    def from_multiselect(self, filters: dict[str, list[str]], group_operator: str = "AND") -> ParsedQuery:
        return parse_ui_selections(filters, group_operator=group_operator)

    def from_ui_tree(self, tree: dict) -> ParsedQuery:
        """Build query from nested UI payload.

        Expected shape:
        {
          "operator": "AND"|"OR",
          "children": [
              {"key": "scope", "values": ["api", "ui"]},
              {"operator": "OR", "children": [...]}
          ]
        }
        """
        if not tree:
            return ParsedQuery(groups=[])
        expression = self._to_expression(tree)
        return parse_query(expression)

    def _to_expression(self, node: dict) -> str:
        operator = str(node.get("operator", "AND")).upper()
        children = node.get("children", [])
        rendered: list[str] = []

        for child in children:
            if "children" in child:
                rendered.append(f"({self._to_expression(child)})")
                continue
            key = child.get("key", "").strip()
            values = [str(v).strip() for v in child.get("values", []) if str(v).strip()]
            if key and values:
                rendered.append(f"{key}={','.join(values)}")

        if not rendered:
            return ""
        joiner = f" {operator} "
        return joiner.join(rendered)


tag_engine = TagEngine()
