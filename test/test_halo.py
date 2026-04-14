#!/usr/bin/env python3
"""
Halo Terminal 测试脚本
用于测试Arduino LED控制和Claude Code事件模拟
"""

import subprocess
import time
import sys
import os

# 以当前文件位置推导项目根目录，避免受 cwd 影响
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PYTHON_DIR = os.path.join(PROJECT_ROOT, 'python')
ARDUINO_DIR = os.path.join(PROJECT_ROOT, 'arduino')
HALO_CONTROLLER = os.path.join(PYTHON_DIR, 'halo_controller.py')
HALO_HOOK = os.path.join(PYTHON_DIR, 'halo_hook.py')

# 添加项目路径以便导入模块
sys.path.insert(0, PYTHON_DIR)

def test_claude_events():
    """测试Claude Code事件"""
    print("🎬 开始测试Claude Code事件...")
    print("=" * 50)

    events = [
        ('SessionStart', 'idle', '🔵 蓝色 - 会话开始'),
        ('UserPromptSubmit', 'thinking', '🟡 黄色 - 用户提交提示'),
        ('PreToolUse', 'thinking', '🟡 黄色 - 准备使用工具'),
        ('idle_prompt', 'input', '🔴 红色 - 需要用户输入'),
        ('PostToolUse', 'idle', '🔵 蓝色 - 工具使用完成'),
        ('permission_prompt', 'input', '🔴 红色 - 需要权限确认'),
        ('SessionEnd', 'idle', '🔵 蓝色 - 会话结束'),
        ('error', 'error', '🟣 紫色 - 错误状态')
    ]

    for event_name, expected_state, description in events:
        print(f"\n📋 测试: {description}")
        print(f"   事件: {event_name}")
        print(f"   预期状态: {expected_state}")

        # 构建JSON数据
        json_data = f'{{"event": "{event_name}"}}'

        # 调用halo_controller.py
        result = subprocess.run(
            [sys.executable, HALO_CONTROLLER, '--debug'],
            input=json_data,
            text=True,
            capture_output=True
        )

        # 输出结果
        if result.stdout:
            print("   输出:")
            for line in result.stdout.strip().split('\n'):
                print(f"     {line}")

        if result.stderr:
            print(f"   错误: {result.stderr.strip()}")

        time.sleep(2)  # 等待LED变化

    print("\n" + "=" * 50)
    print("✅ Claude Code事件测试完成")

def test_direct_commands():
    """测试直接命令"""
    print("\n🎮 开始测试直接命令...")
    print("=" * 50)

    commands = [
        (['--state', 'idle'], '设置空闲状态（蓝色）'),
        (['--state', 'thinking'], '设置思考状态（黄色）'),
        (['--state', 'input'], '设置输入状态（红色）'),
        (['--state', 'error'], '设置错误状态（紫色）'),
        (['--color', '255,0,0'], '设置红色'),
        (['--color', '0,255,0'], '设置绿色'),
        (['--color', '0,0,255'], '设置蓝色'),
        (['--color', '255,255,0'], '设置黄色'),
        (['--test'], '运行测试序列'),
        (['--breathing'], '呼吸灯效果')
    ]

    for args, description in commands:
        print(f"\n📋 测试: {description}")
        print(f"   命令: python halo_controller.py {' '.join(args)} --debug")

        # 调用halo_controller.py
        result = subprocess.run(
            [sys.executable, HALO_CONTROLLER, '--debug'] + args,
            text=True,
            capture_output=True
        )

        # 输出结果
        if result.stdout:
            print("   输出:")
            for line in result.stdout.strip().split('\n'):
                print(f"     {line}")

        if result.stderr:
            print(f"   错误: {result.stderr.strip()}")

        time.sleep(2)  # 等待命令执行

    print("\n" + "=" * 50)
    print("✅ 直接命令测试完成")

def test_hook_performance():
    """测试钩子性能"""
    print("\n⏱️  开始测试钩子性能...")
    print("=" * 50)

    import timeit

    # 测试halo_hook.py的性能
    json_data = '{"event": "UserPromptSubmit"}'

    def run_hook():
        result = subprocess.run(
            [sys.executable, HALO_HOOK],
            input=json_data,
            text=True,
            capture_output=True,
            timeout=1
        )
        return result

    # 运行10次，计算平均时间
    times = []
    for i in range(10):
        start = time.perf_counter()
        run_hook()
        end = time.perf_counter()
        times.append(end - start)

    avg_time = sum(times) / len(times) * 1000  # 转换为毫秒

    print(f"钩子执行时间:")
    print(f"  平均: {avg_time:.2f} ms")
    print(f"  最小: {min(times)*1000:.2f} ms")
    print(f"  最大: {max(times)*1000:.2f} ms")

    print("\n" + "=" * 50)
    print("✅ 性能测试完成")

def main():
    """主测试函数"""
    print("🚀 Halo Terminal 系统测试")
    print("=" * 50)

    # 检查Python模块
    try:
        import serial
        print("✅ pyserial 已安装")
    except ImportError:
        print("❌ pyserial 未安装，运行: pip install pyserial")

    # 检查文件
    required_files = [
        (os.path.join(ARDUINO_DIR, 'halo_terminal', 'halo_terminal.ino'), 'Arduino代码'),
        (HALO_CONTROLLER, '主控制器'),
        (HALO_HOOK, '钩子脚本'),
        (os.path.join(PYTHON_DIR, 'requirements.txt'), '依赖文件'),
    ]

    for filepath, description in required_files:
        if os.path.exists(filepath):
            print(f"✅ {description}: 存在")
        else:
            print(f"❌ {description}: 缺失")

    print("\n" + "=" * 50)

    # 运行测试
    try:
        test_claude_events()
        test_direct_commands()
        test_hook_performance()

        print("\n" + "=" * 50)
        print("🎉 所有测试完成!")
        print("\n下一步:")
        print("1. 将Arduino代码上传到开发板")
        print("2. 安装Python依赖: pip install -r ../python/requirements.txt")
        print("3. 配置Claude Code钩子")
        print("4. 开始使用!")

    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()