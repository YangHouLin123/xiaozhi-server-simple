import asyncio
import websockets
import sys
import json

async def connect_to_server(uri):
    """连接到WebSocket服务器"""
    try:
        async with websockets.connect(uri) as websocket:
            print(f"已连接到服务器: {uri}")
            
            # 发送hello消息进行握手
            hello_msg = json.dumps({"type": "hello"})
            await websocket.send(hello_msg)
            print("已发送握手消息")
            
            # 创建接收消息的任务
            receive_task = asyncio.create_task(receive_messages(websocket))
            
            print("输入文本消息与AI对话，输入特殊命令：")
            print("- 'exit': 退出程序")
            print("- '/abort': 中止当前对话")
            
            # 发送消息循环
            while True:
                message = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: input(">> ")
                )
                
                if message.lower() == 'exit':
                    break
                elif message.lower() == '/abort':
                    await websocket.send(json.dumps({"type": "abort"}))
                    continue
                
                # 使用listen类型的消息，这是服务器能处理的格式
                json_message = json.dumps({
                    "type": "listen", 
                    "state": "detect", 
                    "text": message
                })
                await websocket.send(json_message)
            
            # 取消接收任务
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                pass
                
    except websockets.exceptions.ConnectionClosed:
        print("与服务器的连接已关闭")
    except Exception as e:
        print(f"连接错误: {str(e)}")

async def receive_messages(websocket):
    """接收并显示服务器消息"""
    try:
        async for message in websocket:
            # 解析JSON消息
            try:
                data = json.loads(message)
                if "type" in data:
                    if data["type"] == "text" and "content" in data:
                        # 处理流式输出
                        if "stream" in data:
                            if data["stream"]:
                                # 流式输出中，不换行，直接输出内容
                                print(f"{data['content']}", end="", flush=True)
                            else:
                                # 流式输出结束，换行并显示提示符
                                print("\n>> ", end="", flush=True)
                        else:
                            # 兼容旧格式，完整显示内容
                            print(f"AI: {data['content']}")
                            print(">> ", end="", flush=True)
                    elif data["type"] == "audio":
                        print(f"\n[收到音频数据]")
                        print(">> ", end="", flush=True)
                    elif data["type"] == "hello":
                        print(f"\n[服务器握手]: 会话ID: {data.get('session_id', '未知')}")
                        print(">> ", end="", flush=True)
                    elif data["type"] == "iot":
                        print(f"\n[IoT状态更新]: {data}")
                        print(">> ", end="", flush=True)
                    else:
                        print(f"\n[收到消息]: {data}")
                        print(">> ", end="", flush=True)
                else:
                    print(f"\n[收到未知格式消息]: {data}")
                    print(">> ", end="", flush=True)
            except json.JSONDecodeError:
                print(f"\n[原始消息]: {message}")
                print(">> ", end="", flush=True)
    except asyncio.CancelledError:
        # 任务被取消时正常退出
        pass
    except Exception as e:
        print(f"\n接收消息错误: {str(e)}")
        print(">> ", end="", flush=True)

def main():
    # 默认连接本地服务器
    host = "192.168.1.127"
    port = 8000
    
    # 允许从命令行参数指定服务器地址和端口
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    
    uri = f"ws://{host}:{port}"
    print(f"正在连接到服务器: {uri}")
    
    try:
        asyncio.run(connect_to_server(uri))
    except KeyboardInterrupt:
        print("程序已手动终止")

if __name__ == "__main__":
    main()