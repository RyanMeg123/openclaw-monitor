# 🦞 OpenClaw Monitor

OpenClaw Gateway 实时监控面板 — 通过读取本地日志文件，实时显示 OpenClaw Agent 的工具调用、对话记录、token 用量等信息。

![预览](https://img.shields.io/badge/Python-3.7%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## 功能

- **实时日志流** — 每3秒读取 `gateway.log`，显示 tavily 搜索、API 请求等
- **对话监控** — 每2秒读取 session JSONL，捕获工具调用、用户消息、Agent 回复
- **Token 用量** — 实时显示 token 消耗和成本
- **安全预警** — Shell 调用频率过高、危险命令、文件删除等自动报警
- **工具调用记录** — 可视化展示每次工具调用及结果
- **调用频率图** — 最近60秒实时活动图表

## 快速开始

### 方式一：直接运行（推荐）

```bash
git clone https://github.com/你的用户名/openclaw-monitor.git
cd openclaw-monitor
python3 server.py
```

浏览器会自动打开 `http://127.0.0.1:19999`。

### 方式二：安装为命令行工具

```bash
git clone https://github.com/你的用户名/openclaw-monitor.git
cd openclaw-monitor
pip3 install -e .

# 之后任何地方都可以运行：
openclaw-monitor
```

## 命令行参数

```
用法: python3 server.py [选项]

选项:
  --port, -p PORT         监听端口 (默认: 19999)
  --openclaw-dir, -d DIR  OpenClaw 数据目录 (默认自动检测)
  --no-open               不自动打开浏览器
  -h, --help              显示帮助
```

示例：

```bash
# 自定义端口
python3 server.py --port 8080

# 指定 OpenClaw 目录
python3 server.py --openclaw-dir /custom/path/.openclaw

# 不自动打开浏览器
python3 server.py --no-open
```

## 系统要求

- Python 3.7+
- macOS / Linux（Windows 需要 WSL）
- 已安装并运行 [OpenClaw](https://openclaw.ai)

## 目录结构

```
openclaw-monitor/
├── server.py          # 本地 HTTP 服务器（核心）
├── public/
│   └── index.html     # 监控面板前端
├── bin/
│   └── openclaw-monitor  # 命令行入口脚本
├── setup.py           # pip 安装配置
└── README.md
```

## 工作原理

监控面板不使用 WebSocket（因为 OpenClaw Gateway 的 WebSocket 只允许一个 webchat 连接），而是通过本地 HTTP 服务器轮询读取文件：

- `GET /logs` → 读取 `~/.openclaw/logs/gateway.log` 最后200行
- `GET /session` → 读取 `~/.openclaw/agents/main/sessions/` 最新 JSONL 文件最后80行
- `GET /health` → 检查服务状态
- `GET /` → 提供监控面板 HTML

前端每2~3秒增量拉取新数据，只处理新增内容。

## 开发背景

在尝试直接连接 OpenClaw WebSocket Gateway 时，发现 Gateway 对每个客户端类型（webchat）只允许一个连接，导致监控面板和官方 webchat 互相踢掉对方。因此改用读取日志文件的方案，稳定可靠，不干扰正常使用。

## License

MIT
# openclaw-monitor
