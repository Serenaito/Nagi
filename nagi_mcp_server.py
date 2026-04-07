# -*- coding: utf-8 -*-
"""
Nagi MCP Server - Model Context Protocol 服务器

让 AI 模型（如 Claude）能够通过 Nagi 桌面宠物显示对话和交互。

启动方式:
    python nagi_mcp_server.py

配置 Claude Desktop (claude_desktop_config.json):
{
  "mcpServers": {
    "nagi": {
      "command": "python",
      "args": ["path/to/nagi_mcp_server.py"]
    }
  }
}

或使用 uvx 运行:
{
  "mcpServers": {
    "nagi": {
      "command": "uvx",
      "args": ["--from", "path/to/nagi", "nagi-mcp"]
    }
  }
}
"""

import asyncio
import json
import logging
from typing import Any, Sequence
from contextlib import asynccontextmanager

# MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        Tool,
        TextContent,
        CallToolResult,
        ListToolsResult,
    )
except ImportError:
    print("请安装 MCP SDK: pip install mcp")
    print("或: pip install 'mcp[cli]'")
    exit(1)

# 网络客户端
from network import NetworkClient

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nagi-mcp")


class NagiMCPServer:
    """Nagi MCP 服务器"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9527):
        self.host = host
        self.port = port
        self._client: NetworkClient | None = None
    
    def _ensure_connection(self) -> bool:
        """确保已连接到 Nagi"""
        if self._client is None:
            self._client = NetworkClient(self.host, self.port)
        
        try:
            return self._client.connect()
        except Exception as e:
            logger.error(f"连接 Nagi 失败: {e}")
            return False
    
    def say(self, text: str, duration: int = 3000, typing_speed: int = 50) -> dict:
        """显示对话气泡"""
        if not self._ensure_connection():
            return {"success": False, "error": "无法连接到 Nagi 服务"}
        
        return self._client.show_bubble(
            text=text,
            duration=duration,
            typing_speed=typing_speed
        )
    
    def show_window(self) -> dict:
        """显示窗口"""
        if not self._ensure_connection():
            return {"success": False, "error": "无法连接到 Nagi 服务"}
        return self._client.show_window()
    
    def hide_window(self) -> dict:
        """隐藏窗口"""
        if not self._ensure_connection():
            return {"success": False, "error": "无法连接到 Nagi 服务"}
        return self._client.hide_window()
    
    def move_window(self, x: int, y: int) -> dict:
        """移动窗口"""
        if not self._ensure_connection():
            return {"success": False, "error": "无法连接到 Nagi 服务"}
        return self._client.move_window(x, y)
    
    def change_model(self, model_name: str) -> dict:
        """切换模型"""
        if not self._ensure_connection():
            return {"success": False, "error": "无法连接到 Nagi 服务"}
        return self._client.change_model(model_name)
    
    def get_status(self) -> dict:
        """获取状态"""
        if not self._ensure_connection():
            return {"success": False, "error": "无法连接到 Nagi 服务"}
        return self._client.get_status()
    
    def get_models(self) -> dict:
        """获取可用模型列表"""
        if not self._ensure_connection():
            return {"success": False, "error": "无法连接到 Nagi 服务"}
        return self._client.get_models()
    
    def close(self):
        """关闭连接"""
        if self._client:
            self._client.close()
            self._client = None


# 创建 MCP Server 实例
app = Server("nagi-mcp")
nagi = NagiMCPServer()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """列出所有可用工具"""
    return [
        Tool(
            name="nagi_say",
            description="让桌面宠物 Nagi 显示对话气泡。用于向用户展示 AI 的回复或消息，会以可爱的气泡形式显示在屏幕上，带有打字机效果。",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "要显示的对话文本内容"
                    },
                    "duration": {
                        "type": "integer",
                        "description": "文字显示完成后的持续时间（毫秒），默认 3000",
                        "default": 3000
                    },
                    "typing_speed": {
                        "type": "integer",
                        "description": "打字机效果的速度（毫秒/字符），值越小越快，默认 50",
                        "default": 50
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="nagi_show",
            description="显示桌面宠物 Nagi 窗口。如果窗口被隐藏或最小化，调用此工具可以让 Nagi 重新出现在屏幕上。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="nagi_hide",
            description="隐藏桌面宠物 Nagi 窗口。调用此工具可以让 Nagi 暂时从屏幕上消失。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="nagi_move",
            description="移动桌面宠物 Nagi 窗口到指定的屏幕位置。",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "目标位置的 X 坐标（像素）"
                    },
                    "y": {
                        "type": "integer",
                        "description": "目标位置的 Y 坐标（像素）"
                    }
                },
                "required": ["x", "y"]
            }
        ),
        Tool(
            name="nagi_change_model",
            description="切换桌面宠物 Nagi 的模型/形象。",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_name": {
                        "type": "string",
                        "description": "要切换到的模型名称"
                    }
                },
                "required": ["model_name"]
            }
        ),
        Tool(
            name="nagi_get_status",
            description="获取桌面宠物 Nagi 的当前状态信息，包括窗口位置、当前模型等。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="nagi_get_models",
            description="获取桌面宠物 Nagi 可用的模型列表。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """处理工具调用"""
    logger.info(f"调用工具: {name}, 参数: {arguments}")
    
    try:
        if name == "nagi_say":
            result = nagi.say(
                text=arguments.get("text", ""),
                duration=arguments.get("duration", 3000),
                typing_speed=arguments.get("typing_speed", 50)
            )
        elif name == "nagi_show":
            result = nagi.show_window()
        elif name == "nagi_hide":
            result = nagi.hide_window()
        elif name == "nagi_move":
            result = nagi.move_window(
                x=arguments.get("x", 0),
                y=arguments.get("y", 0)
            )
        elif name == "nagi_change_model":
            result = nagi.change_model(
                model_name=arguments.get("model_name", "")
            )
        elif name == "nagi_get_status":
            result = nagi.get_status()
        elif name == "nagi_get_models":
            result = nagi.get_models()
        else:
            result = {"success": False, "error": f"未知工具: {name}"}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"工具执行错误: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)
        )]


async def main():
    """主函数"""
    logger.info("启动 Nagi MCP Server...")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    finally:
        nagi.close()
        logger.info("Nagi MCP Server 已关闭")


if __name__ == "__main__":
    asyncio.run(main())
