# TW Stocker

每天更新的台股歷史資料庫，計算技術指標，回測然後推薦股票。  

https://voidful.github.io/tw_stocker/stock_report.html

## ⚠️ 環境要求

**Python 版本：3.12 (推薦) 或 3.13**

本專案依賴 `fta` 套件，其內部依賴 `numba` (版本限制為 0.61.x)。由於 numba 官方目前尚未支援 **Python 3.14**，若使用 Python 3.14 則安裝會失敗。請確保你的 Python 環境在 **3.12 或 3.13**。

可透過以下方式檢查 Python 版本：

```bash
python3 --version
```

若版本過新，建議使用虛擬環境管理工具（如 `pyenv` 或 Conda）降級至支援的版本。

### 快速環境設定（macOS / Homebrew）

若你尚未安裝 Python 3.12，可透過 Homebrew 安裝：

```bash
brew install python@3.12
```

安裝完成後，建立虛擬環境並啟動：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

升級 pip、setuptools 與 wheel（確保安裝工具為最新）：

```bash
pip install --upgrade pip setuptools wheel
```

最後安裝專案依賴：

```bash
pip install -r requirements.txt
```

完成後，你可以直接執行專案指令（見下方 **main.py 指令範例**）。

> **重要提醒**：安裝完成後，每次執行專案指令前務必先啟動虛擬環境：`source .venv/bin/activate`。若未啟動虛擬環境而直接執行 `python3 main.py ...`，可能會因為依賴缺失而出錯。

## 檔案說明（各 `.py` 的用途）

- `main.py`: 專案的簡易 CLI 入口，提供子命令 `download`, `update`, `recommend`, `example`，用來分別執行資料下載、更新、報表產生與示範腳本。
- `init.py`: 資料下載器（較像一次性腳本）。對 twstock.codes 中的上市股票/ETF，使用 vectorbt.YFData.download 以 5 分鐘間隔下載近 N 天（預設 59 天）之資料並存成 ./data/{code}.csv。
- `update.py`: CSV 更新器。對每檔股票嘗試從上次紀錄時間開始下載新增的 5 分鐘資料（會清理格式有問題的 CSV 行並 append 新資料），並在每次下載後暫停以避免 rate limit。包含錯誤處理與日誌輸出。
- `recommend.py`: 推薦 / 報表產生器。讀取股票 CSV（來自 nlp2.get_files_from_dir("data")），標準化欄位（open/high/low/close/volume），呼叫 strategy.grid.trade 得到買賣訊號與績效，判斷近期是否應買/賣並彙整成一張 HTML 報表（用 Jinja2 模板 stock_report_template.html），最後寫出 stock_report.html。
- `example.py`: 範例/演示腳本。讀取遠端 CSV（示例為 4967.csv），用 fta 計算技術指標，呼叫 strategy.just_keep_buying_with_technicals.trade 產生交易訊號，然後用 vectorbt.Portfolio.from_signals 建立投資組合並列印/繪圖結果。
- `strategy/grid.py`: 策略模組 — RSI + 布林帶格局策略。自行計算 RSI、EMA、20 日均、上下布林帶；當 RSI 過低且跌破下帶時買入，當 RSI 過高且漲破上帶時賣出。回傳買/賣索引、entry/exit 布林、總獲利與投資報酬率。
- `strategy/dynamic_delay.py`: 策略模組 — 延遲切換型（state-based）交易模擬。以交替買/賣狀態運作，只有當價格變動滿足「延遲次數（delay）」後才執行買/賣。回傳交易事件與績效。
- `strategy/just_keep_buying_with_technicals.py`: 策略模組 — 持續定期買入（帶技術指標過濾）。需要資料中已含 adx,rsi,atr 等指標（或先前用 fta 計算），依 ADX/RSI/ATR 判斷趨勢、動量與波動並在固定間隔投入資金；回傳買賣事件與績效。

另外還有文件 `STRATEGY_INTERFACE.md`，列出各策略函式的輸入欄位需求與回傳格式，方便整合與呼叫。

## main.py 指令範例（實際可使用的指令）

以下範例假設你在專案根目錄（有 `main.py` 的目錄）執行命令。若使用 virtualenv，先啟動你的環境並安裝依賴。

### 快速執行：一鍵更新與報表產生

若要一次性執行「更新資料 → 產生報表」（推薦用法），直接執行：

```bash
./run.sh
```

此腳本會自動：
1. 檢查虛擬環境是否存在
2. 啟動虛擬環境
3. 執行 `update` 下載最新資料
4. 執行 `recommend` 產生推薦報表至 `stock_report.html`

若需完整重新下載所有股票資料，編輯 `run.sh` 並取消註解 `download` 區塊。

### 各別執行指令

- 下載所有股票資料（可能耗時很久，請斟酌使用）：

```bash
source .venv/bin/activate
python3 main.py download
```

- 更新資料（只下載自上次記錄後的新資料）：

```bash
source .venv/bin/activate
python3 main.py update
```

- 產生推薦報表（會掃描 `data/` 下的 CSV，輸出 `stock_report.html`）：

```bash
source .venv/bin/activate
python3 main.py recommend
```

- 執行示範腳本（示範如何計算技術指標並做回測）：

```bash
source .venv/bin/activate
python3 main.py example
```

### Web 前端界面（Flask）

若不想在終端執行指令，可使用 Flask web 前端查看報表並觸發更新：

```bash
source .venv/bin/activate
python3 webapp.py
```

啟動後，在瀏覽器開啟：

```
http://localhost:5000
```

前端功能：
- **即時顯示最新報表**：首次開啟時直接展示 `stock_report.html`
- **更新按鈕**：按下「📊 更新」後會在背景執行 `run.sh`（更新資料 → 產生報表）
- **即時日誌**：更新期間會顯示執行日誌，完成後自動重新載入報表

#### GitHub Pages vs Flask 方式比較

| 項目 | GitHub Pages（線上靜態版） | Flask（本機動態版） |
|------|---------------------------|-----------------|
| 訪問方式 | https://voidful.github.io/tw_stocker/stock_report.html | http://localhost:5000（本機） |
| 部署位置 | GitHub 線上 | 本地/內網伺服器 |
| 更新方式 | 需手動 push 或 CI/CD 自動化 | 點擊網頁按鈕立即更新 |
| 互動性 | 無（純靜態 HTML） | 有（按鈕、日誌、自動重載） |
| 適用場景 | 公開分享、定期自動更新 | 個人開發、隨時查看測試 |

**建議用法**
- **日常開發測試**：使用 Flask 方式，方便快速迭代與檢視結果
- **對外分享報表**：定期將最新的 `stock_report.html` push 到 GitHub Pages，供他人查閱

小提示：
- 若要在背景執行（Linux / macOS），可以使用 `nohup` 或 `&`：

```bash
# 背景執行，並把輸出寫入 log
nohup python3 main.py update > update.log 2>&1 &
```

- 若遇到套件缺失或匯入錯誤，先確認安裝：

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

> **安全提醒**：Flask 前端提供了執行 `run.sh` 的功能。請不要直接在公開網路暴露此服務，除非加入認證防護（例如反向代理、IP 限制等）。

## 使用方式，以2330為例，可以換成自己需要的股票

```python
import pandas as pd

url="https://raw.githubusercontent.com/voidful/tw_stocker/main/data/2330.csv"
pd.read_csv(url)
```

## 資料來源

Yahoo finance，每隔5分鐘的六十天內資料，會用github action持續更新。


## 抽取技術指標
1. `pip install fta`
2. 
```python
import pandas as pd
import fta
url = "https://raw.githubusercontent.com/voidful/tw_stocker/main/data/2330.csv"
df = pd.read_csv(url, index_col='Datetime')

ta = fta.TA_Features()
df_full = ta.get_all_indicators(df)
print(df_full)
```

## 模擬交易
參考`strategy/dynamic_delay`作為我們交易的策略  
```python
import pandas as pd
import fta
from strategy.dynamic_delay import trade

url = "https://raw.githubusercontent.com/voidful/tw_stocker/main/data/2330.csv"
df = pd.read_csv(url, index_col='Datetime')


ta = fta.TA_Features()
df_full = ta.get_all_indicators(df)

PARAMETER = {
    "delay": 15,
    "initial_money": 10000,
    "max_buy": 10,
    "max_sell": 10,
}

states_buy, states_sell, states_entry, states_exit, total_gains, invest = trade(df_full, **PARAMETER)
```
#### 結果
![image](./img/trade_record.png)

### 交易圖表
```python
from matplotlib import pyplot as plt
import pandas as pd
import fta
from strategy.dynamic_delay import trade

url = "https://raw.githubusercontent.com/voidful/tw_stocker/main/data/2330.csv"
df = pd.read_csv(url, index_col='Datetime')


ta = fta.TA_Features()
df_full = ta.get_all_indicators(df)

PARAMETER = {
    "delay": 15,
    "initial_money": 10000,
    "max_buy": 10,
    "max_sell": 10,
}

states_buy, states_sell, states_entry, states_exit, total_gains, invest = trade(df_full, **PARAMETER)

close = df_full['close']
fig = plt.figure(figsize = (15,5))
plt.plot(close, color='r', lw=2.)
plt.plot(close, '^', markersize=10, color='m', label = 'buying signal', markevery = states_buy)
plt.plot(close, 'v', markersize=10, color='k', label = 'selling signal', markevery = states_sell)
plt.legend()
plt.show()
```
#### 結果
![image](./img/trade_graph.png)

### 回測
```python
import vectorbt as vbt
import pandas as pd
import numpy as np
import fta
from strategy.dynamic_delay import trade

url = "https://raw.githubusercontent.com/voidful/tw_stocker/main/data/2330.csv"
df = pd.read_csv(url, index_col='Datetime')


ta = fta.TA_Features()
df_full = ta.get_all_indicators(df)

PARAMETER = {
    "delay": 15,
    "initial_money": 10000,
    "max_buy": 10,
    "max_sell": 10,
}

states_buy, states_sell, states_entry, states_exit, total_gains, invest = trade(df_full, **PARAMETER)

fees = 0 # 假設交易費用為 0
portfolio_kwargs = dict(size=np.inf, fees=float(fees), freq='5m')
portfolio = vbt.Portfolio.from_signals(df_full['close'], states_entry, states_exit, **portfolio_kwargs)
print(portfolio.stats())
portfolio.plot().show()
```


## 重要改動說明

對專案進行了以下改進，增強穩定性與可維護性：

### 1. **模組化主程式入口**
- 所有主要腳本（`init.py`, `update.py`, `recommend.py`, `example.py`）已改為標準的 `if __name__ == '__main__'` 結構，避免匯入時產生副作用。
- 核心邏輯已封裝成 `main()` 函式，方便被其他程式引用或測試。

### 2. **統一 CLI 介面（main.py）**
- 新增 `main.py` 作為主要入口，提供四個子命令：`download`, `update`, `recommend`, `example`。
- 使用 `argparse` 標準化指令處理，易於未來擴展（例如加參數、日誌輸出等）。

### 3. **日誌系統與錯誤處理**
- 所有腳本已統一使用 `logging` 模組，取代直接 `print()`，便於控制日誌輸出級別與格式。
- `update.py` 增強了 CSV 清理與日期轉換的健壯性（避免時區混亂）。
- `recommend.py` 改善了對空訊號列表的處理，防止 IndexError 異常。

### 4. **策略介面文件**
- 新增 `STRATEGY_INTERFACE.md`，詳細列舉三個策略模組的輸入欄位需求與回傳格式。
- 幫助開發者快速理解如何將策略當作獨立 library 使用。

### 5. **代碼品質**
- 所有主程式現已遵循 Python 最佳實踐（模組層級無副作用）。
- 增加了錯誤日誌（從 `print()` → `logging`），便於除錯與追蹤。


報表將輸出至 `stock_report.html`，可用瀏覽器開啟查看。

- 直接在 macOS 用預設瀏覽器開啟：
````
open stock_report.html
````

https://voidful.github.io/tw_stocker/stock_report.html

