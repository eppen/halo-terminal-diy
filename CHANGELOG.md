# Changelog

所有 notable changes 到这个项目将会被记录在这个文件。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且这个项目遵守 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2026-04-13

### 新增
- 初始版本发布
- Arduino代码：支持RGB LED状态控制
- Python控制器：命令行接口和Claude Code钩子
- 完整文档：接线指南、安装说明
- 测试脚本：全面的功能测试
- 安装脚本：自动化设置
- Claude Code钩子配置示例

### 功能
- 🔵 蓝色：空闲状态（等待输入）
- 🟡 黄色：思考状态（处理中）
- 🔴 红色：需要输入状态
- 🟣 紫色：错误状态
- 呼吸灯效果
- 测试序列
- 自定义颜色设置
- 自动串口检测
- 跨平台支持（macOS、Linux）

### 技术细节
- Arduino代码使用PWM控制RGB LED亮度
- Python脚本使用pyserial进行串口通信
- 支持共阳极和共阴极RGB LED
- 完整的错误处理和调试模式

## [0.1.0] - 2026-04-13 (开发版本)

### 新增
- 项目结构搭建
- 基础代码实现
- 初步文档

---
**注意**：这是一个DIY项目，版本号遵循语义化版本控制，但可能根据实际需求灵活调整。