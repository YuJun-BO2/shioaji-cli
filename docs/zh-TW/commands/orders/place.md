# orders place

## 功能定位

這是一個核心的交易命令：**送出委託單 (Place Order)**。
將指定的證券、期權合約與交易條件打包成 Shioaji 的 `Order` 物件，並交由 API 送出至交易所。支援即時（阻擋式）與非阻塞（無等待）回傳。

## 適用情境

- 證券現股、融資融券下單。
- 零股 (零股盤中/盤後) 交易委託。
- 國內期貨與選擇權 (含日盤、夜盤) 市價或限價下單。
- 搭配自動化腳本或警示系統，達到條件後自動送單。

## 命令語法

```powershell
python scripts/shioaji_cli.py orders place --code <合約代碼> --action <Buy/Sell> [其他條件...]
```

## 參數詳解與實務陷阱

| 參數             | 必填 | 說明與常見陷阱 |
|:-----------------|:----:|:-----------------------------------------------------------------------------------|
| `--code`         | **是** | 合約代碼（例如證券的 `2330` 或期貨的 `TXFR1`）。會自動解析合約類別。 |
| `--action`       | **是** | `Buy` (買進) / `Sell` (賣出)。不分大小寫。 |
| `--price`        | 否 | 下單價位。支援純數字。若是**市價單**則此欄位往往被忽略（視交易所/商品規定），預設值 `0`。 |
| `--quantity`     | 否 | 數量。如果是現股預設為「張」，預設為 `1`。若是零股 (`--order-lot IntradayOdd` / `Common`) 則為「股」。|
| `--price-type`   | 否 | 價格條件。期貨常見 `LMT` (限價), `MKT` (市價，只支援 IOC/FOK); 證券常見 `LMT`。未填預設為 `LMT` (依底層實作而定)。 |
| `--order-type`   | 否 | 委託條件。期貨必帶: `ROD` / `IOC` / `FOK`；證券通常自帶預設 `ROD`。 |
| `--octype`       | *(期貨)* | 新倉/平倉指示 (`Auto` / `New` / `Cover` / `DayTrade`)。**期貨當沖** 必須指定 `DayTrade`。 |
| `--order-cond`   | *(證券)* | 證券交易條件。`Cash` (現股,預設) / `MarginTrading` (融資) / `ShortSelling` (融券)。 |
| `--order-lot`    | *(證券)* | 手數類型。`Common` (整股,預設) / `IntradayOdd` (盤中零股) / `Fixing` (盤後定價)。 |
| `--timeout`      | 否 | 從發送到確認收單的等待毫秒數。設定 `0` 代表「**非阻塞 (Non-blocking)**」，送出後會立即回傳本地 Trade 物件。 |

## 回傳與資料結構重點

若下單成功，底層呼叫的是 `api.place_order(contract, order)`，並回傳 `Trade` 物件！
（若為 `--timeout 0` 非同步模式，回傳的欄位可能不包含主機的流水號或全部資訊，需靠額外查詢指令補齊）

**核心回傳 JSON 結構 (`Trade`)**
- `contract`: 指向目標標的合約。
- `order`: 剛打包好的原生委託單屬性。可以檢查有沒有組錯(`action`, `price_type` 等)。
- **`status`**: （最重要！）
  - 阻擋模式下：如果成功應該會看到狀態被更新成 `PendingSubmit` 取號中，或直接 `Submitted`。
  - 非阻塞下 (`timeout=0`)：狀態將呈現最原始的初始階段。要在後續利用 `orders list` 來輪詢。

## 實戰與進階範例

### 1. 台股：整股現價買進
買進長榮 (2603) 1 張，限價 150 元：
```powershell
python scripts/shioaji_cli.py orders place --code 2603 --action Buy --price 150 --price-type LMT
```

### 2. 台指期貨：市價當沖 (非阻塞式極速下單)
使用 IOC 條件買進台指近月 1 口市價當沖：
*(注意：市價在期貨只能配 IOC 或 FOK；當沖需帶入 `--octype DayTrade`)*
```powershell
python scripts/shioaji_cli.py orders place --code TXFR1 --market futures --action Buy --price 0 --price-type MKT --order-type IOC --octype DayTrade --timeout 0
```

### 3. 台股：盤中零股交易
買進台積電 (2330) 100 股（注意單位），限價 750 元。**必須指定 `--order-lot IntradayOdd`**。
```powershell
python scripts/shioaji_cli.py orders place --code 2330 --action Buy --price 750 --quantity 100 --order-lot IntradayOdd
```

## 常見開發順序
1. 先利用 `auth check` 確保憑證沒問題。
2. 開發階段若不想真花錢，請確認 `auth check` 回傳 `simulation=True`（以模擬環境測試）。
3. 送出委託 `orders place`。
4. 立刻執行 `orders list` 查看委託回報 (`status.status`) 是否為已送出或是已成交。
