# accounts margin

## 功能定位

查詢**期貨與選擇權 (Futures & Options)** 帳戶的保證金、權益數與風險指標 (Margin & Risk Indicator)。
這是操作衍生性金融商品前，確認資金水位、評估是否面臨追繳 (Margin Call) 或斷頭風險的核心命令。

## 適用情境

- 盤前確認期權帳戶的剩餘可用保證金 (`available_margin`) 是否足夠下新單。
- 盤中即時監控風險指標 (`risk_indicator`) 以評估留倉部位風險。
- 盤後確認當日整體權益數 (`equity`) 與保證金變化。

*(注意：此命令僅針對「期貨」帳戶；若要查詢「證券」交割帳戶的銀行餘額，請使用 `accounts balance`)*

## 命令語法

```powershell
python scripts/shioaji_cli.py accounts margin 
```

## 參數詳解

| 參數 | 必填 | 預設值 | 說明 |
|---|---|---|---|
| `--account-kind` | 否 | `futures` | 鎖定查詢的帳號類別。預設自動鎖定為期貨 (`futures`)。 |
| `--account-id` | 否 | 自動套用 | 如果你有多個期貨帳戶，可輸入此參數（指定帳戶 7 碼 ID）。未填則預設使用第一個匹配的期貨帳戶。 |

---

## 核心回傳資料結構

執行完畢後，會回傳代表期貨帳戶保證金與權益結構的 JSON 物件。重要欄位對照如下：

| 欄位名稱                 | 型別    | 說明與風險提示                                                                                       |
|:-----------------------|:-------|:-------------------------------------------------------------------------------------------------|
| `status`               | `str`  | API 抓取狀態，通常為 `Fetched` 表示成功。                                                             |
| **`equity`** / `equity_amount` | `float`| **權益數**。帳戶內包含所有現金與未平倉浮動損益的總價值。                                           |
| **`available_margin`** | `float`| **可用保證金**。你目前還剩多少錢可以用來建立「新倉」。下單前最關鍵的數字。                             |
| **`risk_indicator`**   | `float`| **風險指標 (%)**。正常情況應高於 100%。若此數值過低 (例如低於 25%)，且低於券商規定的維持率，會面臨直接被代為平倉斷頭的風險。 |
| `initial_margin`       | `float`| **原始保證金**。你目前持有的所有未平倉部位，按照規定需要的最低建倉保證金總額。                         |
| `maintenance_margin`   | `float`| **維持保證金**。部位存續需要的最低保證金水位。當權益數低於此數值，會收到 Margin Call (盤中追繳)。      |
| `margin_call`          | `float`| 追繳金額。若無須追繳則為 `0.0`。                                                                     |
| `today_balance`        | `float`| 本日帳戶餘額。                                                                                     |

*(備註：針對選擇權還有特有欄位如 `option_openbuy_market_value` 買方市值、`option_opensell_market_value` 賣方市值。)*

---

## 實戰與進階範例

### 1. 快速查詢預設期貨帳戶風險指標
```powershell
python scripts/shioaji_cli.py accounts margin
```
*預期你可以在終端機看到包含 `"risk_indicator": 999.0` (沒部位時通常顯示最大值) 等資訊。*

### 2. 指定特定的期貨帳戶查詢
```powershell
python scripts/shioaji_cli.py accounts margin --account-id 1234567
```

## 注意事項與雷區

1. **帳戶類別錯誤**: 底層對應 `api.margin()`。如果誤用 `--account-kind stock` 帶入證券帳號，API 將回傳錯誤或無效資料。
2. **模擬環境之差異**: 在 `--env-file .env` 為 `SIMULATION=true` 時，查詢到的會是模擬期貨帳號的保證金餘額（多半會自動配給一筆虛擬保證金）。測試策略時，請留意虛擬帳戶與真實帳戶風險指標的跳動幅度可能因報價遲延而略有不同。

## 常見操作順序

1. 先確認目標帳號。
2. 執行查詢命令取得核心指標。
3. 需要追查時再查 detail 或 summary。

## 進階範例

```powershell
python scripts/shioaji_cli.py accounts margin
```

## 延伸閱讀

- [全域參數說明](../../global-options.md)
