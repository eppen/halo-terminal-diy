# DIY Halo Terminal

用Arduino DIY一个物理状态灯，当Claude Code需要你输入时亮灯提醒！

## ✨ 功能特性

- **状态可视化**: 用RGB LED显示Claude Code的工作状态
  - 🔵 蓝色: 空闲，等待输入
  - 🟡 黄色: 正在思考/处理
  - 🔴 红色: 需要用户输入/确认
  - 🟣 紫色: 错误状态
- **智能提醒**: 通过USB串口实时接收Claude Code状态变化
- **呼吸灯效果**: 需要输入时红色LED会闪烁提醒
- **电位器调亮度**（可选）: 模拟口 A0 接电位器，统一调节所有状态与颜色的明暗
- **完全开源**: 代码完全开放，可自由修改扩展
- **跨平台**: 支持macOS、Linux、Windows

## 📦 所需材料


| 组件         | 数量  | 说明           |
| ---------- | --- | ------------ |
| Arduino开发板 | 1   | UNO、Nano或类似  |
| RGB LED灯   | 1   | 共阳极或共阴极      |
| 220Ω电阻     | 3   | 限流电阻         |
| 面包板        | 1   | 用于电路搭建       |
| 杜邦线        | 若干  | 连接线          |
| USB数据线     | 1   | 连接电脑和Arduino |
| 电位器（线性，如 10kΩ） | 0–1 | 可选，接 A0 调节整体亮度 |


## 🔧 硬件连接

### 接线图（共阳极RGB LED）

```
Arduino      RGB LED
 9 (PWM)  →  R (红色引脚)
10 (PWM)  →  G (绿色引脚)
11 (PWM)  →  B (蓝色引脚)
5V        →  公共阳极 (+)
```

### 接线图（共阴极RGB LED）

```
Arduino      RGB LED
 9 (PWM)  →  R (红色引脚)
10 (PWM)  →  G (绿色引脚)
11 (PWM)  →  B (蓝色引脚)
GND       →  公共阴极 (-)
```

**注意**: 

- 每个LED引脚都需要串联220Ω电阻
- 如果使用不同引脚，需修改Arduino代码中的引脚定义
- 使用亮度电位器时：外侧两脚接 5V 与 GND，中间脚接 **A0**（详见 `docs/wiring.md` 方案四）；不接电位器时建议将 A0 接 GND 避免悬空

## 🚀 快速开始

### 1. 上传Arduino代码

1. 打开Arduino IDE
2. 打开 `arduino/halo_terminal.ino`
3. 选择正确的开发板和端口
4. 点击上传

### 2. 安装Python依赖

```bash
cd python
pip install -r requirements.txt
```

### 3. 测试连接

```bash
# 测试所有功能
python test/test_halo.py

# 或直接测试控制器
python python/halo_controller.py --debug
```

### 4. 配置Claude Code

编辑 `~/.claude/settings.json`，添加以下钩子配置：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 /绝对路径/到/halo-terminal-diy/python/halo_hook.py"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 /绝对路径/到/halo-terminal-diy/python/halo_hook.py"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 /绝对路径/到/halo-terminal-diy/python/halo_hook.py"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 /绝对路径/到/halo-terminal-diy/python/halo_hook.py"
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /绝对路径/到/halo-terminal-diy/python/halo_hook.py"
          }
        ]
      },
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /绝对路径/到/halo-terminal-diy/python/halo_hook.py"
          }
        ]
      }
    ]
  }
}
```

**注意**: 将 `/绝对路径/到/halo-terminal-diy` 替换为你的实际路径。

## 📖 使用说明

### 基本使用

1. 连接Arduino到电脑
2. 确保Python脚本有执行权限：`chmod +x python/*.py`
3. 启动Claude Code，LED会自动响应状态变化

### 手动控制

```bash
# 设置状态
python python/halo_controller.py --state idle      # 蓝色
python python/halo_controller.py --state thinking  # 黄色
python python/halo_controller.py --state input     # 红色
python python/halo_controller.py --state error     # 紫色

# 自定义颜色
python python/halo_controller.py --color 255,0,0   # 红色
python python/halo_controller.py --color 0,255,0   # 绿色
python python/halo_controller.py --color 0,0,255   # 蓝色

# 特效
python python/halo_controller.py --test           # 测试序列
python python/halo_controller.py --breathing      # 呼吸灯

# 指定串口
python python/halo_controller.py --port /dev/cu.usbmodem1101 --state idle
```

### 调试模式

如果不想连接硬件，可以使用调试模式：

```bash
python python/halo_controller.py --debug --state thinking
```

## 🎯 状态映射


| Claude Code事件     | LED状态 | 说明     |
| ----------------- | ----- | ------ |
| SessionStart      | 蓝色    | 会话开始   |
| UserPromptSubmit  | 黄色    | 用户提交提示 |
| PreToolUse        | 黄色    | 准备使用工具 |
| PostToolUse       | 蓝色    | 工具使用完成 |
| idle_prompt       | 红色    | 需要用户输入 |
| permission_prompt | 红色    | 需要权限确认 |
| SessionEnd        | 蓝色    | 会话结束   |
| 其他事件              | 蓝色    | 默认状态   |


## 🛠️ 故障排除

### LED不亮

1. 检查接线是否正确
2. 确认电阻已正确串联
3. 检查Arduino是否供电
4. 验证引脚定义是否与接线一致

### Python脚本无法连接

1. 检查串口权限：`ls -l /dev/tty.usb*`
2. 可能需要添加用户到dialout组：`sudo usermod -a -G dialout $USER`
3. 重新插拔USB线
4. 检查端口号：`python python/halo_controller.py --port /dev/ttyUSB0`

### Claude Code钩子不工作

1. 检查路径是否正确
2. 确保Python脚本有执行权限
3. 查看Claude Code日志：`tail -f ~/.claude/claude.log`
4. 测试钩子：`echo '{"event":"SessionStart"}' | python python/halo_hook.py`

## 🔧 自定义修改

### 修改LED引脚

编辑 `arduino/halo_terminal.ino`：

```cpp
#define PIN_RED 9    // 改为你的红色引脚
#define PIN_GREEN 10 // 改为你的绿色引脚
#define PIN_BLUE 11  // 改为你的蓝色引脚
```

### 添加新状态

1. 在Arduino代码中添加新状态
2. 在Python脚本中添加事件映射
3. 在Claude Code钩子中配置新事件

### 扩展功能

- 添加蜂鸣器提示音
- 添加WiFi模块远程控制
- 添加LCD屏幕显示状态文本
- 记录使用统计

## 📁 项目结构

```
halo-terminal-diy/
├── arduino/
│   └── halo_terminal.ino     # Arduino主程序
├── python/
│   ├── halo_controller.py    # 主控制器（命令行工具）
│   ├── halo_hook.py          # 简化钩子（Claude Code专用）
│   └── requirements.txt      # Python依赖
├── test/
│   └── test_halo.py          # 测试脚本
├── docs/                     # 文档和接线图
└── README.md                 # 项目说明
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送到分支：`git push origin feature/new-feature`
5. 创建Pull Request

## 📄 许可证

MIT License - 详见LICENSE文件

## 🙏 致谢

灵感来自官方Halo Terminal项目，但这是一个完全开源的DIY版本。

---

**让编程更有趣，让等待不再无聊！** 🚀