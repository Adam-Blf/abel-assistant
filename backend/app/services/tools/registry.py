"""
=============================================================================
TOOLS REGISTRY - Tool Management System
=============================================================================
A.B.E.L. Project - Registry for external tools that Gemini can use
=============================================================================
"""

from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ToolCategory(str, Enum):
    """Tool categories"""
    WEATHER = "weather"
    NEWS = "news"
    SEARCH = "search"
    UTILITY = "utility"


@dataclass
class ToolDefinition:
    """Tool definition for Gemini function calling"""
    name: str
    description: str
    category: ToolCategory
    parameters: Dict[str, Any]
    handler: Callable
    requires_auth: bool = False
    rate_limit: int = 30  # requests per minute


class ToolRegistry:
    """
    Tool registry for managing external tools

    Tools are registered here and can be:
    - Queried for their definitions (for Gemini function calling)
    - Executed by name with parameters
    """

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        logger.info("[ToolRegistry] Initialized")

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool"""
        self._tools[tool.name] = tool
        logger.info(f"[ToolRegistry] Registered tool: {tool.name}")

    def unregister(self, name: str) -> bool:
        """Unregister a tool"""
        if name in self._tools:
            del self._tools[name]
            logger.info(f"[ToolRegistry] Unregistered tool: {name}")
            return True
        return False

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name"""
        return self._tools.get(name)

    def get_all_tools(self) -> List[ToolDefinition]:
        """Get all registered tools"""
        return list(self._tools.values())

    def get_tools_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        """Get tools by category"""
        return [t for t in self._tools.values() if t.category == category]

    def get_gemini_function_declarations(self) -> List[Dict[str, Any]]:
        """
        Get tool definitions in Gemini function calling format

        Returns list of function declarations for Gemini API
        """
        declarations = []

        for tool in self._tools.values():
            declaration = {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": tool.parameters.get("properties", {}),
                    "required": tool.parameters.get("required", [])
                }
            }
            declarations.append(declaration)

        return declarations

    async def execute(
        self,
        name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool by name

        Args:
            name: Tool name
            parameters: Tool parameters

        Returns:
            Tool execution result
        """
        tool = self._tools.get(name)

        if not tool:
            return {
                "success": False,
                "error": f"Tool '{name}' not found"
            }

        try:
            result = await tool.handler(**parameters)
            return {
                "success": True,
                "tool": name,
                "result": result
            }
        except Exception as e:
            logger.error(f"[ToolRegistry] Tool execution failed: {name} - {e}")
            return {
                "success": False,
                "tool": name,
                "error": str(e)
            }


# Global registry instance
_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance"""
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry
