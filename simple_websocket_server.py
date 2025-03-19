import asyncio
import websockets
import json
from datetime import datetime
from config.logger import setup_logging
from core.utils.util import get_local_ip
from core.utils import llm

TAG = __name__

class SimpleWebSocketServer:
    def __init__(self, config: dict):
        self.config = config
        self.logger = setup_logging()
        self._llm = self._create_llm_instance()
        self.active_connections = set()

    def _create_llm_instance(self):
        """创建LLM处理模块实例"""
        llm_module = self.config["selected_module"]["LLM"]
        llm_type = self.config["LLM"][llm_module].get("type", llm_module)
        return llm.create_instance(llm_type, self.config["LLM"][llm_module])

    async def start(self):
        server_config = self.config["server"]
        host = server_config["ip"]
        port = server_config["port"]

        self.logger.bind(tag=TAG).info("Server is running at ws://{}:{}", get_local_ip(), port)
        self.logger.bind(tag=TAG).info("=======上面的地址是websocket协议地址，请勿用浏览器访问=======")
        async with websockets.serve(self._handle_connection, host, port):
            await asyncio.Future()

    async def _handle_connection(self, websocket):
        """处理新连接"""
        try:
            await self._handle_messages(websocket)
        except websockets.exceptions.ConnectionClosed:
            self.logger.bind(tag=TAG).info("Client disconnected")
        except Exception as e:
            self.logger.bind(tag=TAG).error(f"Error handling connection: {str(e)}")

    async def _handle_messages(self, websocket):
        """处理WebSocket消息"""
        async for message in websocket:
            try:
                # 处理文本消息
                if isinstance(message, str):
                    data = None
                    text = message
                    message_type = "text"
                    
                    try:
                        # 尝试解析JSON消息
                        data = json.loads(message)
                        if data.get("type") == "hello":
                            # 处理握手消息
                            response = json.dumps({
                                "type": "hello",
                                "session_id": str(id(websocket))
                            })
                            await websocket.send(response)
                            continue
                        elif data.get("type") == "listen" and data.get("text"):
                            text = data["text"]
                            message_type = "listen"
                        else:
                            response = json.dumps({
                                "type": "error",
                                "content": "不支持的消息类型"
                            })
                            await websocket.send(response)
                            continue
                    except json.JSONDecodeError:
                        # 如果不是JSON格式，保持默认值
                        pass
                    
                    # 获取prompt并替换{date_time}为当前时间
                    prompt = self.config.get("prompt", "你是一个AI助手，请回答问题。")
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    prompt = prompt.replace("{date_time}", current_time)
                    
                    # 构造对话格式
                    dialogue = [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": text}
                    ]
                    
                    # 使用流式响应
                    for content in self._llm.response("", dialogue):
                        response = json.dumps({
                            "type": "text",
                            "content": content,
                            "stream": True
                        })
                        await websocket.send(response)
                        # 添加小延迟，确保流式输出更均匀
                        await asyncio.sleep(0.01)
                    
                    # 发送流式响应结束标记
                    response = json.dumps({
                        "type": "text",
                        "content": "",
                        "stream": False
                    })
                    await websocket.send(response)
            except Exception as e:
                self.logger.bind(tag=TAG).error(f"Error handling message: {str(e)}")
