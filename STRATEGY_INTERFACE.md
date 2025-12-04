tw_stocker 策略介面說明

本檔案列出主要策略函式、預期的輸入欄位與回傳格式。

- strategy/grid.trade(real_movement, ...):
  - 輸入：DataFrame `real_movement`（必須包含 `close` 欄位）。函式會自動計算 `rsi`, `ema`, `ma20`, `upper_band`, `lower_band`。
  - 回傳：(states_buy, states_sell, states_entry, states_exit, total_gains, invest)
    - states_buy / states_sell：買賣發生的整數索引列表
    - states_entry / states_exit：布林值陣列/列表，表示每個時間點的入場/出場訊號
    - total_gains：最終獲利（或虧損）的數值
    - invest：相對於初始資本的百分比變化

- strategy/dynamic_delay.trade(real_movement, delay=5, ...):
  - 輸入：DataFrame `real_movement` 或公開 `.close` 屬性的物件（Series）。策略會交替買賣狀態，並等待 `delay` 次確認。
  - 回傳：格式同上。

- strategy/just_keep_buying_with_technicals.trade(real_movement, ...):
  - 輸入：DataFrame `real_movement` 應該已包含技術指標欄位 `adx`, `rsi`, `atr` 與 `close`（可用 `fta` 計算）。
  - 回傳：格式同上。

注意事項：
- 所有策略函式回傳的訊號與 `vectorbt.Portfolio.from_signals` 相容，使用 `states_entry` 與 `states_exit` 布林列表即可。
- 傳入策略前，請確保 DataFrame 欄位名稱為小寫（`close`, `open`, `high`, `low`, `volume`）。
