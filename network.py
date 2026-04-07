# -*- coding: utf-8 -*-
"""
网络模块 - 基于 Socket 通信的远程控制接口

支持的命令格式 (JSON):
{
    "action": "命令名称",
    "params": { ... }  // 可选参数
}

支持的命令:
- show_window: 显示窗口
- hide_window: 隐藏窗口
- show_bubble: 显示气泡文字，参数: text, x, y, duration, typing_speed, max_width
- change_model: 切换模型，参数: model_name
- set_topmost: 设置置顶，参数: enabled
- set_movable: 设置可移动，参数: enabled
- move_window: 移动窗口，参数: x, y
- reset_position: 重置窗口位置
- get_status: 获取状态信息
- get_models: 获取可用模型列表
- quit: 退出程序
"""

import json
import socket
import threading
import logging
from typing import Callable, Dict, Any, Optional
from PySide6.QtCore import QObject, Signal, QThread

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NetworkCommand:
    """网络命令定义"""
    SHOW_WINDOW = "show_window"
    HIDE_WINDOW = "hide_window"
    SHOW_BUBBLE = "show_bubble"
    CHANGE_MODEL = "change_model"
    SET_TOPMOST = "set_topmost"
    SET_MOVABLE = "set_movable"
    MOVE_WINDOW = "move_window"
    RESET_POSITION = "reset_position"
    GET_STATUS = "get_status"
    GET_MODELS = "get_models"
    QUIT = "quit"


class NetworkServerThread(QThread):
    """网络服务器线程"""
    
    # 信号定义
    command_received = Signal(str, dict)  # action, params
    client_connected = Signal(str)  # client address
    client_disconnected = Signal(str)  # client address
    error_occurred = Signal(str)  # error message
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9527, parent=None):
        super().__init__(parent)
        self.host = host
        self.port = port
        self._running = False
        self._server_socket: Optional[socket.socket] = None
        self._clients: Dict[str, socket.socket] = {}
        self._lock = threading.Lock()
        self._response_queue: Dict[str, str] = {}
    
    def run(self):
        """启动服务器"""
        self._running = True
        
        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind((self.host, self.port))
            self._server_socket.listen(5)
            self._server_socket.settimeout(1.0)  # 设置超时以便能够检查 _running 标志
            
            logger.info(f"网络服务器启动: {self.host}:{self.port}")
            
            while self._running:
                try:
                    client_socket, address = self._server_socket.accept()
                    client_addr = f"{address[0]}:{address[1]}"
                    
                    with self._lock:
                        self._clients[client_addr] = client_socket
                    
                    self.client_connected.emit(client_addr)
                    logger.info(f"客户端连接: {client_addr}")
                    
                    # 为每个客户端启动处理线程
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_addr),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.timeout:
                    continue
                except Exception as e:
                    if self._running:
                        logger.error(f"接受连接错误: {e}")
                        
        except Exception as e:
            self.error_occurred.emit(f"服务器启动失败: {e}")
            logger.error(f"服务器启动失败: {e}")
        finally:
            self._cleanup()
    
    def _handle_client(self, client_socket: socket.socket, client_addr: str):
        """处理客户端连接"""
        buffer = ""
        
        try:
            client_socket.settimeout(None)
            
            while self._running:
                try:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    
                    buffer += data.decode('utf-8')
                    
                    # 处理可能的多条消息（以换行符分隔）
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            response = self._process_message(line, client_addr)
                            # 发送响应
                            try:
                                client_socket.sendall((response + '\n').encode('utf-8'))
                            except:
                                pass
                                
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"处理客户端数据错误 [{client_addr}]: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"客户端处理错误 [{client_addr}]: {e}")
        finally:
            self._disconnect_client(client_addr)
    
    def _process_message(self, message: str, client_addr: str) -> str:
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            action = data.get("action", "")
            params = data.get("params", {})
            
            if not action:
                return json.dumps({
                    "success": False,
                    "error": "缺少 action 字段"
                }, ensure_ascii=False)
            
            # 发射信号，由主线程处理
            self.command_received.emit(action, params)
            
            return json.dumps({
                "success": True,
                "action": action,
                "message": f"命令 '{action}' 已接收"
            }, ensure_ascii=False)
            
        except json.JSONDecodeError as e:
            return json.dumps({
                "success": False,
                "error": f"JSON 解析错误: {e}"
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"处理错误: {e}"
            }, ensure_ascii=False)
    
    def _disconnect_client(self, client_addr: str):
        """断开客户端连接"""
        with self._lock:
            if client_addr in self._clients:
                try:
                    self._clients[client_addr].close()
                except:
                    pass
                del self._clients[client_addr]
        
        self.client_disconnected.emit(client_addr)
        logger.info(f"客户端断开: {client_addr}")
    
    def _cleanup(self):
        """清理资源"""
        with self._lock:
            for addr, sock in list(self._clients.items()):
                try:
                    sock.close()
                except:
                    pass
            self._clients.clear()
        
        if self._server_socket:
            try:
                self._server_socket.close()
            except:
                pass
            self._server_socket = None
        
        logger.info("网络服务器已关闭")
    
    def stop(self):
        """停止服务器"""
        self._running = False
        self.wait(2000)  # 等待最多 2 秒
    
    def broadcast(self, message: dict):
        """向所有客户端广播消息"""
        msg_str = json.dumps(message, ensure_ascii=False) + '\n'
        msg_bytes = msg_str.encode('utf-8')
        
        with self._lock:
            for addr, sock in list(self._clients.items()):
                try:
                    sock.sendall(msg_bytes)
                except:
                    pass


class NetworkController(QObject):
    """
    网络控制器 - 管理网络服务和命令处理
    
    使用方式:
        controller = NetworkController(main_window)
        controller.start()
    """
    
    # 信号定义 - 用于与主窗口通信
    show_window_requested = Signal()
    hide_window_requested = Signal()
    show_bubble_requested = Signal(str, dict)  # text, params
    change_model_requested = Signal(str)  # model_name
    set_topmost_requested = Signal(bool)  # enabled
    set_movable_requested = Signal(bool)  # enabled
    move_window_requested = Signal(int, int)  # x, y
    reset_position_requested = Signal()
    quit_requested = Signal()
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9527, parent=None):
        super().__init__(parent)
        self.host = host
        self.port = port
        self._server: Optional[NetworkServerThread] = None
        
        # 命令处理器映射
        self._handlers: Dict[str, Callable] = {
            NetworkCommand.SHOW_WINDOW: self._handle_show_window,
            NetworkCommand.HIDE_WINDOW: self._handle_hide_window,
            NetworkCommand.SHOW_BUBBLE: self._handle_show_bubble,
            NetworkCommand.CHANGE_MODEL: self._handle_change_model,
            NetworkCommand.SET_TOPMOST: self._handle_set_topmost,
            NetworkCommand.SET_MOVABLE: self._handle_set_movable,
            NetworkCommand.MOVE_WINDOW: self._handle_move_window,
            NetworkCommand.RESET_POSITION: self._handle_reset_position,
            NetworkCommand.GET_STATUS: self._handle_get_status,
            NetworkCommand.GET_MODELS: self._handle_get_models,
            NetworkCommand.QUIT: self._handle_quit,
        }
    
    def start(self):
        """启动网络服务"""
        if self._server and self._server.isRunning():
            logger.warning("网络服务已在运行")
            return
        
        self._server = NetworkServerThread(self.host, self.port, self)
        self._server.command_received.connect(self._on_command_received)
        self._server.client_connected.connect(self._on_client_connected)
        self._server.client_disconnected.connect(self._on_client_disconnected)
        self._server.error_occurred.connect(self._on_error)
        self._server.start()
        
        logger.info(f"网络控制器已启动 - {self.host}:{self.port}")
    
    def stop(self):
        """停止网络服务"""
        if self._server:
            self._server.stop()
            self._server = None
            logger.info("网络控制器已停止")
    
    def _on_command_received(self, action: str, params: dict):
        """处理接收到的命令"""
        handler = self._handlers.get(action)
        if handler:
            try:
                handler(params)
                logger.info(f"执行命令: {action}, 参数: {params}")
            except Exception as e:
                logger.error(f"命令执行失败 [{action}]: {e}")
        else:
            logger.warning(f"未知命令: {action}")
    
    def _on_client_connected(self, address: str):
        """客户端连接事件"""
        logger.info(f"客户端已连接: {address}")
    
    def _on_client_disconnected(self, address: str):
        """客户端断开事件"""
        logger.info(f"客户端已断开: {address}")
    
    def _on_error(self, error: str):
        """错误事件"""
        logger.error(f"网络错误: {error}")
    
    # 命令处理方法
    def _handle_show_window(self, params: dict):
        """处理显示窗口命令"""
        self.show_window_requested.emit()
    
    def _handle_hide_window(self, params: dict):
        """处理隐藏窗口命令"""
        self.hide_window_requested.emit()
    
    def _handle_show_bubble(self, params: dict):
        """处理显示气泡文字命令"""
        text = params.get("text", "")
        if text:
            self.show_bubble_requested.emit(text, params)
    
    def _handle_change_model(self, params: dict):
        """处理切换模型命令"""
        model_name = params.get("model_name", "")
        if model_name:
            self.change_model_requested.emit(model_name)
    
    def _handle_set_topmost(self, params: dict):
        """处理设置置顶命令"""
        enabled = params.get("enabled", True)
        self.set_topmost_requested.emit(bool(enabled))
    
    def _handle_set_movable(self, params: dict):
        """处理设置可移动命令"""
        enabled = params.get("enabled", True)
        self.set_movable_requested.emit(bool(enabled))
    
    def _handle_move_window(self, params: dict):
        """处理移动窗口命令"""
        x = params.get("x")
        y = params.get("y")
        if x is not None and y is not None:
            self.move_window_requested.emit(int(x), int(y))
    
    def _handle_reset_position(self, params: dict):
        """处理重置窗口位置命令"""
        self.reset_position_requested.emit()
    
    def _handle_get_status(self, params: dict):
        """处理获取状态命令"""
        from G import G
        status = {
            "window_topmost": G.config.get("window_topmost", False),
            "window_movable": G.config.get("window_movable", True),
            "window_x": G.config.get("window_x"),
            "window_y": G.config.get("window_y"),
            "current_model": G.config.get("current_model", ""),
        }
        # 广播状态信息
        if self._server:
            self._server.broadcast({
                "type": "status",
                "data": status
            })
    
    def _handle_get_models(self, params: dict):
        """处理获取模型列表命令"""
        from G import G
        models = G.config.get_available_models()
        # 广播模型列表
        if self._server:
            self._server.broadcast({
                "type": "models",
                "data": models
            })
    
    def _handle_quit(self, params: dict):
        """处理退出命令"""
        self.quit_requested.emit()


# ============= 客户端工具类（用于测试和外部调用）=============

class NetworkClient:
    """
    网络客户端 - 用于远程控制窗口
    
    使用方式:
        client = NetworkClient()
        client.connect()
        client.show_bubble("Hello, World!")
        client.close()
    """
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9527):
        self.host = host
        self.port = port
        self._socket: Optional[socket.socket] = None
    
    def connect(self) -> bool:
        """连接到服务器"""
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self.host, self.port))
            self._socket.settimeout(5.0)
            logger.info(f"已连接到服务器: {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"连接失败: {e}")
            return False
    
    def close(self):
        """关闭连接"""
        if self._socket:
            try:
                self._socket.close()
            except:
                pass
            self._socket = None
    
    def send_command(self, action: str, params: dict = None) -> dict:
        """发送命令并获取响应"""
        if not self._socket:
            return {"success": False, "error": "未连接到服务器"}
        
        try:
            command = {
                "action": action,
                "params": params or {}
            }
            message = json.dumps(command, ensure_ascii=False) + '\n'
            self._socket.sendall(message.encode('utf-8'))
            
            # 接收响应
            response = b""
            while True:
                chunk = self._socket.recv(4096)
                if not chunk:
                    break
                response += chunk
                if b'\n' in response:
                    break
            
            if response:
                return json.loads(response.decode('utf-8').strip())
            return {"success": False, "error": "无响应"}
            
        except socket.timeout:
            return {"success": False, "error": "超时"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # 便捷方法
    def show_window(self) -> dict:
        """显示窗口"""
        return self.send_command(NetworkCommand.SHOW_WINDOW)
    
    def hide_window(self) -> dict:
        """隐藏窗口"""
        return self.send_command(NetworkCommand.HIDE_WINDOW)
    
    def show_bubble(self, text: str, x: int = None, y: int = None, 
                    duration: int = 2000, typing_speed: int = 50, 
                    max_width: int = 200) -> dict:
        """显示气泡文字"""
        params = {"text": text}
        if x is not None:
            params["x"] = x
        if y is not None:
            params["y"] = y
        params["duration"] = duration
        params["typing_speed"] = typing_speed
        params["max_width"] = max_width
        return self.send_command(NetworkCommand.SHOW_BUBBLE, params)
    
    def change_model(self, model_name: str) -> dict:
        """切换模型"""
        return self.send_command(NetworkCommand.CHANGE_MODEL, {"model_name": model_name})
    
    def set_topmost(self, enabled: bool) -> dict:
        """设置置顶"""
        return self.send_command(NetworkCommand.SET_TOPMOST, {"enabled": enabled})
    
    def set_movable(self, enabled: bool) -> dict:
        """设置可移动"""
        return self.send_command(NetworkCommand.SET_MOVABLE, {"enabled": enabled})
    
    def move_window(self, x: int, y: int) -> dict:
        """移动窗口"""
        return self.send_command(NetworkCommand.MOVE_WINDOW, {"x": x, "y": y})
    
    def reset_position(self) -> dict:
        """重置窗口位置"""
        return self.send_command(NetworkCommand.RESET_POSITION)
    
    def get_status(self) -> dict:
        """获取状态"""
        return self.send_command(NetworkCommand.GET_STATUS)
    
    def get_models(self) -> dict:
        """获取模型列表"""
        return self.send_command(NetworkCommand.GET_MODELS)
    
    def quit(self) -> dict:
        """退出程序"""
        return self.send_command(NetworkCommand.QUIT)


# ============= 测试代码 =============

if __name__ == "__main__":
    import time
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "client":
        # 客户端测试模式
        print("=== 客户端测试模式 ===")
        client = NetworkClient()
        
        if client.connect():
            print("连接成功!")
            
            # 测试各种命令
            print("\n发送 show_bubble 命令...")
            result = client.show_bubble("Hello from network client!", duration=3000)
            print(f"响应: {result}")
            
            time.sleep(1)
            
            print("\n发送 get_status 命令...")
            result = client.get_status()
            print(f"响应: {result}")
            
            print("\n发送 get_models 命令...")
            result = client.get_models()
            print(f"响应: {result}")
            
            client.close()
        else:
            print("连接失败!")
    else:
        print("=== 网络模块 ===")
        print("使用方式:")
        print("  服务端: 在 main.py 中集成 NetworkController")
        print("  客户端: python network.py client")
        print("\n支持的命令:")
        for cmd in dir(NetworkCommand):
            if not cmd.startswith('_'):
                print(f"  - {getattr(NetworkCommand, cmd)}")
