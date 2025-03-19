# xiaozhi-server-simple

一个基于WebSocket的简易AI对话服务器，支持与大语言模型进行文本对话。

## 项目介绍

`xiaozhi-server-simple`是一个轻量级的WebSocket服务器，用于连接客户端与大语言模型(LLM)，实现简单的AI对话功能。服务器接收客户端发送的文本消息，将其转发给配置的LLM模型，然后以流式方式将AI的回复返回给客户端。

## 功能特点

- 基于WebSocket协议的实时通信
- 支持流式输出AI回复
- 简单的握手认证机制
- 支持多种LLM模型配置
- 跨平台支持(Windows/Linux/macOS)
- 简洁的命令行客户端示例

## 安装步骤

### 环境要求

- Python 3.8+

### 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖包括：
- ruamel.yaml==0.18.10
- websockets==14.2
- openai==1.61.0
- loguru==0.7.3

## 配置说明

### 配置文件

项目使用YAML格式的配置文件。默认配置文件为`config.yaml`，您也可以创建`data/.config.yaml`作为私有配置文件（推荐用于存储API密钥等敏感信息）。

### 基本配置项

```yaml
# 服务器基础配置
server:
  # 服务器监听地址和端口
  ip: 0.0.0.0  # 监听所有网络接口
  port: 8000   # 监听端口
  # 认证配置
  auth:
    enabled: false  # 是否启用认证
    tokens:         # 设备token列表
      - token: "your-token1"
        name: "your-device-name1"

# 日志配置
log:
  log_level: INFO
  log_dir: tmp
  log_file: "server.log"

# LLM模型配置
selected_module:
  LLM: "openai"  # 选择使用的LLM模块

LLM:
  openai:
    type: "openai"
    api_key: "your-api-key"  # OpenAI API密钥
    model: "gpt-3.5-turbo"   # 使用的模型
    temperature: 0.7
    max_tokens: 2000
```

## 使用方法

### 启动服务器

```bash
python app_simple.py
```

服务器将在配置的IP和端口上启动WebSocket服务。

### 使用客户端

项目提供了一个简单的命令行客户端示例：

```bash
python simple_client.py [host] [port]
```

默认连接本地服务器（127.0.0.1:8000）。您可以指定服务器地址和端口作为命令行参数。

#### 客户端命令

- 输入文本消息与AI对话
- 输入`exit`退出程序
- 输入`/abort`中止当前对话

## 开发说明

### 项目结构

```
.
├── app_simple.py              # 服务器入口文件
├── simple_websocket_server.py # WebSocket服务器实现
├── simple_client.py           # 命令行客户端示例
├── config/                    # 配置相关
│   ├── logger.py              # 日志配置
│   └── settings.py            # 配置加载
├── core/                      # 核心功能
│   ├── providers/             # 服务提供者
│   │   └── llm/              # LLM模型实现
│   └── utils/                 # 工具函数
│       ├── llm.py            # LLM工厂类
│       └── util.py           # 通用工具函数
├── data/                      # 数据目录
│   └── .config.yaml           # 私有配置文件
└── requirements.txt           # 依赖列表
```

### 自定义LLM模型

您可以通过扩展`core/providers/llm/`目录下的模块来添加对新LLM模型的支持。

## 许可证

[MIT License](LICENSE)
