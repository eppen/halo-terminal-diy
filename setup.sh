#!/bin/bash

# Halo Terminal DIY 安装脚本
# 版本: 1.0.0

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目信息
PROJECT_NAME="DIY Halo Terminal"
VERSION="1.0.0"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                 $PROJECT_NAME 安装脚本                 ║"
    echo "║                         v$VERSION                         ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
}

print_step() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

check_platform() {
    print_step "检查系统平台..."

    case "$(uname -s)" in
        Darwin)
            OS="macOS"
            print_success "检测到: macOS"
            ;;
        Linux)
            OS="Linux"
            print_success "检测到: Linux"
            ;;
        CYGWIN*|MINGW32*|MSYS*|MINGW*)
            OS="Windows"
            print_error "Windows暂不完全支持，可能需要手动配置"
            exit 1
            ;;
        *)
            OS="其他"
            print_warning "未知操作系统，可能无法正常工作"
            ;;
    esac
}

check_python() {
    print_step "检查Python环境..."

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION 已安装"
    else
        print_error "Python3 未安装"
        echo "请安装 Python3:"
        if [ "$OS" = "macOS" ]; then
            echo "  1. 访问 https://www.python.org/downloads/"
            echo "  2. 或使用 Homebrew: brew install python"
        elif [ "$OS" = "Linux" ]; then
            echo "  使用包管理器安装:"
            echo "    Ubuntu/Debian: sudo apt install python3 python3-pip"
            echo "    Fedora: sudo dnf install python3 python3-pip"
            echo "    Arch: sudo pacman -S python python-pip"
        fi
        exit 1
    fi
}

check_arduino() {
    print_step "检查Arduino环境..."

    # 检查是否已安装Arduino IDE
    if [ "$OS" = "macOS" ]; then
        if [ -d "/Applications/Arduino.app" ]; then
            print_success "Arduino IDE 已安装"
        else
            print_warning "Arduino IDE 未安装"
            echo "建议安装Arduino IDE用于上传代码:"
            echo "  1. 访问 https://www.arduino.cc/en/software"
            echo "  2. 下载并安装Arduino IDE"
        fi
    else
        print_warning "请确保已安装Arduino IDE"
    fi

    # 检查串口权限
    if [ "$OS" = "Linux" ]; then
        if groups $USER | grep -q "dialout"; then
            print_success "用户已在 dialout 组中"
        else
            print_warning "用户不在 dialout 组中，可能需要手动添加:"
            echo "  sudo usermod -a -G dialout $USER"
            echo "  然后重新登录"
        fi
    fi
}

install_python_deps() {
    print_step "安装Python依赖..."

    cd "$PROJECT_DIR/python"

    if pip install -r requirements.txt; then
        print_success "Python依赖安装完成"
    else
        print_error "Python依赖安装失败"
        echo "尝试使用pip3:"
        if pip3 install -r requirements.txt; then
            print_success "Python依赖安装完成"
        else
            print_error "请手动安装: pip install pyserial"
            exit 1
        fi
    fi

    cd "$PROJECT_DIR"
}

make_executable() {
    print_step "设置脚本执行权限..."

    chmod +x "$PROJECT_DIR/python/halo_controller.py"
    chmod +x "$PROJECT_DIR/python/halo_hook.py"
    chmod +x "$PROJECT_DIR/test/test_halo.py"

    print_success "脚本权限设置完成"
}

test_installation() {
    print_step "测试安装..."

    echo -e "${YELLOW}运行测试脚本（调试模式）...${NC}"
    if python3 "$PROJECT_DIR/test/test_halo.py"; then
        print_success "测试完成"
    else
        print_warning "测试过程中出现警告，但安装可能仍然可用"
    fi
}

configure_claude_code() {
    print_step "配置Claude Code钩子..."

    HOOKS_FILE="$HOME/.claude/settings.json"
    EXAMPLE_FILE="$PROJECT_DIR/docs/claude_hooks_example.json"

    if [ ! -f "$HOOKS_FILE" ]; then
        print_warning "Claude Code配置文件不存在: $HOOKS_FILE"
        echo "请先运行Claude Code创建配置文件"
        return
    fi

    echo -e "${YELLOW}当前Claude Code钩子配置示例:${NC}"
    echo "  文件位置: $EXAMPLE_FILE"
    echo ""
    echo -e "${YELLOW}如何配置:${NC}"
    echo "  1. 打开 $HOOKS_FILE"
    echo "  2. 添加或修改 'hooks' 部分"
    echo "  3. 参考 $EXAMPLE_FILE 中的配置"
    echo "  4. 确保路径正确: $PROJECT_DIR/python/halo_hook.py"
    echo ""
    echo -e "${YELLOW}测试钩子:${NC}"
    echo "  echo '{\"event\":\"SessionStart\"}' | python3 $PROJECT_DIR/python/halo_hook.py"
}

show_next_steps() {
    echo ""
    echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}                  安装完成！🎉                      ${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}下一步操作:${NC}"
    echo ""
    echo "1. 🔌 硬件搭建:"
    echo "   参考 $PROJECT_DIR/docs/wiring.md"
    echo "   连接Arduino和RGB LED"
    echo ""
    echo "2. ⬆️  Arduino代码上传:"
    echo "   打开 $PROJECT_DIR/arduino/halo_terminal.ino"
    echo "   使用Arduino IDE上传到开发板"
    echo ""
    echo "3. 🔧 Claude Code配置:"
    echo "   编辑 ~/.claude/settings.json"
    echo "   添加钩子配置（参考 docs/claude_hooks_example.json）"
    echo ""
    echo "4. 🧪 测试系统:"
    echo "   python3 $PROJECT_DIR/test/test_halo.py"
    echo "   或手动测试: python3 python/halo_controller.py --state idle"
    echo ""
    echo "5. 🚀 开始使用:"
    echo "   启动Claude Code，LED会自动响应状态变化"
    echo ""
    echo -e "${YELLOW}常用命令:${NC}"
    echo "  # 测试所有功能"
    echo "  python3 test/test_halo.py"
    echo ""
    echo "  # 手动控制LED"
    echo "  python3 python/halo_controller.py --state thinking"
    echo "  python3 python/halo_controller.py --color 255,0,0"
    echo "  python3 python/halo_controller.py --test"
    echo ""
    echo "  # 调试模式（不连接硬件）"
    echo "  python3 python/halo_controller.py --debug --state input"
    echo ""
    echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}           祝您使用愉快！如有问题请查看README.md         ${NC}"
    echo -e "${BLUE}══════════════════════════════════════════════════════════${NC}"
}

main() {
    print_header

    print_step "开始安装 $PROJECT_NAME..."
    echo "项目目录: $PROJECT_DIR"
    echo ""

    # 执行安装步骤
    check_platform
    echo ""

    check_python
    echo ""

    check_arduino
    echo ""

    install_python_deps
    echo ""

    make_executable
    echo ""

    test_installation
    echo ""

    configure_claude_code
    echo ""

    show_next_steps
}

# 运行主函数
main "$@"