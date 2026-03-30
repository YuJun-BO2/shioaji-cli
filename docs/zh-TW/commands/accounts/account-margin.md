# account-margin

## 功能定位

本命令專門用於查詢期貨/選擇權帳戶的核心「維持保證金」(Account Margin) 狀態與風險指標。它是期權交易者在盤前確認交易額度、盤中監控風險指標，以及盤後結算部位資金狀態的關鍵指引。

## 適用情境

- **盤中監控與風控**：監看帳戶之風險指標，避免低於特定成數而遭斷頭或代沖銷。
- **盤前額度評估**：下新單前確認帳戶內可用的新增保證金額度。
- **盤後保證金盤點**：對帳時檢視不同幣別下的保證金餘額與相關會計數字。

## 命令語法

```powershell
python shioaji_cli.py accounts account-margin [參數選項]
```

## 參數詳解

| 參數 | 必填 | 預設值 | 可選值 | 說明 |
|---|---|---|---|---|
| `--account-kind` | 否 | `futures` | `auto / any / stock / futures` | 帳戶種類。保證金查詢主要針對期權（futures），輸入其他類型將被忽略或報錯。 |
| `--account-id` | 否 | 當前預設帳戶 | 有效的帳號字串 | 目標帳號 ID。未指定時系統將自動選取預設的期貨帳號。 |
| `--currency` | 否 | `NTD` | `NTD / USD / JPY / EUR` 等 | 查詢的計價幣別，以支援多幣別帳戶查核。 |
| `--margin-type` | 否 | `1` | `1 / 2` | `1` 代表即時餘額結構；`2` 代表風險計算標準。 |

## 核心回傳資料結構

執行後將回傳 `AccountMargin` 結構的詳細物件。此物件結構豐富，常被轉為 DataFrame 呈現，其核心欄位包括：

- **currency**: 該保證金明細的對應幣別。
- **margin**: 當前需要的總保證金要求。
- **risk_indicator**: 風險指標百分比（例如高於 100% 屬安全水準，低於 25% 可能面臨斷頭）。
- **available_margin**: 備用可用保證金額度（用於交易新部位的扣款）。
- **equity**: 帳戶權益數（包含本金與未實現損益）。

## 實戰範例

**範例 1：查詢台幣預設即時保證金**

```powershell
python shioaji_cli.py accounts account-margin --account-kind futures --currency NTD --margin-type 1
```
*說明：查詢自己預設期貨帳號內的台幣 (NTD) 即時可用保證金與風險指標。出金或下單前通常會檢視此數字。*

**範例 2：查詢外幣風險保證金結構**

```powershell
python shioaji_cli.py accounts account-margin --account-kind futures --currency USD --margin-type 2
```
*說明：若有交易海外期貨，可查詢美元帳戶（USD）以風險導向（margin-type = 2）查看風控門檻。*

## 注意事項與雷區

1. **僅限期貨帳戶**：
   這個查詢命令是針對期貨選擇權（Futures）等帶有保證金制度的產品所設計的。查詢證券（Stock）帳戶將不會有實質意義，並可能拋出對應 API 例外或為空。
2. **多幣別查詢邏輯**：
   若是混合保證金或涉及外幣轉會，查詢 `NTD` 所顯示之總合可能未涵蓋你在 `USD` 下的原始餘額，須根據實際交易種類搭配 `--currency` 參數逐一檢視。
3. **風險指標解讀即時性**：
   獲取到的 `risk_indicator` 雖是來自券商主機的回報，但在極端波動行情下可能發生些許延遲，切勿將保證金壓得過緊。

## 延伸閱讀

- [帳務欄位詳細表](../../../references/account_info.md)
- [如何查詢部位列表](positions.md)
