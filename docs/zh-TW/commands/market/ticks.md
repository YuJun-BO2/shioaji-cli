# market ticks

## 功能定位

這是一個市場明細查詢命令：**取得歷史逐筆撮合明細 (Ticks)**。
相較於 `kbars` 把某一分鐘內的所有成交壓扁成一個 OHLC 數據點，`ticks` 會把那一天、那一秒鐘發生的「每一筆」真實買賣明細忠實還原給你。非常適合微觀結構分析或高頻策略回測。

## 適用情境

- 復盤今天的暴跌/暴漲瞬間，看是大單砸盤還是散戶螞蟻搬象。
- 高頻交易策略尋找最佳進出場 tick 級特徵。
- 繪製 Tick 級別的光滑價格曲線與量價分佈圖 (Volume Profile)。

## 命令語法

```powershell
python scripts/shioaji_cli.py market ticks --code <代碼> --date <日期> [其他篩選參數...]
```

## 參數詳解

| 參數 | 必填 | 預設值 | 說明 |
|---|---|---|---|
| `--code` | **是** | 無 | 目標商品代碼（如 `2330`, `TXFR1`）。 |
| `--market` | 否 | `auto` | 輔助定位的市場類別。 |
| `--date` | **是** | 無 | 指定查詢的**單一交易日**，格式 `YYYY-MM-DD`。注意，不像 `kbars` 能查區間，ticks **只能查一天**！ |
| `--start-time` | 否 | 無 | 縮小範圍段的起點。格式如 `09:00:00` 或 `09:00:00.000000`。 |
| `--end-time`   | 否 | 無 | 縮小範圍段的終點。與 `--start-time` 必須成對出現。 |
| `--last-count` | 否 | 無 | 若只想抓那一天**最後 N 筆**的成交紀錄。不要跟 start/end 同時混用。 |

---

## 核心回傳資料結構 (`Ticks` 物件)

回傳結果與 `kbars` 一樣，這是一個陣列化的字典 (Columnar dictionary)，旨在將極端大量的 Tick 資料盡可能壓縮陣列大小。

| 欄位名稱 | 型別 | 說明與實務應用 |
|:-------|:----|:-----------|
| `ts`   | `list[int]` | 每一筆成交發生的 Unix Timestamp (奈秒級)。**注意，兩筆 tick 哪怕 ts 相同，也是各自獨立的撮合事件。** |
| `close`| `list[float]`| 該筆成交的撮合價格。 |
| `volume`|`list[int]` | 該筆撮合的成交口數/張數。如果數字異常巨大即為大戶單。 |
| `bid_price`/`ask_price`| `list[float]` | 發生該筆成交「瞬間」，市場上最佳的一檔買價與賣價。 |
| `tick_type` | `list[int]` | 此筆成交的內外盤屬性。例如 `1`: 買進 (外盤成交) / `2`: 賣出 (內盤成交)。通常用來估算買賣氣勢。 |

## 實戰與進階範例

### 1. 抓取完整一天的逐筆明細
如果標的是熱門股 (如台積電) 或台指期，一天可以產生數萬筆甚至數十萬筆 Ticks。
```powershell
python scripts/shioaji_cli.py market ticks --code 2330 --date 2024-03-20
```

### 2. 針對盤中急殺時段的高解析回查
若只對 09:00 到 09:05 的激烈多空交戰有興趣：
```powershell
python scripts/shioaji_cli.py market ticks --code TXFR1 --market futures --date 2024-03-20 --start-time 09:00:00 --end-time 09:05:00
```

### 3. 取出今日收盤前的最後百筆撮合
確認尾盤的造市狀況或最後的大單敲進方向：
```powershell
python scripts/shioaji_cli.py market ticks --code 2330 --date 2024-03-20 --last-count 100
```

## 注意事項與雷區

1. **資料量暴衝 (OOM 風險)**: `ticks` 回傳的量極為龐大，特別是台指期 (`TXFR1`) 單日可能高達 20MB~50MB 以陣列輸出到終端機。如果你的 CLI 是被其他腳本透過 stdout pipe 呼叫，請確保緩衝區 (buffer) 足夠大，否則可能卡死。
2. **與 websocket ticks 的差異**: `market ticks` 是拉取「過去已發生」的歷史資料；而 `quote subscribe` 則是訂閱「未來即將發生」的即時串流。不要一直寫 while 迴圈去 call 這個指令當作串流行情用。
3. **沒有當日跨盤查詢**: `ticks` 只允許查詢你指定的「那天」。如果你要查台指期包含夜盤 (昨天 15:00 ~ 今日 05:00) 的資料，你需要正確解讀 T+1 的盤後交易日切分規則。
