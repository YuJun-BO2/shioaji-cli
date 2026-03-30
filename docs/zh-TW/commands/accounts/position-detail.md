# position-detail

## 功能定位

本命令用於查詢「未平倉部位」的底層詳細記錄。當使用 `positions` 查出彙總持倉後，若需檢視組成該持倉的多筆分批建倉明細、成本差異與條件記錄時，可透過此命令追蹤。

## 適用情境

- **分批建倉紀錄檢核**：確認某檔股票/期權的多筆買進（或賣出）明細，包含不同時間點的成本。
- **融資融券擔保維持率**：檢視證券帳戶在融資、融券交易時更詳細的擔保品與保證金計算狀況。

## 命令語法

```powershell
python shioaji_cli.py accounts position-detail [參數選項]
```

## 參數詳解

| 參數 | 必填 | 預設值 | 可選值 | 說明 |
|---|---|---|---|---|
| `--detail-id` | 是 | 無 | `positions` 查得的 ID | 目標未平倉部位的對應 ID，這必須從主部位列表先查出。 |
| `--account-kind` | 否 | `any` | `auto / any / stock / futures` | 限定該帳戶種類。 |
| `--account-id` | 否 | 當前預設帳戶 | 有效的帳號字串 | 特定的帳號 ID。 |

## 核心回傳資料結構

執行後會回傳 `PositionDetail` 的清單，每個元素紀錄一筆構成未平倉總量的心臟交易，常見欄位涵蓋：

- **date**: 建倉/委託成交的原始日期。
- **code**: 商品合約代碼。
- **quantity**: 該筆明細殘餘的部位量。
- **price** / **last_price**: 建倉價格與當前最新市價。
- **pnl**: 單筆明細的當前未實現損益估計。
- **fee** / **tax**: 已產生的手續費或稅基。（依市場種類可能有所差異）
- **cond**: 交易條件（例如現股、融資、融券）。
- **margintrading_amt** / **collateral**: （證券專用）融資金額與擔保品現值等。

## 實戰範例

**範例 1：查詢某檔股票持倉的逐筆建倉明細**

1. 首先利用主查詢獲取 ID：
   ```powershell
   python shioaji_cli.py accounts positions
   ```
   (假設查出台積電持倉對應的 detail-id 為 1)

2. 帶入 ID 取得分批細節：
   ```powershell
   python shioaji_cli.py accounts position-detail --account-kind stock --detail-id 1
   ```

## 注意事項與雷區

1. **必須先查總部位**：
   此命令不接受直接輸入商品代碼，只能接收 `--detail-id`，也就是說這是一個第二層（Second-layer）的鑽取查詢指令。
2. **多幣別與券種混用**：
   對於證券交易，它能協助確認現股與融資券混雜的情況；對於期貨，通常會直接列出多空單對存的狀況。

## 延伸閱讀

- [帳務欄位詳細表](../../../references/account_info.md)
- [主部位查詢](positions.md)
