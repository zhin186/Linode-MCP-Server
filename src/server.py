"""
Linode Enhanced MCP Server
"""

import asyncio
import os
from typing import Any, Dict, List

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel,
)

from .linode_client import LinodeClient
from .tools import (
    get_region_instance_stats,
    calculate_monthly_cost,
    find_idle_resources,
    audit_ip_resources,
    batch_tag_management,
)


class LinodeMCPServer(Server):
    """Linode MCP 服务器"""
    
    def __init__(self):
        super().__init__("linode-enhanced-mcp")
        self.client: LinodeClient = None
    
    async def initialize(self):
        """初始化"""
        self.client = LinodeClient()
    
    async def list_resources(self) -> List[Resource]:
        """列出资源"""
        return []
    
    async def read_resource(self, uri: Any) -> str:
        """读取资源"""
        return ""
    
    async def list_tools(self) -> List[Tool]:
        """列出可用工具"""
        return [
            Tool(
                name="get_region_instance_stats",
                description="获取指定区域的实例统计信息，包括数量、状态分布、类型分布和成本估算",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "region": {
                            "type": "string",
                            "description": "区域 ID，如 us-east, us-west, eu-west, ap-south, ap-northeast 等"
                        },
                        "include_cost": {
                            "type": "boolean",
                            "description": "是否包含成本估算",
                            "default": True
                        }
                    },
                    "required": ["region"]
                }
            ),
            Tool(
                name="calculate_monthly_cost",
                description="计算当前所有资源的月度费用估算，支持按区域、类型或标签分组",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "group_by": {
                            "type": "string",
                            "enum": ["region", "type", "label"],
                            "description": "分组方式",
                            "default": "region"
                        }
                    }
                }
            ),
            Tool(
                name="find_idle_resources",
                description="查找闲置资源：长期关机、无标签、watchdog禁用或无公网IP的实例",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "days_offline": {
                            "type": "integer",
                            "description": "定义闲置天数阈值",
                            "default": 7
                        },
                        "missing_tags": {
                            "type": "boolean",
                            "description": "是否检查无标签实例",
                            "default": True
                        }
                    }
                }
            ),
            Tool(
                name="audit_ip_resources",
                description="审计 IP 资源使用情况，统计公网/私网 IP 分布、检测未分配 IP",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "region": {
                            "type": "string",
                            "description": "指定区域审计，不传则审计所有区域"
                        }
                    }
                }
            ),
            Tool(
                name="batch_tag_management",
                description="批量管理实例标签：添加、删除或替换标签",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["add", "remove", "replace"],
                            "description": "操作类型：add添加, remove删除, replace替换"
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "标签列表"
                        },
                        "instance_ids": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "实例 ID 列表，不传则处理所有实例"
                        },
                        "filter_by_region": {
                            "type": "string",
                            "description": "按区域过滤实例"
                        }
                    },
                    "required": ["action", "tags"]
                }
            ),
        ]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """调用工具"""
        if not self.client:
            await self.initialize()
        
        try:
            if name == "get_region_instance_stats":
                return await get_region_instance_stats(self.client, arguments)
            elif name == "calculate_monthly_cost":
                return await calculate_monthly_cost(self.client, arguments)
            elif name == "find_idle_resources":
                return await find_idle_resources(self.client, arguments)
            elif name == "audit_ip_resources":
                return await audit_ip_resources(self.client, arguments)
            elif name == "batch_tag_management":
                return await batch_tag_management(self.client, arguments)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
        
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """主入口"""
    server = LinodeMCPServer()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="linode-enhanced-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
