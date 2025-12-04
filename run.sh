#!/bin/bash

# TW Stocker 完整執行腳本
# 自動啟動虛擬環境並依序執行 download → update → recommend

set -e  # 若任一命令失敗則停止執行

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 檢查虛擬環境是否存在
if [ ! -d ".venv" ]; then
    echo "❌ 虛擬環境不存在，請先執行："
    echo "   python3.12 -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# 啟動虛擬環境
echo "🔧 啟動虛擬環境..."
source .venv/bin/activate

echo "✅ 虛擬環境已啟動"
echo ""

# 執行 download（可選，首次使用或需要完整更新時執行）
# 預設註解，若要執行請取消下方註解
# echo "📥 開始下載股票資料（首次執行或重新初始化）..."
# python main.py download
# echo "✅ 下載完成"
# echo ""

# 執行 update
echo "🔄 開始更新股票資料..."
python main.py update
echo "✅ 資料更新完成"
echo ""

# 執行 recommend
echo "📊 開始產生推薦報表..."
python main.py recommend
echo "✅ 報表產生完成，輸出至 stock_report.html"
echo ""

echo "🎉 所有操作完成！"
echo "   報表位置：$(pwd)/stock_report.html"
