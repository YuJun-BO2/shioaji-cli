# quote subscribe

## 功能定位

即時行情訂閱命令。這是觸發並維持接收即時報價 (Streaming Quotes) 的核心操作。
透過此命令，CLI 會接管你的終端機並在指定的時間內 (`--duration`)，持續將行情的 Tick、BidAsk 或 Quote 事件轉為 JSON 物件並輸出到標準輸出 (stdout)。此設計極度適合外部策略程式 (例如 Node.js 或 Go) 透過 pipe / subprocess 呼叫並即時串流接收與分析行情。

## 適用情境

- 演算法交易、高頻交易短期監看報價。
- 自行串接資料庫，或將即時行情推送到自己寫的 WebSocket Server。
- 開盤期間針對特定標的監測買賣五檔 (`bidask`)。
- 零股盤中監看 (`--intraday-odd true`)。

## 命令語法

```powershell
python scripts/shioaji_cli.py quote subscribe --code <合約代碼> [其他參數]
```

## 參數詳解與實務陷阱

| 參數 | 必填 | 說明 |
|---|---|---|
| `--code` | **是** | 目標商品代碼 (如 `2330`, `TXFR1`)。 |
| `--market` | 否 | `auto`(預設) / `futures` / `options` / `stock` / `indexs`。 |
| `--quote-type`| 否 | **極度重要**，決定你收到什麼資料：<br/>1. `tick` (逐筆成交，預設)<br/>2. `bidask` (買賣五檔即時變動)<br/>3. `quote` (綜合報價) |
| `--version` | 否 | 格式版本 (`v0` / `v1` / `v2`)。1.0 以後通常預設使用 `v1`，不同 Version 對應到 LLMS 不同的事件與資料結構 (例如 `TickSTKv1`、`BidAskFOPv1`)。 |
| `--intraday-odd` | 否 | `true` 或 `false`(預設)。若要訂閱**零股**的即時盤中資料，必須顯式切成 true，零股的行情與整股通道不同。 |
| `--duration` | 否 | 訂閱並阻塞執行的秒數。預設 `30` 秒，時間到後 CLI 會自動解除訂閱並退出。如果設為超大值可用於長期常駐接收。 |
| `--auto-unsubscribe`|否 | `true`(預設) / `false`。離開前是否主動告訴 Server 解除訂閱。 |

## 回傳與資料結構與陷阱

當你啟動後，**每當市場有新事件，CLI 就會非同步印出一行 JSON** 到 stdout。其結構如下：

```json
{"topic": "MKT/id/TSE/2330", "quote": {"AmountSum": [...], "Close": [...], "Time": "09:00:23.123456"}}
```

**陷阱與注意事項：**
1. **阻塞輸出**: 原生的 `api.quote.subscribe` 是背景運行的，但 CLI 使用了 `while + sleep` 來阻止程式結束。所有的事件回呼都是由獨立的 thread 引發，如果外部應用程式來不及讀取 stdout，可能造成 buffer 堆積。
2. **連線上限**: Shioaji 伺服器對同時訂閱的商品數量有限制 (一般情況為數百檔)，如果你瘋狂訂閱整個市場，帳號會被懲罰性斷線甚至暫時鎖定。建議精準訂閱需要的合約。
3. **回傳格式**: `v0` 跟 `v1` 的 json 結構大不相同。`v1` 將很多欄位簡化並轉換為 Array 以降低封包大小，在設計你的解析器的時候務必確認目前使用的版本。

## 實戰範例

### 1. 訂閱台指期連續月 (逐筆成交 Tick) 60 秒
```powershell
python scripts/shioaji_cli.py quote subscribe --code TXFR1 --market futures --quote-type tick --version v1 --duration 60
```

### 2. 訂閱台積電買賣五檔 (BidAsk) 120 秒
```powershell
python scripts/shioaji_cli.py quote subscribe --code 2330 --market stock --quote-type bidask --version v1 --duration 120
```

### 3. 訂閱零股行情
```powershell
python scripts/shioaji_cli.py quote subscribe --code 2330 --market stock --intraday-odd true --duration 300
```
