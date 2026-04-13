#!/usr/bin/env python3
"""
Halo Terminal 控制器
通过串口控制Arduino RGB LED
"""

import serial
import sys
import json
import time
import os
import glob
from pathlib import Path

class HaloController:
    def __init__(self, port=None, baudrate=9600):
        """初始化串口连接"""
        self.port = port
        self.baudrate = baudrate
        self.ser = None

        # 如果没有指定端口，自动检测
        if not port:
            self.port = self.detect_arduino_port()

        if self.port:
            self.connect()
        else:
            print("⚠️  未检测到Arduino设备，将在控制台模拟输出")

    def detect_arduino_port(self):
        """自动检测Arduino串口"""
        import platform
        system = platform.system()

        if system == "Darwin":  # macOS
            possible_ports = [
                "/dev/cu.usbmodem*",
                "/dev/cu.usbserial*",
                "/dev/tty.usbmodem*",
                "/dev/tty.usbserial*"
            ]
        elif system == "Linux":
            possible_ports = [
                "/dev/ttyACM*",
                "/dev/ttyUSB*"
            ]
        elif system == "Windows":
            possible_ports = [
                "COM3", "COM4", "COM5", "COM6", "COM7", "COM8"
            ]
        else:
            return None

        for pattern in possible_ports:
            ports = glob.glob(pattern)
            if ports:
                # 选择第一个检测到的端口
                return ports[0]

        return None

    def connect(self):
        """连接串口"""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # 等待Arduino重置
            print(f"✅ 已连接到 {self.port}")
            return True
        except Exception as e:
            print(f"❌ 连接失败: {e}")
            self.ser = None
            return False

    def send_command(self, command):
        """发送命令到Arduino"""
        if not self.ser:
            # 模拟模式
            print(f"📤 [模拟] 发送命令: {command}")
            return True

        try:
            self.ser.write(f"{command}\n".encode('utf-8'))
            self.ser.flush()
            print(f"📤 发送命令: {command}")
            return True
        except Exception as e:
            print(f"❌ 发送失败: {e}")
            return False

    def set_state(self, state):
        """设置状态"""
        states = {
            "idle": "idle",        # 蓝色
            "thinking": "thinking", # 黄色
            "input": "input",      # 红色
            "error": "error"       # 紫色
        }

        if state in states:
            return self.send_command(states[state])
        else:
            print(f"❌ 未知状态: {state}")
            return False

    def set_color(self, r, g, b):
        """设置自定义颜色"""
        return self.send_command(f"rgb:{r},{g},{b}")

    def test_sequence(self):
        """运行测试序列"""
        return self.send_command("test")

    def breathing_effect(self):
        """运行呼吸灯效果"""
        return self.send_command("breathing")

    def close(self):
        """关闭串口"""
        if self.ser:
            self.ser.close()
            self.ser = None
            print("🔌 已断开串口连接")

# Claude Code钩子处理函数
def handle_claude_hook():
    """
    从stdin读取Claude Code的JSON数据
    并转换为Arduino命令
    """
    # 读取标准输入（Claude Code传递的JSON）
    if not sys.stdin.isatty():
        data = sys.stdin.read()
        if data:
            try:
                event_data = json.loads(data)
                # 解析事件类型
                event_type = event_data.get("event", "")
                print(f"📥 收到Claude事件: {event_type}")

                return event_type
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析错误: {e}")
                return "error"

    return None

def main():
    """主函数：处理Claude Code钩子调用"""
    import argparse

    parser = argparse.ArgumentParser(description='Halo Terminal Controller')
    parser.add_argument('--port', help='串口端口')
    parser.add_argument('--state', help='直接设置状态 (idle, thinking, input, error)')
    parser.add_argument('--color', help='设置颜色，格式: 255,0,0')
    parser.add_argument('--test', action='store_true', help='运行测试序列')
    parser.add_argument('--breathing', action='store_true', help='运行呼吸灯效果')
    parser.add_argument('--debug', action='store_true', help='调试模式，不连接硬件')

    args = parser.parse_args()

    # 调试模式
    if args.debug:
        print("🐛 调试模式启用，不连接硬件")
        controller = HaloController(port=None)
        controller.ser = None
    else:
        # 创建控制器
        controller = HaloController(port=args.port)

    # 处理命令行参数
    if args.state:
        controller.set_state(args.state)
    elif args.color:
        try:
            r, g, b = map(int, args.color.split(','))
            controller.set_color(r, g, b)
        except:
            print("❌ 颜色格式错误，使用 255,0,0 格式")
    elif args.test:
        controller.test_sequence()
    elif args.breathing:
        controller.breathing_effect()
    else:
        # 处理Claude Code事件
        event = handle_claude_hook()

        if event:
            # 映射Claude Code事件到LED状态
            event_mapping = {
                "SessionStart": "idle",
                "UserPromptSubmit": "thinking",
                "PreToolUse": "thinking",
                "PostToolUse": "idle",
                "idle_prompt": "input",       # 需要用户输入
                "permission_prompt": "input", # 需要权限确认
                "Stop": "idle",
                "SessionEnd": "idle",
                "error": "error",
                "Setup:init": "idle",
                "Setup:maintenance": "thinking",
                "SubagentStart": "thinking",
                "SubagentStop": "idle",
                "PreCompact:manual": "thinking",
                "PreCompact:auto": "thinking",
                "PermissionRequest": "input"
            }

            state = event_mapping.get(event, "idle")

            # 发送状态命令
            controller.set_state(state)
        else:
            print("📝 使用方法:")
            print("  作为Claude Code钩子: 从stdin接收JSON事件")
            print("  命令行模式:")
            print("    --state idle|thinking|input|error  设置状态")
            print("    --color 255,0,0                    设置自定义颜色")
            print("    --test                            运行测试序列")
            print("    --breathing                       呼吸灯效果")
            print("    --debug                           调试模式（不连接硬件）")
            print("    --port /dev/ttyUSB0               指定串口端口")

    # 保持连接短暂时间后关闭
    time.sleep(0.5)
    controller.close()

if __name__ == "__main__":
    main()