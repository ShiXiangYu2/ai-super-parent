#!/usr/bin/env bash
set -euo pipefail

# ═══════════════════════════════════════════════════════════════
# 超级家长 AI — 一键 Demo 启动脚本
# ═══════════════════════════════════════════════════════════════
# 用法:
#   bash demo.sh              # 启动 Demo（默认端口 8000）
#   bash demo.sh --port 8080  # 指定端口
#   bash demo.sh --seed-only  # 只生成数据，不启动服务器
#   bash demo.sh --tour       # 启动后打开多步演示引导
# ═══════════════════════════════════════════════════════════════

cd "$(dirname "$0")"
PORT=8000
SEED_ONLY=false
TOUR=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --port) PORT="$2"; shift 2 ;;
        --seed-only) SEED_ONLY=true; shift ;;
        --tour) TOUR=true; shift ;;
        *) echo "未知参数: $1"; exit 1 ;;
    esac
done

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║        🌟  超级家长 AI  —  产品 Demo                   ║"
echo "║        B2B SaaS 家校共育智能平台                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── 检查 Python ──
PYTHON=""
for cmd in python3.12 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PYTHON="$cmd"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "❌ 未找到 Python 3.12+，请先安装: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python: $($PYTHON --version)"

# ── 创建/激活 venv ──
if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    $PYTHON -m venv .venv
fi

source .venv/bin/activate
echo "✅ 虚拟环境已激活"

# ── 安装依赖 ──
echo "📦 安装依赖..."
pip install -q -r requirements.txt 2>/dev/null
echo "✅ 依赖已安装"

# ── 清理旧数据，生成全新 Demo 数据 ──
DB_PATH="${DB_PATH:-data/app.db}"
rm -f "$DB_PATH"
echo "🗑️  已清理旧数据库"

echo "🌱 生成 Demo 数据..."
$PYTHON scripts/demo_seed.py

if [ "$SEED_ONLY" = true ]; then
    echo ""
    echo "✅ 数据生成完毕。运行以下命令启动服务:"
    echo "   uvicorn src.api.main:app --reload --port $PORT"
    exit 0
fi

# ── 启动服务器 ──
echo ""
echo "🚀 启动服务器 (端口 $PORT)..."

# 检查端口占用
if lsof -i :$PORT &>/dev/null 2>&1; then
    echo "⚠️  端口 $PORT 已被占用，尝试使用 $((PORT + 1))"
    PORT=$((PORT + 1))
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  🎯 Demo 已就绪!                                       ║"
echo "║                                                         ║"
echo "║  🌐 打开浏览器访问:                                     ║"
echo "║     http://localhost:${PORT}                             ║"
echo "║                                                         ║"
echo "║  📋 演示账号:                                           ║"
echo "║  ┌─────────────────────────────────────────────────┐   ║"
echo "║  │ 👑 平台管理员  │ admin@demo.com  │ admin123    │   ║"
echo "║  │ 👨‍🏫 教师       │ teacher@demo.com│ teacher123  │   ║"
echo "║  │ 👪 家长1       │ parent@demo.com │ parent123   │   ║"
echo "║  │ 👪 家长2       │ parent2@demo.com│ parent123   │   ║"
echo "║  │ 👪 家长3       │ parent3@demo.com│ parent123   │   ║"
echo "║  └─────────────────────────────────────────────────┘   ║"
echo "║                                                         ║"
echo "║  💡 提示: 用家长账号登录体验 AI 育儿问答和成长报告      ║"
echo "║           用管理员账号体验多机构管理后台                 ║"
echo "║           用教师账号体验评语辅助和班级管理               ║"
echo "║                                                         ║"
echo "║  ⌨️  按 Ctrl+C 停止服务器                               ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

uvicorn src.api.main:app --host 0.0.0.0 --port "$PORT" --reload
