# accounts positions

## 功能定位

查詢**未平倉庫存部位 (Open Positions)** 與其**未實現損益**。
這是一個跨帳戶類型的關鍵命令。無論是台股現貨的持股，還是期貨與選擇權的留倉部位，只要目前還有數量未完全結清，都可以透過這個命令查出平均成本與即時的帳面賺賠。

## 適用情境

- 盤中/盤前檢視手中持股與期權部位現況。
- 查詢未平倉部位的累計浮動損益 (`pnl`)。
- 若部分持股是融資/融券買進，或是零股買進，可用於確認庫存狀態的分類（透過 `cond` 欄位）。

## 命令語法

```powershell
python scripts/shioaji_cli.py accounts positions [參數...]
```

## 參數詳解

| 參數 | 必填 | 預設值 | 說明 |
|---|---|---|---|
| `--account-kind` | 否 | `any` | `stock`(僅查證券) / `futures`(僅查期貨) / `any`(自動偵測或預設帳戶)。若有多個帳戶，建議明確切換。 |
| `--account-id` | 否 | 無 | 若有同名憑證但分屬不同分公司的帳戶（如 0062402），請輸入該 7 碼 ID。 |

---

## 核心回傳資料結構 (`Position` 物件清單)

執行完畢後會回傳一個包含所有未平倉標的的陣列。依據不同的商品屬性，回傳的欄位有細微差異：

### 共通與重要欄位

| 欄位名稱      | 說明與實務應用                                                                                     |
|:------------|:-----------------------------------------------------------------------------------------------|
| `id`        | **部位識別碼**。如果你需要進一步查詢這檔股票你到底是分幾筆、什麼時候買進的，必須留下這個 `id` 去執行 `accounts position-detail`。 |
| `code`      | 標的代碼，例如 `"2330"` 或 `"TX00"`。                                                            |
| `direction` | 部位方向。`Action.Buy` 表示多單（看漲持股）；`Action.Sell` 表示空單（融券或期貨空單）。 |
| `quantity`  | 未平倉數量。台股預設為「張/股」，期貨預設為「口」。                                               |
| `price`     | **平均建倉成本**。這是你當初買進被扣總款項後除以數量的均價。                                         |
| `last_price`| 最新市價/成交價。                                                                                 |
| `pnl`       | **未實現損益 (Profit and Loss)**。基於 `last_price` - `price` 計算出的帳面賺賠金額。               |
| `cond`      | *(限證券)* 交易條件 (StockOrderCond)。例如 `Cash` (現股), `MarginTrading` (融資), `ShortSelling` (融券)。 |

---

## 實戰與進階範例

### 1. 查詢台股現貨庫存
如果你已經預設過帳戶，或是要明確指定查台股：
```powershell
python scripts/shioaji_cli.py accounts positions --account-kind stock
```

### 2. 查詢期貨與選擇權留倉部位
```powershell
python scripts/shioaji_cli.py accounts positions --account-kind futures
```

### 3. 查看部位的原始 JSON 結構
如果想要結合外部程式 (如 Node.js 或 Go) 處理損益計算，你可以加上 `--raw` 參數：
```powershell
python scripts/shioaji_cli.py --raw accounts positions 
```

## 注意事項與雷區

1. **已結清部位不會顯示**: 這個命令只列出「還有庫存」的部位。若你已經在今天將股票賣出出清，該檔商品就會從 `positions` 中消失。如果想查已結清的損益，請改用 `accounts settle-profitloss`。
2. **損益計算延遲**: `pnl` 與 `last_price` 是由主機或本地 API 根據接收到的最後一筆報價計算得出，在盤中劇烈波動時可能會有秒差。對於極短線或程式交易者，建議自行訂閱 `subscribe` 行情報價後與 `positions` 中的 `price` 自行計算即時損益。
3. **查明細的必要性**: 這是一個「彙整」過後的結果。如果你的 2330 是分 3 天買進共 5 張，這裡只會顯示一筆 `quantity=5`，用平均價呈現。要看單筆紀錄請利用這份清單拿到的 `id` 餵給 `position-detail`。

## 常見操作順序

1. 先確認目標帳號。
2. 執行查詢命令取得核心指標。
3. 需要追查時再查 detail 或 summary。

## 進階範例

```powershell
python scripts/shioaji_cli.py accounts positions --account-kind any
```

## 延伸閱讀

- [全域參數說明](../../global-options.md)
