#!/usr/bin/env python3
"""
简化版Halo Terminal钩子
专为Claude Code钩子设计，快速处理事件
"""

import sys
import json
import serial
import time
import os

# 默认串口配置（自动检测）
DEFAULT_PORT = None  # 自动检测
BAUDRATE = 9600

def detect_arduino_port():
    """自动检测Arduino串口"""
    import platform
    import glob

    system = platform.system()

    if system == "Darwin":  # macOS
        patterns = ["/dev/cu.usbmodem*", "/dev/tty.usbmodem*"]
    elif system == "Linux":
        patterns = ["/dev/ttyACM*", "/dev/ttyUSB*"]
    elif system == "Windows":
        # Windows需要不同处理
        return None
    else:
        return None

    for pattern in patterns:
        ports = glob.glob(pattern)
        if ports:
            return ports[0]

    return None

def send_to_arduino(command, port=None):
    """发送命令到Arduino"""
    if not port:
        port = detect_arduino_port()

    if not port:
        # 没有检测到Arduino，静默失败（避免干扰Claude Code）
        return False

    try:
        ser = serial.Serial(port, BAUDRATE, timeout=1)
        time.sleep(0.5)  # 短暂等待
        ser.write(f"{command}\n".encode('utf-8'))
        ser.flush()
        ser.close()
        return True
    except:
        # 串口操作失败，静默处理
        return False

def main():
    """主函数：处理Claude Code钩子"""
    # 读取Claude Code传递的数据
    data = sys.stdin.read()

    if not data:
        return

    try:
        event_data = json.loads(data)
        event = event_data.get("event", "")

        # 事件映射到Arduino命令
        command_map = {
            "SessionStart": "idle",
            "UserPromptSubmit": "thinking",
            "PreToolUse": "thinking",
            "PostToolUse": "idle",
            "idle_prompt": "input",
            "permission_prompt": "input",
            "Stop": "idle",
            "SessionEnd": "idle",
            "Setup:init": "idle",
            "Setup:maintenance": "thinking",
            "SubagentStart": "thinking",
            "SubagentStop": "idle",
            "PreCompact:manual": "thinking",
            "PreCompact:auto": "thinking",
            "PermissionRequest": "input"
        }

        command = command_map.get(event, "idle")

        # 发送到Arduino
        send_to_arduino(command)

    except json.JSONDecodeError:
        # JSON解析失败，静默处理
        pass
    except Exception as e:
        # 其他异常，静默处理
        pass

if __name__ == "__main__":
    main()