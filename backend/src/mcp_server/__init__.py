"""The MCP interface of the API (mcp-server, design D12): a second entry
point next to the REST routes, calling the same domain services. Not named
`mcp`, which would shadow the SDK package on the import path."""

from . import tools  # noqa: F401  (registers the tools)
from .gate import McpGate
from .server import mcp_lifespan

__all__ = ["McpGate", "mcp_lifespan"]
