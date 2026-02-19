#!/usr/bin/env python3
"""
openclaw-monitor — 本地日志服务
读取 OpenClaw Gateway 日志 & 会话 JSONL，提供给监控面板使用
"""

import os
import json
import glob
import subprocess
import argparse
from http.server import HTTPServer, BaseHTTPRequestHandler

DEFAULT_PORT = 19999
DEFAULT_OPENCLAW_DIR = os.path.expanduser("~/.openclaw")


def find_openclaw_dir():
    candidates = [
        os.path.expanduser("~/.openclaw"),
        os.path.expanduser("~/Library/Application Support/openclaw"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    return candidates[0]


def get_paths(openclaw_dir):
    return {
        "gateway_log": os.path.join(openclaw_dir, "logs", "gateway.log"),
        "session_dir": os.path.join(openclaw_dir, "agents", "main", "sessions"),
    }


def get_custom_name_path(openclaw_dir):
    return os.path.join(openclaw_dir, "monitor-name.txt")


def read_agent_name(openclaw_dir):
    """
    优先级：
    1. ~/.openclaw/monitor-name.txt（用户自定义）
    2. 系统用户名
    """
    name_file = get_custom_name_path(openclaw_dir)
    if os.path.exists(name_file):
        try:
            name = open(name_file).read().strip()
            if name:
                return name
        except Exception:
            pass
    return os.environ.get("USER") or os.environ.get("USERNAME") or "My"


class MonitorHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 静默 HTTP 访问日志

    def send_cors(self, content_type="text/plain"):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_cors()

    def do_POST(self):
        if self.path == "/name":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8").strip()
            try:
                data = json.loads(body)
                name = data.get("name", "").strip()
            except Exception:
                name = body.strip()

            if name:
                name_file = get_custom_name_path(self.server.openclaw_dir)
                with open(name_file, "w", encoding="utf-8") as f:
                    f.write(name)
                self.send_cors("application/json")
                self.wfile.write(json.dumps({"ok": True, "name": name}).encode())
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        paths = get_paths(self.server.openclaw_dir)

        if self.path == "/logs":
            log_file = paths["gateway_log"]
            if not os.path.exists(log_file):
                self.send_cors()
                self.wfile.write(b"# gateway.log not found\n")
                return
            result = subprocess.run(
                ["tail", "-200", log_file], capture_output=True, text=True
            )
            self.send_cors("text/plain; charset=utf-8")
            self.wfile.write(result.stdout.encode("utf-8"))

        elif self.path == "/session":
            session_dir = paths["session_dir"]
            if not os.path.isdir(session_dir):
                self.send_cors("application/json")
                self.wfile.write(b"[]")
                return
            files = sorted(glob.glob(os.path.join(session_dir, "*.jsonl")))
            if not files:
                self.send_cors("application/json")
                self.wfile.write(b"[]")
                return
            latest = files[-1]
            result = subprocess.run(
                ["tail", "-80", latest], capture_output=True, text=True
            )
            parsed = []
            for line in result.stdout.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                try:
                    parsed.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
            self.send_cors("application/json; charset=utf-8")
            self.wfile.write(json.dumps(parsed).encode("utf-8"))

        elif self.path == "/config":
            # 返回 agent 名字等配置，供前端动态渲染标题
            agent_name = read_agent_name(self.server.openclaw_dir)
            config = {
                "agentName": agent_name,
                "displayTitle": f"{agent_name}'s Suit Monitor",
                "openclawDir": self.server.openclaw_dir,
            }
            self.send_cors("application/json; charset=utf-8")
            self.wfile.write(json.dumps(config, ensure_ascii=False).encode("utf-8"))

        elif self.path == "/" or self.path == "/index.html":
            html_path = os.path.join(os.path.dirname(__file__), "public", "index.html")
            if not os.path.exists(html_path):
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"index.html not found")
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            with open(html_path, "rb") as f:
                self.wfile.write(f.read())

        elif self.path == "/health":
            self.send_cors("application/json")
            paths_check = get_paths(self.server.openclaw_dir)
            status = {
                "ok": True,
                "openclaw_dir": self.server.openclaw_dir,
                "gateway_log_exists": os.path.exists(paths_check["gateway_log"]),
                "session_dir_exists": os.path.isdir(paths_check["session_dir"]),
                "agent_name": read_agent_name(self.server.openclaw_dir),
            }
            self.wfile.write(json.dumps(status).encode())

        else:
            self.send_response(404)
            self.end_headers()


def main():
    parser = argparse.ArgumentParser(
        description="OpenClaw Monitor — 本地日志服务器"
    )
    parser.add_argument(
        "--port", "-p", type=int, default=DEFAULT_PORT, help=f"监听端口 (默认: {DEFAULT_PORT})"
    )
    parser.add_argument(
        "--openclaw-dir", "-d", default=None, help="OpenClaw 数据目录 (默认自动检测)"
    )
    parser.add_argument(
        "--no-open", action="store_true", help="不自动打开浏览器"
    )
    args = parser.parse_args()

    openclaw_dir = args.openclaw_dir or find_openclaw_dir()
    paths = get_paths(openclaw_dir)
    agent_name = read_agent_name(openclaw_dir)

    print(f"\n🦞 OpenClaw Monitor")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"  Agent 名称:    {agent_name}")
    print(f"  OpenClaw 目录: {openclaw_dir}")
    print(f"  Gateway 日志:  {'✓' if os.path.exists(paths['gateway_log']) else '✗ 未找到'} {paths['gateway_log']}")
    print(f"  会话目录:      {'✓' if os.path.isdir(paths['session_dir']) else '✗ 未找到'} {paths['session_dir']}")
    print(f"  监控面板:      http://127.0.0.1:{args.port}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    server = HTTPServer(("127.0.0.1", args.port), MonitorHandler)
    server.openclaw_dir = openclaw_dir

    if not args.no_open:
        import threading, webbrowser, time
        def open_browser():
            time.sleep(0.8)
            webbrowser.open(f"http://127.0.0.1:{args.port}")
        threading.Thread(target=open_browser, daemon=True).start()

    print(f"  服务运行中，按 Ctrl+C 停止\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  已停止")


if __name__ == "__main__":
    main()
