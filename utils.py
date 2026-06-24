"""
Utility functions for the Ozon MCP server.
"""
import json
from typing import Any

def format_json_res(data: Any) -> str:
    """Utility to ensure consistent JSON output for MCP tools."""
    return json.dumps(data, ensure_ascii=False, indent=2)
